"""Connect the formalizer, model selector, solvers, and GMAT verification (TJC-1.16).

This module is the single connected entry point for the complete scoped
rendezvous workflow, after the thin CW/GMAT vertical slice
(``scripts/run_cw_gmat_slice.py``) proved out the CW-to-GMAT path on its own:

1. ``RendezvousCase.readiness`` records whether the already-formalized
   structured case (the ``orbital-problem-formalizer`` skill's output,
   restated here as data rather than Markdown) is ``READY_TO_SOLVE``,
   ``NEEDS_CLARIFICATION``, or ``OUT_OF_SCOPE``. A non-``READY_TO_SOLVE``
   case short-circuits immediately: no model selection, no CW/two-body
   solve, and no GMAT execution are ever attempted for an ambiguous or
   out-of-scope request;
2. for a ready case, ``src/model_selector.py::select_model`` decides CW
   rendezvous, the bounded two-body fallback, UNSUPPORTED, or NEEDS MORE
   INFORMATION from the case's recorded assumptions;
3. a CW selection calls ``src/cw.py::solve_cw_rendezvous`` and then reuses
   ``scripts/run_cw_gmat_slice.py::run_cw_rendezvous_gmat_verification`` --
   the exact same solve/script-generation/execution/parsing/screenshot
   pipeline the vertical slice already hardened -- rather than
   duplicating it;
4. a bounded-two-body-fallback selection instead propagates with
   ``src/twobody.py::propagate_cartesian_state`` and still receives an
   independent GMAT verification, generated/parsed via the inertial-coast
   script support added to ``src/gmat_verify.py``
   (``generate_two_body_coast_script``/``parse_inertial_report``) -- the
   two-body path is never silently skipped past GMAT verification; and
5. UNSUPPORTED/NEEDS MORE INFORMATION selections return an explicit,
   clearly non-authoritative result with no physics or GMAT execution at
   all.

Every outcome is assembled into one
``src/verification_report.py::UnifiedVerificationReport`` (via
``assemble_verification_report``) carrying the specified facts,
assumptions, model-selection reasoning, exact tool inputs/outputs,
numeric tolerances, artifact paths, and the final trust statement that
distinguishes "the deterministic solver succeeded" from "GMAT
independently verified it" (see ``WorkflowResult.to_dict``).
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Sequence

import numpy as np

from .cw import CW_RENDEZVOUS_UNITS, solve_cw_rendezvous
from .gmat_verify import (
    check_gmat_available,
    compare_gmat_final_state,
    generate_two_body_coast_script,
    parse_inertial_report,
    run_gmat_script,
    validate_screenshot,
)
from .model_selector import ModelSelectionCase, ModelSelectionResult, select_model
from .twobody import propagate_cartesian_state
from .verification_report import UnifiedVerificationReport, assemble_verification_report

Readiness = Literal["READY_TO_SOLVE", "NEEDS_CLARIFICATION", "OUT_OF_SCOPE"]

# Two-body fallback tolerances mirror scripts/generate_benchmark_gmat_evidence.py's
# benchmark case (c): the same scoped point-mass coast GMAT already independently
# verifies at this tolerance scale.
TWO_BODY_DEFAULT_TOLERANCES = {"position_m": 1.0, "velocity_mps": 0.001}


@dataclass(frozen=True)
class RendezvousCase:
    """One already-formalized structured rendezvous request.

    This is the Python-side restatement of the ``orbital-problem-formalizer``
    skill's Markdown output (``.pi/skills/orbital-problem-formalizer/SKILL.md``):
    the skill itself is prompt-driven, not Python code, so this dataclass is
    the structured-case representation this module's deterministic workflow
    actually consumes. ``readiness``/``clarification_questions`` mirror that
    skill's ``### Readiness``/``### Clarification Questions`` sections;
    ``model_selection_case`` carries the already-reviewed assumption items
    ``src/model_selector.py::select_model`` requires.
    """

    case_id: str
    readiness: Readiness
    clarification_questions: tuple[str, ...] = ()
    out_of_scope_reason: str = ""

    # Populated only when readiness is READY_TO_SOLVE.
    model_selection_case: Optional[ModelSelectionCase] = None

    # CW-path physical inputs (used when select_model chooses "CW rendezvous").
    mu_m3_s2: Optional[float] = None
    reference_radius_m: Optional[float] = None
    initial_relative_state: Optional[Sequence[float]] = None
    final_relative_state: Optional[Sequence[float]] = None
    transfer_time_s: Optional[float] = None
    pos_tol_m: float = 1.0
    vel_tol_mps: float = 0.001
    dv_tol_mps: float = 0.001

    # Two-body fallback physical inputs (used when select_model chooses
    # "bounded two-body fallback"); mirror src/twobody.py's contract.
    inertial_cartesian_state: Optional[Sequence[float]] = None
    coast_duration_s: Optional[float] = None
    rk4_steps: int = 2000


@dataclass(frozen=True)
class WorkflowResult:
    """One connected-workflow outcome, always carrying its full evidence trail.

    ``verification_report`` is ``None`` only for ``NEEDS_CLARIFICATION``/
    ``OUT_OF_SCOPE``/``UNSUPPORTED``/``NEEDS MORE INFORMATION`` outcomes that
    never reach a GMAT verification step at all; every outcome that *does*
    attempt a deterministic solve carries one.
    """

    case_id: str
    readiness: Readiness
    outcome: str
    verified: bool
    verification_status: str
    clarification_questions: tuple[str, ...]
    model_selection: Optional[ModelSelectionResult]
    verification_report: Optional[UnifiedVerificationReport]
    artifacts: dict
    trust_statement: str

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "readiness": self.readiness,
            "outcome": self.outcome,
            "verified": self.verified,
            "verification_status": self.verification_status,
            "clarification_questions": list(self.clarification_questions),
            "model_selection": (
                {
                    "selection": self.model_selection.selection,
                    "qualified": self.model_selection.qualified,
                    "reasons": list(self.model_selection.reasons),
                    "assumptions": list(self.model_selection.assumptions),
                    "concerns": list(self.model_selection.concerns),
                    "deterministic_tool": self.model_selection.deterministic_tool,
                    "missing_items": list(self.model_selection.missing_items),
                }
                if self.model_selection is not None
                else None
            ),
            "unified_verification_report": self.artifacts.get("unified_verification_report"),
            "artifacts": {key: value for key, value in self.artifacts.items() if key != "unified_verification_report"},
            "trust_statement": self.trust_statement,
        }


def _clarification_result(case: RendezvousCase) -> WorkflowResult:
    """NEEDS_CLARIFICATION: stop before any physics/model-selection/GMAT step."""
    return WorkflowResult(
        case_id=case.case_id,
        readiness="NEEDS_CLARIFICATION",
        outcome="NEEDS_CLARIFICATION",
        verified=False,
        verification_status="NOT VERIFIED: NEEDS_CLARIFICATION",
        clarification_questions=case.clarification_questions,
        model_selection=None,
        verification_report=None,
        artifacts={},
        trust_statement=(
            "No deterministic solver or GMAT verification was attempted: the structured "
            "case is not yet READY TO SOLVE. Resolve the clarification question(s) above "
            "before any physics is run."
        ),
    )


def _out_of_scope_result(case: RendezvousCase) -> WorkflowResult:
    """OUT_OF_SCOPE: stop before any physics/model-selection/GMAT step."""
    return WorkflowResult(
        case_id=case.case_id,
        readiness="OUT_OF_SCOPE",
        outcome="OUT_OF_SCOPE",
        verified=False,
        verification_status=f"NOT VERIFIED: OUT_OF_SCOPE: {case.out_of_scope_reason}",
        clarification_questions=(),
        model_selection=None,
        verification_report=None,
        artifacts={},
        trust_statement=(
            "No deterministic solver or GMAT verification was attempted: this request is "
            f"outside the supported two-spacecraft, circular-LEO, impulsive LVLH rendezvous "
            f"class ({case.out_of_scope_reason}). Restate it within the supported class or "
            "route it for human review."
        ),
    )


def _unresolved_selection_result(case: RendezvousCase, model_selection: ModelSelectionResult) -> WorkflowResult:
    """UNSUPPORTED / NEEDS MORE INFORMATION: no physics or GMAT execution."""
    return WorkflowResult(
        case_id=case.case_id,
        readiness="READY_TO_SOLVE",
        outcome=model_selection.selection,
        verified=False,
        verification_status=f"NOT VERIFIED: {model_selection.selection}",
        clarification_questions=(),
        model_selection=model_selection,
        verification_report=None,
        artifacts={},
        trust_statement=(
            "No deterministic solver or GMAT verification was attempted: model selection "
            f"returned '{model_selection.selection}', not a usable deterministic tool. "
            + " ".join(model_selection.reasons)
        ),
    )


def _run_cw_path(case: RendezvousCase, model_selection: ModelSelectionResult, output_dir: Path, gmat_executable: str) -> WorkflowResult:
    """CW rendezvous selection: solve, then reuse the hardened CW/GMAT slice pipeline."""
    import scripts.run_cw_gmat_slice as slice_runner  # local import: avoids a module-load-time dependency cycle

    n = math.sqrt(case.mu_m3_s2 / case.reference_radius_m**3)
    cw_case = {
        "case_id": case.case_id,
        "input_path": f"src.workflow.RendezvousCase(case_id={case.case_id!r})",
        "mu": case.mu_m3_s2,
        "radius_m": case.reference_radius_m,
        "state0": list(case.initial_relative_state),
        "target": list(case.final_relative_state) if case.final_relative_state is not None else [0.0] * 6,
        "transfer_s": case.transfer_time_s,
        "pos_tol": case.pos_tol_m,
        "vel_tol": case.vel_tol_mps,
        "dv_tol": case.dv_tol_mps,
    }
    result, returncode = slice_runner.run_cw_rendezvous_gmat_verification(
        cw_case, output_dir,
        gmat_executable=gmat_executable, gmat_gui_executable="GMAT-R2026a",
        skip_gui_screenshot=True, timeout_s=180.0,
    )
    verified = bool(result["verified"])
    report_dict = result["unified_verification_report"]
    artifacts = {
        "generated_script": str(output_dir / "generated_cw_rendezvous.script"),
        "trajectory_screenshot": result.get("trajectory_artifact"),
        "report_files": {
            key: str((output_dir / f"d_{key}.txt")) for key in ("init", "postburn1", "final", "trajectory")
        },
    }
    solver_name = report_dict["solver"]["name"]
    comparison_status = report_dict["comparison"]["status"]
    if verified:
        trust_statement = (
            f"The {solver_name} solver succeeded AND GMAT independently verified its "
            "candidate solution (comparison status PASS): this is a genuine, independently "
            "checked VERIFIED result, not merely a solver success."
        )
    else:
        trust_statement = (
            f"The {solver_name} solver {'succeeded' if report_dict['solver']['feasible'] else 'FAILED'} at "
            f"computing a candidate solution, but GMAT did NOT independently verify it "
            f"(failure_mode={result['failure_mode']!r}, comparison status {comparison_status!r}). "
            "A solver success alone is never reported as VERIFIED."
        )
    return WorkflowResult(
        case_id=case.case_id,
        readiness="READY_TO_SOLVE",
        outcome=result["failure_mode"] or "VERIFIED",
        verified=verified,
        verification_status=result["verification_status"],
        clarification_questions=(),
        model_selection=model_selection,
        verification_report=None,  # the dict form is already in artifacts/report_dict below
        artifacts={**artifacts, "unified_verification_report": report_dict},
        trust_statement=trust_statement,
    )


def _run_two_body_path(case: RendezvousCase, model_selection: ModelSelectionResult, output_dir: Path, gmat_executable: str) -> WorkflowResult:
    """Bounded two-body fallback selection: propagate, then still run GMAT verification.

    Mirrors ``scripts/generate_benchmark_gmat_evidence.py::run_two_body_case`` but
    returns a ``WorkflowResult``/``UnifiedVerificationReport`` instead of an ad hoc
    dict, and reuses the general ``generate_two_body_coast_script``/
    ``parse_inertial_report`` support added to ``src/gmat_verify.py`` rather than a
    benchmark-script-local inertial-report parser.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tolerances = dict(TWO_BODY_DEFAULT_TOLERANCES)
    run_id = f"{case.case_id}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"

    state0 = np.asarray(case.inertial_cartesian_state, dtype=float)
    final_state = propagate_cartesian_state(state0, case.mu_m3_s2, case.coast_duration_s, steps=case.rk4_steps)

    final_report_path = (output_dir / "d_final.txt").resolve()
    trajectory_report_path = (output_dir / "d_trajectory.txt").resolve()
    script_path = output_dir / "generated_two_body_coast.script"
    script_path.write_text(
        generate_two_body_coast_script(
            state0_si=state0, mu_m3_s2=case.mu_m3_s2, duration_s=case.coast_duration_s,
            final_report_path=final_report_path, trajectory_report_path=trajectory_report_path,
        )
    )

    screenshot_path = output_dir / "trajectory.svg"
    relative_states = np.array([[0.0, 0.0, 0.0], [final_state[0] - state0[0], final_state[1] - state0[1], 0.0]])
    _write_two_body_svg(screenshot_path, relative_states, case.case_id)
    screenshot = validate_screenshot(screenshot_path)

    def _finish(
        *, failure_mode, verified, verification_status, gmat_availability=None, gmat_run=None,
        gmat_final_state_si=None, comparison=None,
    ) -> WorkflowResult:
        report = assemble_verification_report(
            case_id=case.case_id, run_id=run_id,
            solver_name="point-mass-two-body-fixed-step-rk4-coast",
            solver_status="coast", solver_feasible=True,
            solver_reason="src.twobody.propagate_cartesian_state succeeded at propagating the declared inertial coast state.",
            gmat_availability=gmat_availability, gmat_run=gmat_run,
            cw_final_state_si=final_state, gmat_final_state_si=gmat_final_state_si, comparison=comparison,
            units=(("position", "m"), ("velocity", "m/s"), ("time", "s"), ("gravitational_parameter", "m^3/s^2")),
            tolerances=tolerances,
            screenshot_result=screenshot, screenshot_media_type="image/svg+xml",
            screenshot_caption=f"Two-body inertial coast displacement plot for case '{case.case_id}'.",
            failure_mode=failure_mode, verified=verified, verification_status=verification_status,
        )
        artifacts = {
            "generated_script": str(script_path),
            "trajectory_screenshot": str(screenshot_path) if screenshot.ok else None,
            "report_files": {"final": str(final_report_path), "trajectory": str(trajectory_report_path)},
        }
        if verified:
            trust_statement = (
                "The point-mass two-body RK4 coast solver succeeded AND GMAT independently "
                "verified its propagated state (comparison status PASS): a genuine, "
                "independently checked VERIFIED result."
            )
        else:
            trust_statement = (
                "The point-mass two-body RK4 coast solver succeeded at propagating the "
                f"declared state, but GMAT did NOT independently verify it "
                f"(failure_mode={failure_mode!r}). A solver success alone is never reported "
                "as VERIFIED."
            )
        return WorkflowResult(
            case_id=case.case_id, readiness="READY_TO_SOLVE", outcome=failure_mode or "VERIFIED",
            verified=verified, verification_status=verification_status, clarification_questions=(),
            model_selection=model_selection, verification_report=None,
            artifacts={**artifacts, "unified_verification_report": report.to_dict()},
            trust_statement=trust_statement,
        )

    availability = check_gmat_available(gmat_executable)
    if not availability.available:
        return _finish(
            failure_mode="MISSING_GMAT", verified=False,
            verification_status=f"NOT VERIFIED: MISSING_GMAT: {availability.reason}",
            gmat_availability=availability,
        )

    run = run_gmat_script(availability.executable, script_path, timeout_s=180.0)
    if not run.attempted or run.exit_status != 0:
        return _finish(
            failure_mode="EXECUTION_ERROR", verified=False,
            verification_status=f"NOT VERIFIED: EXECUTION_ERROR: {run.reason}",
            gmat_availability=availability, gmat_run=run,
        )

    final_parsed = parse_inertial_report(final_report_path, expect_single_row=True)
    if not final_parsed.ok:
        return _finish(
            failure_mode="MALFORMED_OUTPUT", verified=False,
            verification_status=f"NOT VERIFIED: MALFORMED_OUTPUT: {final_parsed.reason}",
            gmat_availability=availability, gmat_run=run,
        )
    gmat_final_state = final_parsed.states_si[0]

    if not screenshot.ok:
        return _finish(
            failure_mode="SCREENSHOT_FAILURE", verified=False,
            verification_status=f"NOT VERIFIED: SCREENSHOT_FAILURE: {screenshot.reason}",
            gmat_availability=availability, gmat_run=run, gmat_final_state_si=gmat_final_state,
        )

    comparison = compare_gmat_final_state(
        gmat_final_state, final_state, pos_tol_m=tolerances["position_m"], vel_tol_mps=tolerances["velocity_mps"],
    )
    if comparison.status != "PASS":
        return _finish(
            failure_mode="NUMERICAL_DISAGREEMENT", verified=False,
            verification_status=f"NOT VERIFIED: NUMERICAL_DISAGREEMENT ({comparison.status}): {comparison.reason}",
            gmat_availability=availability, gmat_run=run, gmat_final_state_si=gmat_final_state, comparison=comparison,
        )

    return _finish(
        failure_mode=None, verified=True, verification_status="VERIFIED",
        gmat_availability=availability, gmat_run=run, gmat_final_state_si=gmat_final_state, comparison=comparison,
    )


def _write_two_body_svg(path: Path, relative_states_si: np.ndarray, case_id: str) -> None:
    """Deterministic SVG plot for the two-body fallback, matching the CW slice's own writer."""
    xs = relative_states_si[:, 0]
    ys = relative_states_si[:, 1]
    margin, width, height = 30, 640, 400
    x_span = max(1.0, float(xs.max() - xs.min()))
    y_span = max(1.0, float(ys.max() - ys.min()))
    scale = min((width - 2 * margin) / x_span, (height - 2 * margin) / y_span)

    def p(x: float, y: float) -> tuple[float, float]:
        return (margin + (x - xs.min()) * scale, height - margin - (y - ys.min()) * scale)

    poly = " ".join(f"{px:.2f},{py:.2f}" for px, py in (p(x, y) for x, y in zip(xs, ys)))
    start, end = p(xs[0], ys[0]), p(xs[-1], ys[-1])
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="100%" height="100%" fill="white"/>'
        f'<text x="20" y="24" font-family="sans-serif" font-size="16">'
        f"Two-body inertial coast displacement (m) for case '{case_id}'</text>"
        f'<line x1="30" y1="370" x2="610" y2="370" stroke="#777"/>'
        f'<line x1="30" y1="30" x2="30" y2="370" stroke="#777"/>'
        f'<polyline fill="none" stroke="#1769aa" stroke-width="2" points="{poly}"/>'
        f'<circle cx="{start[0]:.2f}" cy="{start[1]:.2f}" r="4" fill="#d33"/>'
        f'<circle cx="{end[0]:.2f}" cy="{end[1]:.2f}" r="4" fill="#2a9d3f"/>'
        f"</svg>"
    )


def run_rendezvous_workflow(
    case: RendezvousCase,
    *,
    output_dir: Path,
    gmat_executable: str = "GmatConsole-R2026a",
) -> WorkflowResult:
    """Run the complete connected rendezvous workflow for one structured case.

    Readiness is checked first (AC2): a ``NEEDS_CLARIFICATION`` or
    ``OUT_OF_SCOPE`` case returns immediately, before ``select_model`` or any
    physics/GMAT call. A ``READY_TO_SOLVE`` case is passed to
    ``src/model_selector.py::select_model``; a CW selection reuses the
    hardened CW/GMAT vertical slice pipeline (AC1, AC3), a bounded
    two-body-fallback selection still receives independent GMAT verification
    (AC3), and an UNSUPPORTED/NEEDS MORE INFORMATION selection returns an
    explicit non-authoritative result with no physics or GMAT execution at
    all (AC4).
    """
    if case.readiness == "NEEDS_CLARIFICATION":
        return _clarification_result(case)
    if case.readiness == "OUT_OF_SCOPE":
        return _out_of_scope_result(case)
    if case.model_selection_case is None:
        raise ValueError("A READY_TO_SOLVE case must supply model_selection_case.")

    model_selection = select_model(case.model_selection_case)
    output_dir = Path(output_dir)

    if model_selection.selection == "CW rendezvous":
        return _run_cw_path(case, model_selection, output_dir, gmat_executable)
    if model_selection.selection == "bounded two-body fallback":
        return _run_two_body_path(case, model_selection, output_dir, gmat_executable)
    return _unresolved_selection_result(case, model_selection)
