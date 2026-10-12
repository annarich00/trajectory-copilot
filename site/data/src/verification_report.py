"""Unified operator-facing verification report assembly (TJC-1.19).

``scripts/run_cw_gmat_slice.py`` already computes every piece this module
needs: a CW analytical solution (``src/cw.py``), GMAT availability/execution
evidence, a parsed/compared GMAT final state, and a validated screenshot
artifact (``src/gmat_verify.py``). Before this module, those pieces were
assembled into ``verification_result.json`` as an ad hoc dict, built up
field-by-field across several ``if`` branches in the runner script. This
module formalizes that assembly into one explicit, always-fully-populated
dataclass, so the numerical comparison, tolerances, units, GMAT run
identity, and screenshot artifact are guaranteed to travel together rather
than being scattered across whichever branch of the runner happened to run.

``assemble_verification_report`` is the single entry point. It does not run
GMAT, parse reports, or validate screenshots itself (that remains
``src/gmat_verify.py``'s job); it only accepts those already-computed
results and formats/validates them into one report. Critically, it
re-enforces (does not merely assume) the "never a false PASS" invariant
already implemented by ``src/gmat_verify.py``/``scripts/run_cw_gmat_slice.py``:
constructing a report with ``verified=True`` while GMAT was not attempted,
exited nonzero, produced no parsed final state, had a non-PASS comparison,
or has an invalid screenshot raises ``ValueError`` immediately, so a future
caller cannot silently thread a false PASS through this layer even by
mistake.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .gmat_verify import GMATAvailability, GMATComparisonResult, GMATRunResult, ScreenshotResult


@dataclass(frozen=True)
class ScreenshotArtifact:
    """A directly accessible screenshot/plot artifact reference (AC2).

    ``media_type`` is an explicit MIME type (``"image/svg+xml"`` for the
    deterministic SVG fallback plot, ``"image/png"`` for a real captured
    GMAT GUI render) rather than left to be inferred from a file extension.
    ``case_id``/``run_id`` give the case/run association so it is always
    clear which verification run this screenshot belongs to, even if the
    artifact file is later moved or viewed in isolation.
    """

    media_type: str
    path: str | None
    caption: str
    case_id: str
    run_id: str
    ok: bool
    reason: str


@dataclass(frozen=True)
class UnifiedVerificationReport:
    """One operator-facing verification contract (AC1 + AC2 fields together).

    Every field required by AC1 (GMAT version/run identity, compared
    states, units, tolerances, measured discrepancies, PASS/WARNING/FAIL/
    INCOMPLETE status) and AC2 (the ``screenshot`` artifact reference) is
    present unconditionally on every instance -- never only "whatever keys
    happen to be in a dict" for a given failure mode. Fields that cannot
    yet have a value for an earlier failure mode (e.g. no GMAT final state
    when GMAT never ran) are explicitly ``None``, not omitted.
    """

    case_id: str
    run_id: str

    # GMAT version/run identity.
    gmat_executable: str | None
    gmat_version_banner: str
    gmat_attempted: bool
    gmat_exit_status: int | None
    gmat_run_reason: str

    # The CW analytical solver's own outcome, kept explicitly distinct from
    # GMAT's independent verification outcome (AC4).
    solver_name: str
    solver_status: str
    solver_feasible: bool
    solver_reason: str

    # Compared states/trajectory quantities, units, tolerances, measured
    # discrepancies, and the PASS/WARNING/FAIL/INCOMPLETE comparison status.
    cw_final_state_m_mps: list[float] | None
    gmat_final_state_m_mps: list[float] | None
    units: tuple[tuple[str, str], ...]
    tolerances: dict[str, float]
    position_error_m: float | None
    velocity_error_mps: float | None
    comparison_status: str
    comparison_reason: str

    # The directly accessible screenshot artifact reference (AC2).
    screenshot: ScreenshotArtifact

    # Overall outcome. ``verified`` is only ever ``True`` when every
    # constructor-time invariant below held (AC3).
    failure_mode: str | None
    verified: bool
    verification_status: str

    def to_human_readable(self) -> str:
        """Render the AC4 operator-facing narrative.

        Distinguishes "the CW solver itself succeeded" (``solver_feasible``:
        a targetable boundary condition, independent of GMAT) from "GMAT
        independently verified it" (``comparison_status == 'PASS'`` *and*
        GMAT actually ran and produced parsed output), and explains likely
        discrepancy causes when the evidence supports it: a bounded
        tolerance overrun (``WARNING``) reads as likely numerical/
        integration precision, while a large-margin ``FAIL`` reads as a
        likely frame/unit/convention mismatch rather than mere imprecision.
        """
        lines: list[str] = []
        lines.append(f"Verification report for case '{self.case_id}' (run '{self.run_id}')")
        lines.append("")

        # 1. The CW/two-body solver's own outcome, independent of GMAT.
        if self.solver_feasible:
            lines.append(
                f"SOLVER: The {self.solver_name} solver SUCCEEDED at computing a candidate "
                f"solution (status='{self.solver_status}'). {self.solver_reason}"
            )
        else:
            lines.append(
                f"SOLVER: The {self.solver_name} solver FAILED to find a candidate solution "
                f"(status='{self.solver_status}'). {self.solver_reason} No GMAT independent "
                "verification was attempted for this case: there is no candidate to verify."
            )
        lines.append("")

        # 2. GMAT's independent verification outcome, kept explicitly distinct
        #    from "the solver succeeded" above (AC4's required distinction).
        if not self.gmat_attempted:
            lines.append(
                "INDEPENDENT VERIFICATION: NOT PERFORMED. GMAT was never launched "
                f"({self.gmat_run_reason}). A solver success above is NOT the same as an "
                "independent GMAT verification; this case has no GMAT verification evidence "
                "at all and must not be reported as verified."
            )
        elif self.gmat_exit_status != 0:
            lines.append(
                "INDEPENDENT VERIFICATION: NOT PERFORMED. GMAT was launched but did not exit "
                f"successfully ({self.gmat_run_reason}). No numerical comparison could be made."
            )
        elif self.gmat_final_state_m_mps is None:
            lines.append(
                "INDEPENDENT VERIFICATION: NOT PERFORMED. GMAT exited successfully but its "
                "reported output could not be parsed into a usable final state "
                f"({self.comparison_reason})."
            )
        elif self.comparison_status == "PASS":
            lines.append(
                "INDEPENDENT VERIFICATION: GMAT independently verified the candidate solution. "
                f"Position error {self.position_error_m:.3e} m and velocity error "
                f"{self.velocity_error_mps:.3e} m/s are both within tolerance "
                f"(position tolerance {self.tolerances.get('position_m')} m, velocity tolerance "
                f"{self.tolerances.get('velocity_mps')} m/s). A solver success alone does NOT by "
                "itself constitute this independent verification -- this GMAT comparison is what "
                "does."
            )
        elif self.position_error_m is None or self.velocity_error_mps is None:
            lines.append(
                "INDEPENDENT VERIFICATION: NOT PERFORMED. No GMAT-vs-CW numerical comparison was "
                f"made ({self.comparison_reason})."
            )
        else:
            lines.append(
                f"INDEPENDENT VERIFICATION: GMAT ran and produced a comparable final state, but "
                f"the comparison status is '{self.comparison_status}', not PASS. Position error "
                f"{self.position_error_m:.3e} m vs. tolerance {self.tolerances.get('position_m')} m; "
                f"velocity error {self.velocity_error_mps:.3e} m/s vs. tolerance "
                f"{self.tolerances.get('velocity_mps')} m/s. {self.comparison_reason}"
            )
            pos_tol = self.tolerances.get("position_m")
            vel_tol = self.tolerances.get("velocity_mps")
            if self.comparison_status == "WARNING" and pos_tol and vel_tol:
                lines.append(
                    "LIKELY CAUSE: the discrepancy is a bounded, small-margin tolerance overrun "
                    "(within the configured warning margin of tolerance), which is consistent "
                    "with ordinary numerical/integrator precision limits rather than a frame, "
                    "unit, or modeling error; it should still not be reported as verified."
                )
            elif self.comparison_status == "FAIL" and pos_tol and vel_tol:
                lines.append(
                    "LIKELY CAUSE: the discrepancy is far beyond the configured warning margin, "
                    "which is more consistent with a frame/unit/state-ordering mismatch or an "
                    "incorrect GMAT script mapping than with ordinary numerical precision; "
                    "re-check the CW-to-GMAT frame/unit mapping before re-running."
                )
        lines.append("")

        # 3. The screenshot artifact.
        if self.screenshot.ok:
            lines.append(
                f"SCREENSHOT: a valid {self.screenshot.media_type} trajectory artifact is "
                f"available at '{self.screenshot.path}' ({self.screenshot.caption})."
            )
        else:
            lines.append(f"SCREENSHOT: MISSING OR INVALID. {self.screenshot.reason}")
        lines.append("")

        # 4. Overall status.
        lines.append(f"OVERALL: {self.verification_status}")
        if not self.verified and self.failure_mode:
            lines.append(f"failure_mode: {self.failure_mode}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialize to the same plain-dict shape embedded in ``verification_result.json``."""
        return {
            "case_id": self.case_id,
            "run_id": self.run_id,
            "gmat": {
                "executable": self.gmat_executable,
                "version_banner": self.gmat_version_banner,
                "attempted": self.gmat_attempted,
                "exit_status": self.gmat_exit_status,
                "reason": self.gmat_run_reason,
            },
            "solver": {
                "name": self.solver_name,
                "status": self.solver_status,
                "feasible": self.solver_feasible,
                "reason": self.solver_reason,
            },
            "comparison": {
                "cw_final_state_m_mps": self.cw_final_state_m_mps,
                "gmat_final_state_m_mps": self.gmat_final_state_m_mps,
                "units": list(self.units),
                "tolerances": self.tolerances,
                "position_error_m": self.position_error_m,
                "velocity_error_mps": self.velocity_error_mps,
                "status": self.comparison_status,
                "reason": self.comparison_reason,
            },
            "screenshot": {
                "media_type": self.screenshot.media_type,
                "path": self.screenshot.path,
                "caption": self.screenshot.caption,
                "case_id": self.screenshot.case_id,
                "run_id": self.screenshot.run_id,
                "ok": self.screenshot.ok,
                "reason": self.screenshot.reason,
            },
            "failure_mode": self.failure_mode,
            "verified": self.verified,
            "verification_status": self.verification_status,
            "human_readable_report": self.to_human_readable(),
        }


def assemble_verification_report(
    *,
    case_id: str,
    run_id: str,
    solver_name: str,
    solver_status: str,
    solver_feasible: bool,
    solver_reason: str,
    gmat_availability: GMATAvailability | None,
    gmat_run: GMATRunResult | None,
    cw_final_state_si: np.ndarray | None,
    gmat_final_state_si: np.ndarray | None,
    comparison: GMATComparisonResult | None,
    units: tuple[tuple[str, str], ...],
    tolerances: dict[str, float],
    screenshot_result: ScreenshotResult,
    screenshot_media_type: str,
    screenshot_caption: str,
    failure_mode: str | None,
    verified: bool,
    verification_status: str,
) -> UnifiedVerificationReport:
    """Assemble one ``UnifiedVerificationReport`` from already-computed evidence.

    This is a pure formatting/validation layer: it does not run GMAT, parse
    reports, compare states, or validate screenshots -- those remain
    ``src/gmat_verify.py``'s job (see that module's docstring). Its own job
    is to (1) put every AC1/AC2 field in one explicit place, and (2)
    re-enforce AC3 as a hard invariant at construction time: it is a
    programming error, not merely a documentation convention, for a caller
    to request ``verified=True`` without GMAT having actually attempted and
    successfully exited, produced a parseable final state, compared PASS,
    and had a valid screenshot -- that combination raises ``ValueError``
    immediately rather than silently assembling a false-PASS report.
    """
    gmat_attempted = bool(gmat_run.attempted) if gmat_run is not None else False
    gmat_exit_status = gmat_run.exit_status if gmat_run is not None else None
    gmat_run_reason = gmat_run.reason if gmat_run is not None else (
        gmat_availability.reason if gmat_availability is not None else "GMAT was never invoked."
    )
    gmat_executable = gmat_availability.executable if gmat_availability is not None else None
    gmat_version_banner = gmat_availability.version_banner if gmat_availability is not None else ""

    comparison_status = comparison.status if comparison is not None else "INCOMPLETE"
    comparison_reason = (
        comparison.reason if comparison is not None else "No GMAT-vs-CW numerical comparison was performed."
    )
    position_error_m = comparison.position_error_m if comparison is not None else None
    velocity_error_mps = comparison.velocity_error_mps if comparison is not None else None

    screenshot = ScreenshotArtifact(
        media_type=screenshot_media_type,
        path=screenshot_result.path,
        caption=screenshot_caption,
        case_id=case_id,
        run_id=run_id,
        ok=screenshot_result.ok,
        reason=screenshot_result.reason,
    )

    # AC3 invariant, enforced here (not merely assumed from the caller's own
    # upstream logic): missing numerical output, failed GMAT execution, or a
    # missing/invalid screenshot can never be packaged as verified=True.
    if verified:
        problems: list[str] = []
        if not gmat_attempted:
            problems.append("GMAT was never attempted")
        if gmat_exit_status != 0:
            problems.append(f"GMAT exit_status is {gmat_exit_status!r}, not 0")
        if gmat_final_state_si is None:
            problems.append("no parsed GMAT final state is present")
        if comparison is None or comparison.status != "PASS":
            problems.append(f"comparison status is '{comparison_status}', not PASS")
        if not screenshot.ok:
            problems.append(f"screenshot artifact is invalid ({screenshot.reason})")
        if problems:
            raise ValueError(
                "Refusing to assemble a verified=True UnifiedVerificationReport: " + "; ".join(problems) + "."
            )

    return UnifiedVerificationReport(
        case_id=case_id,
        run_id=run_id,
        gmat_executable=gmat_executable,
        gmat_version_banner=gmat_version_banner,
        gmat_attempted=gmat_attempted,
        gmat_exit_status=gmat_exit_status,
        gmat_run_reason=gmat_run_reason,
        solver_name=solver_name,
        solver_status=solver_status,
        solver_feasible=solver_feasible,
        solver_reason=solver_reason,
        cw_final_state_m_mps=(cw_final_state_si.tolist() if cw_final_state_si is not None else None),
        gmat_final_state_m_mps=(gmat_final_state_si.tolist() if gmat_final_state_si is not None else None),
        units=units,
        tolerances=tolerances,
        position_error_m=position_error_m,
        velocity_error_mps=velocity_error_mps,
        comparison_status=comparison_status,
        comparison_reason=comparison_reason,
        screenshot=screenshot,
        failure_mode=failure_mode,
        verified=verified,
        verification_status=verification_status,
    )
