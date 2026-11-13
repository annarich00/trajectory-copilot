"""Connect the formalizer, model selector, solvers, and GMAT verification (TJC-1.16).

This module is the single connected entry point for the complete scoped
rendezvous workflow, after the thin CW/GMAT vertical slice
(``scripts/run_cw_gmat_slice.py``) proved out the CW-to-GMAT path on its own:

1. ``RendezvousCase.readiness`` records whether the already-formalized
   structured case (the ``formalize_rendezvous_problem`` pi tool's output,
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
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal, Optional, Sequence

import numpy as np

from .cw import CW_RENDEZVOUS_UNITS, solve_cw_rendezvous
from .gmat_verify import (
    attempt_gmat_gui_screenshot,
    check_gmat_available,
    compare_gmat_final_state,
    generate_two_body_coast_script,
    generate_two_body_gui_preview_script,
    parse_inertial_report,
    run_gmat_script,
    validate_gui_screenshot,
    validate_screenshot,
)
from .model_selector import ModelSelectionCase, ModelSelectionResult, select_model
from .twobody import propagate_cartesian_state
from .workflow_visualization import (
    comparison_stage,
    scene_stage,
    trajectory_stage,
    two_body_comparison_stage,
    two_body_trajectory_stage,
)
from .verification_report import UnifiedVerificationReport, assemble_verification_report

Readiness = Literal["READY_TO_SOLVE", "NEEDS_CLARIFICATION", "OUT_OF_SCOPE"]

# Called with each visualization record (see src/workflow_visualization.py) the
# moment its pipeline stage produces it, so a caller can show it live.
ArtifactCallback = Callable[[dict], None]

# Two-body fallback tolerances mirror scripts/generate_benchmark_gmat_evidence.py's
# benchmark case (c): the same scoped point-mass coast GMAT already independently
# verifies at this tolerance scale.
TWO_BODY_DEFAULT_TOLERANCES = {"position_m": 1.0, "velocity_mps": 0.001}

# Repo root, used only to turn absolute artifact paths into the browser-relative
# paths the static demo site's server (site/server.js) actually serves under
# /artifacts/... -- the demo page cannot fetch an absolute filesystem path.
_REPO_ROOT = Path(__file__).resolve().parents[1]


def _relative_artifact_path(path) -> Optional[str]:
    """Return ``path`` relative to the repo root with forward slashes, or
    ``None`` if ``path`` is falsy. Falls back to the raw string for any path
    outside the repo root (should not happen for artifacts this module writes).
    """
    if not path:
        return None
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


@dataclass(frozen=True)
class RendezvousCase:
    """One already-formalized structured rendezvous request.

    This is the Python-side restatement of the ``formalize_rendezvous_problem``
    pi tool's Markdown output (``.pi/extensions/orbital-problem-formalizer-tool/``):
    that tool renders a validated specification rather than Python code, so this
    dataclass is the structured-case representation this module's deterministic workflow
    actually consumes. ``readiness``/``clarification_questions`` mirror that
    tool's ``### Readiness``/``### Clarification Questions`` sections;
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
    saved_run_path: Optional[str] = None

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


def build_cw_run_manifest(
    case_id: str, output_dir: Path, result: dict, visualization_artifacts: Optional[list] = None,
) -> tuple[dict, dict]:
    """Build the ``run_manifest.json``/``run_summary.json`` payloads for one
    completed CW/GMAT verification ``result`` dict (the same shape
    ``scripts/run_cw_gmat_slice.py::run_cw_rendezvous_gmat_verification``
    returns), and write both files into ``output_dir``.

    Shared by both callers of that reusable core -- ``_run_cw_path`` below
    (``src/workflow.py``'s own orchestration) and
    ``scripts/gmat_tool_bridge.py`` (the ``run_gmat_verification`` pi tool's
    Python half) -- so a run triggered through either path produces the
    identical saved-run contract the static demo site reads.

    Each visualization stage record (3D scene, trajectory/burns plot,
    comparison plot) is attached to its matching step as an ``artifact``/
    ``artifacts`` entry with a repo-root-relative path (not an absolute
    filesystem path), since the demo site's server only serves paths under
    ``site/`` and ``artifacts/`` -- an absolute path would 404 in the
    browser even though the file exists on disk.
    """
    output_dir = Path(output_dir)
    visualization_artifacts = visualization_artifacts or []
    verified = bool(result["verified"])
    trajectory_artifact = result.get("trajectory_artifact")

    def _media_type(path: Optional[str]) -> str:
        suffix = Path(path).suffix.lower() if path else ""
        return {
            ".png": "image/png", ".svg": "image/svg+xml", ".html": "text/html",
        }.get(suffix, "application/octet-stream")

    def _visualization_step(rec: dict) -> dict:
        name = rec.get("name", rec.get("stage", "visualization"))
        step = {"name": name, "status": rec.get("status"), "reason": rec.get("reason")}
        paths = [p for p in (rec.get("paths") or []) if p]
        artifacts = [
            {"name": f"{name}_{i}" if len(paths) > 1 else name, "path": _relative_artifact_path(p), "media_type": _media_type(p)}
            for i, p in enumerate(paths)
        ]
        if artifacts:
            step["artifacts" if len(artifacts) > 1 else "artifact"] = artifacts if len(artifacts) > 1 else artifacts[0]
        return step

    run_manifest = {
        "demo_id": case_id,
        "run_id": f"{case_id}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}",
        "case_id": case_id,
        "mode": "cw",
        "request": f"{case_id}",
        "outcome": result["failure_mode"] or "VERIFIED",
        "verified": verified,
        "verification_status": result["verification_status"],
        "steps": [
            {"name": "formalize_rendezvous_problem", "status": "completed"},
            {"name": "select_rendezvous_model", "status": "completed"},
        ] + [_visualization_step(rec) for rec in visualization_artifacts],
        "artifacts": [
            {"name": "generated_script", "path": _relative_artifact_path(output_dir / "generated_cw_rendezvous.script"), "media_type": "text/plain"},
            {"name": "gui_preview_script", "path": _relative_artifact_path(output_dir / "generated_cw_rendezvous_gui_preview.script"), "media_type": "text/plain"},
            {"name": "trajectory_screenshot", "path": _relative_artifact_path(trajectory_artifact), "media_type": _media_type(trajectory_artifact)},
        ],
        "not_generated": [
            {"name": rec.get("name", rec.get("stage", "visualization")), "reason": rec.get("reason")}
            for rec in visualization_artifacts if rec.get("status") == "not_generated"
        ],
    }
    run_summary = {
        **run_manifest,
        "artifact_paths": {
            "generated_script": _relative_artifact_path(output_dir / "generated_cw_rendezvous.script"),
            "gui_preview_script": _relative_artifact_path(output_dir / "generated_cw_rendezvous_gui_preview.script"),
            "trajectory_screenshot": _relative_artifact_path(trajectory_artifact),
            "report_files": {key: _relative_artifact_path(output_dir / f"d_{key}.txt") for key in ("init", "postburn1", "final", "trajectory")},
        },
    }
    (output_dir / "run_manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n")
    (output_dir / "run_summary.json").write_text(json.dumps(run_summary, indent=2) + "\n")
    return run_manifest, run_summary


def _run_cw_path(
    case: RendezvousCase, model_selection: ModelSelectionResult, output_dir: Path, gmat_executable: str,
    gmat_gui_executable: str, attempt_gui_screenshot: bool, on_artifact: Optional[ArtifactCallback] = None,
) -> WorkflowResult:
    """CW rendezvous selection: solve, then reuse the hardened CW/GMAT slice pipeline.

    Visualization artifacts are generated at their own stage boundaries (TJC-16.5):
    the 3D scene before the solve, the trajectory/burns plot as soon as the solve
    returns (before any GMAT script is generated or run), and the comparison plot
    after GMAT execution and parsing. Each is reported through ``on_artifact`` the
    moment it is produced.
    """
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
    visualization_artifacts: list = []

    def _emit(record: dict) -> None:
        visualization_artifacts.append(record)
        if on_artifact is not None:
            on_artifact(record)

    _emit(scene_stage(case.initial_relative_state, case.reference_radius_m, output_dir))
    solved: dict = {}

    def _on_solution(solution) -> None:
        solved["solution"] = solution
        _emit(trajectory_stage(solution, output_dir))

    result, returncode = slice_runner.run_cw_rendezvous_gmat_verification(
        cw_case, output_dir,
        gmat_executable=gmat_executable, gmat_gui_executable=gmat_gui_executable,
        skip_gui_screenshot=not attempt_gui_screenshot, timeout_s=180.0, on_solution=_on_solution,
    )
    verified = bool(result["verified"])
    report_dict = result["unified_verification_report"]
    comparison_record = comparison_stage(
        case_id=case.case_id, solution=solved.get("solution"),
        initial_relative_state=case.initial_relative_state,
        comparison_status=report_dict["comparison"]["status"],
        pos_tol_m=case.pos_tol_m, vel_tol_mps=case.vel_tol_mps,
        gmat_trajectory_report=output_dir / "d_trajectory.txt", output_dir=output_dir,
    )
    _emit(comparison_record)
    if comparison_record["status"] == "generated":
        report_dict["comparison_plot_path"] = comparison_record["paths"][1]
    if report_dict["solver"]["feasible"]:
        build_cw_run_manifest(case.case_id, output_dir, result, visualization_artifacts)
    artifacts = {
        "generated_script": str(output_dir / "generated_cw_rendezvous.script"),
        "trajectory_screenshot": result.get("trajectory_artifact"),
        "screenshot_source": result.get("screenshot_source"),
        "gui_screenshot_attempt": result.get("gui_screenshot_attempt"),
        "report_files": {
            key: str((output_dir / f"d_{key}.txt")) for key in ("init", "postburn1", "final", "trajectory")
        },
        "visualization_artifacts": visualization_artifacts,
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
        saved_run_path=str(output_dir / "run_summary.json"),
    )


def _run_two_body_path(
    case: RendezvousCase, model_selection: ModelSelectionResult, output_dir: Path, gmat_executable: str,
    gmat_gui_executable: str, attempt_gui_screenshot: bool, on_artifact: Optional[ArtifactCallback] = None,
) -> WorkflowResult:
    """Bounded two-body fallback selection: propagate, then still run GMAT verification.

    Mirrors ``scripts/generate_benchmark_gmat_evidence.py::run_two_body_case`` but
    returns a ``WorkflowResult``/``UnifiedVerificationReport`` instead of an ad hoc
    dict, and reuses the general ``generate_two_body_coast_script``/
    ``parse_inertial_report`` support added to ``src/gmat_verify.py`` rather than a
    benchmark-script-local inertial-report parser.

    ``attempt_gui_screenshot`` mirrors ``scripts/run_cw_gmat_slice.py``'s real
    GMAT GUI screenshot attempt (``attempt_gmat_gui_screenshot``) before
    falling back to the deterministic SVG plot (``_write_two_body_svg``); a
    failed/unavailable GUI attempt only changes which artifact is used
    (``screenshot_source``), never the overall ``verified``/``failure_mode``
    outcome.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # The three TJC-16 plots all need inputs this path does not have (a relative
    # state, burns, a solver state history), so each stage boundary records an
    # explicit ``not_generated`` entry with its reason instead of a plot.
    visualization_artifacts: list = []

    def _emit(record: dict) -> None:
        visualization_artifacts.append(record)
        if on_artifact is not None:
            on_artifact(record)

    _emit(scene_stage(None, None, output_dir))
    tolerances = dict(TWO_BODY_DEFAULT_TOLERANCES)
    run_id = f"{case.case_id}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"

    state0 = np.asarray(case.inertial_cartesian_state, dtype=float)
    final_state = propagate_cartesian_state(state0, case.mu_m3_s2, case.coast_duration_s, steps=case.rk4_steps)
    _emit(two_body_trajectory_stage())

    final_report_path = (output_dir / "d_final.txt").resolve()
    trajectory_report_path = (output_dir / "d_trajectory.txt").resolve()
    script_path = output_dir / "generated_two_body_coast.script"
    script_path.write_text(
        generate_two_body_coast_script(
            state0_si=state0, mu_m3_s2=case.mu_m3_s2, duration_s=case.coast_duration_s,
            final_report_path=final_report_path, trajectory_report_path=trajectory_report_path,
        )
    )

    # Attempt a real GMAT GUI (OrbitView/OpenFrames) screenshot before falling
    # back to the deterministic SVG plot (mirrors _run_cw_path's slice_runner
    # pipeline exactly). A failed/unavailable GUI attempt is never treated as
    # an overall verification failure -- it only changes screenshot_source.
    svg_screenshot_path = output_dir / "trajectory.svg"
    screenshot_source = "svg_fallback"
    gui_result = None
    screenshot_path = svg_screenshot_path
    if attempt_gui_screenshot:
        gui_preview_script_path = output_dir / "generated_two_body_coast_gui_preview.script"
        gui_preview_script_path.write_text(
            generate_two_body_gui_preview_script(
                state0_si=state0, mu_m3_s2=case.mu_m3_s2, duration_s=case.coast_duration_s,
            )
        )
        gui_png_path = output_dir / "trajectory_gmat_gui.png"
        gui_result = attempt_gmat_gui_screenshot(gmat_gui_executable, gui_preview_script_path, gui_png_path)
        if gui_result.captured:
            gui_screenshot = validate_gui_screenshot(gui_png_path)
            if gui_screenshot.ok:
                screenshot_path = gui_png_path
                screenshot_source = "gmat_gui"
    gui_screenshot_attempt = (
        {"attempted": gui_result.attempted, "captured": gui_result.captured, "reason": gui_result.reason}
        if gui_result is not None
        else None
    )

    relative_states = np.array([[0.0, 0.0, 0.0], [final_state[0] - state0[0], final_state[1] - state0[1], 0.0]])
    if screenshot_source == "svg_fallback":
        _write_two_body_svg(svg_screenshot_path, relative_states, case.case_id)
    screenshot = (
        validate_gui_screenshot(screenshot_path)
        if screenshot_source == "gmat_gui"
        else validate_screenshot(screenshot_path)
    )
    screenshot_media_type = "image/png" if screenshot_source == "gmat_gui" else "image/svg+xml"
    screenshot_caption = (
        f"GMAT GUI (OrbitView/OpenFrames) trajectory render for case '{case.case_id}'."
        if screenshot_source == "gmat_gui"
        else f"Two-body inertial coast displacement plot for case '{case.case_id}'."
    )

    def _finish(
        *, failure_mode, verified, verification_status, gmat_availability=None, gmat_run=None,
        gmat_final_state_si=None, comparison=None,
    ) -> WorkflowResult:
        _emit(two_body_comparison_stage())
        report = assemble_verification_report(
            case_id=case.case_id, run_id=run_id,
            solver_name="point-mass-two-body-fixed-step-rk4-coast",
            solver_status="coast", solver_feasible=True,
            solver_reason="src.twobody.propagate_cartesian_state succeeded at propagating the declared inertial coast state.",
            gmat_availability=gmat_availability, gmat_run=gmat_run,
            cw_final_state_si=final_state, gmat_final_state_si=gmat_final_state_si, comparison=comparison,
            units=(("position", "m"), ("velocity", "m/s"), ("time", "s"), ("gravitational_parameter", "m^3/s^2")),
            tolerances=tolerances,
            screenshot_result=screenshot, screenshot_media_type=screenshot_media_type,
            screenshot_caption=screenshot_caption,
            failure_mode=failure_mode, verified=verified, verification_status=verification_status,
        )
        artifacts = {
            "generated_script": str(script_path),
            "trajectory_screenshot": str(screenshot_path) if screenshot.ok else None,
            "screenshot_source": screenshot_source,
            "gui_screenshot_attempt": gui_screenshot_attempt,
            "report_files": {"final": str(final_report_path), "trajectory": str(trajectory_report_path)},
            "visualization_artifacts": visualization_artifacts,
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
    gmat_gui_executable: str = "GMAT-R2026a",
    attempt_gui_screenshot: bool = True,
    on_artifact: Optional[ArtifactCallback] = None,
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

    ``attempt_gui_screenshot`` (default ``True``) genuinely attempts a real
    GMAT GUI (OrbitView/OpenFrames) trajectory screenshot for both the CW and
    two-body paths before falling back to the deterministic SVG plot, using
    ``gmat_gui_executable`` (distinct from the console-mode
    ``gmat_executable`` used for numeric verification). Pass ``False`` to
    skip the GUI attempt entirely and go straight to the SVG fallback (e.g.
    in environments with no reachable display at all).

    Visualization artifacts (TJC-16.5) are generated at their own stage
    boundaries and recorded in ``artifacts["visualization_artifacts"]``, in
    pipeline order: the 3D relative-position scene after model selection and
    before the solve, the trajectory/burns plot after the solve and before
    GMAT, and the CW-vs-GMAT comparison plot after GMAT execution and parsing.
    ``on_artifact``, if given, is called with each record as it is produced.
    Stages without the inputs for a plot are recorded as ``not_generated``
    with a reason. The GMAT execution and screenshot handoff is unchanged.
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
        return _run_cw_path(case, model_selection, output_dir, gmat_executable, gmat_gui_executable, attempt_gui_screenshot, on_artifact)
    if model_selection.selection == "bounded two-body fallback":
        return _run_two_body_path(case, model_selection, output_dir, gmat_executable, gmat_gui_executable, attempt_gui_screenshot, on_artifact)
    return _unresolved_selection_result(case, model_selection)
