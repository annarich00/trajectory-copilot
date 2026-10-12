"""Tests for src/verification_report.py's report-assembly/formatting layer (TJC-1.19).

These tests target ``assemble_verification_report``/``UnifiedVerificationReport``
directly: the underlying GMAT execution/comparison/screenshot logic already has
its own dedicated tests in ``tests/test_cw_gmat_slice.py`` (TJC-1.21/TJC-2).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gmat_verify import GMATAvailability, GMATComparisonResult, GMATRunResult, ScreenshotResult  # noqa: E402
from src.verification_report import assemble_verification_report  # noqa: E402

UNITS = (("position", "m"), ("velocity", "m/s"))
TOLERANCES = {"position_m": 1.0, "velocity_mps": 0.001, "delta_v_mps": 0.001}


def _availability(ok=True) -> GMATAvailability:
    return GMATAvailability(ok, "/stand-in/gmat" if ok else None, "GMAT stand-in banner", "stand-in reason")


def _run(exit_status=0, attempted=True) -> GMATRunResult:
    return GMATRunResult(attempted, exit_status, "stdout", "", False, "GMAT exited successfully.")


def _good_screenshot() -> ScreenshotResult:
    return ScreenshotResult(True, "/tmp/trajectory.svg", "screenshot artifact is non-empty, well-formed SVG.")


def _bad_screenshot() -> ScreenshotResult:
    return ScreenshotResult(False, None, "screenshot artifact does not exist.")


def _assemble(**overrides):
    kwargs = dict(
        case_id="case-01",
        run_id="case-01-run-1",
        solver_name="clohessy-wiltshire",
        solver_status="unique",
        solver_feasible=True,
        solver_reason="Phi_rv is well-conditioned.",
        gmat_availability=_availability(),
        gmat_run=_run(),
        cw_final_state_si=np.zeros(6),
        gmat_final_state_si=np.full(6, 1e-6),
        comparison=GMATComparisonResult("PASS", 1e-6, 1e-9, 1.0, 0.001, 10.0, "within tolerance"),
        units=UNITS,
        tolerances=TOLERANCES,
        screenshot_result=_good_screenshot(),
        screenshot_media_type="image/svg+xml",
        screenshot_caption="caption",
        failure_mode=None,
        verified=True,
        verification_status="VERIFIED",
    )
    kwargs.update(overrides)
    return assemble_verification_report(**kwargs)


# --- AC1: all required fields are present together -------------------------


def test_report_includes_all_ac1_fields_together():
    report = _assemble()
    assert report.gmat_executable == "/stand-in/gmat"
    assert report.gmat_version_banner == "GMAT stand-in banner"
    assert report.gmat_attempted is True
    assert report.gmat_exit_status == 0
    assert report.cw_final_state_m_mps == [0.0] * 6
    assert report.gmat_final_state_m_mps == pytest.approx([1e-6] * 6)
    assert report.units == UNITS
    assert report.tolerances == TOLERANCES
    assert report.position_error_m == pytest.approx(1e-6)
    assert report.velocity_error_mps == pytest.approx(1e-9)
    assert report.comparison_status == "PASS"
    assert report.verified is True
    assert report.verification_status == "VERIFIED"
    assert report.failure_mode is None


# --- AC2: screenshot artifact reference -------------------------------------


def test_report_screenshot_artifact_has_media_type_path_caption_and_case_run_association():
    report = _assemble(screenshot_media_type="image/png", screenshot_caption="a real GMAT GUI render")
    s = report.screenshot
    assert s.media_type == "image/png"
    assert s.path == "/tmp/trajectory.svg"
    assert s.caption == "a real GMAT GUI render"
    assert s.case_id == "case-01"
    assert s.run_id == "case-01-run-1"
    assert s.ok is True


# --- AC5 outcome coverage: PASS / WARNING / FAIL / GMAT failures / screenshot --


def test_agreement_produces_pass():
    report = _assemble()
    assert report.comparison_status == "PASS"
    assert report.verified is True


def test_tolerance_warning_is_distinct_from_pass_and_fail():
    comparison = GMATComparisonResult("WARNING", 5.0, 0.0001, 1.0, 0.001, 10.0, "within warning margin")
    report = _assemble(
        comparison=comparison, failure_mode="NUMERICAL_DISAGREEMENT", verified=False,
        verification_status="NOT VERIFIED: NUMERICAL_DISAGREEMENT (WARNING): within warning margin",
    )
    assert report.comparison_status == "WARNING"
    assert report.verified is False
    assert report.failure_mode == "NUMERICAL_DISAGREEMENT"


def test_disagreement_produces_fail():
    comparison = GMATComparisonResult("FAIL", 500.0, 0.5, 1.0, 0.001, 10.0, "gross numerical disagreement")
    report = _assemble(
        comparison=comparison, failure_mode="NUMERICAL_DISAGREEMENT", verified=False,
        verification_status="NOT VERIFIED: NUMERICAL_DISAGREEMENT (FAIL): gross numerical disagreement",
    )
    assert report.comparison_status == "FAIL"
    assert report.verified is False


@pytest.mark.parametrize("failure_mode", ["MISSING_GMAT", "EXECUTION_ERROR", "MALFORMED_OUTPUT"])
def test_gmat_failure_modes_are_each_distinct_and_never_verified(failure_mode):
    if failure_mode == "MISSING_GMAT":
        availability, run, gmat_final = _availability(ok=False), None, None
    elif failure_mode == "EXECUTION_ERROR":
        availability, run, gmat_final = _availability(), _run(exit_status=1), None
    else:
        availability, run, gmat_final = _availability(), _run(exit_status=0), None

    report = _assemble(
        gmat_availability=availability, gmat_run=run, gmat_final_state_si=gmat_final,
        comparison=None, failure_mode=failure_mode, verified=False,
        verification_status=f"NOT VERIFIED: {failure_mode}: evidence",
    )
    assert report.failure_mode == failure_mode
    assert report.verified is False
    assert report.comparison_status == "INCOMPLETE"


def test_missing_screenshot_refuses_verified_true():
    with pytest.raises(ValueError, match="screenshot artifact is invalid"):
        _assemble(screenshot_result=_bad_screenshot())


def test_corrupt_screenshot_refuses_verified_true():
    corrupt = ScreenshotResult(False, "/tmp/trajectory.svg", "screenshot artifact is empty.")
    with pytest.raises(ValueError, match="screenshot artifact is invalid"):
        _assemble(screenshot_result=corrupt)


def test_missing_screenshot_in_a_not_verified_report_is_still_recorded():
    """A missing screenshot does not need to raise when the report is honestly
    not claiming to be verified (e.g. a MISSING_GMAT failure before any
    screenshot was generated)."""
    report = _assemble(
        screenshot_result=_bad_screenshot(), gmat_availability=_availability(ok=False), gmat_run=None,
        gmat_final_state_si=None, comparison=None, failure_mode="MISSING_GMAT", verified=False,
        verification_status="NOT VERIFIED: MISSING_GMAT: evidence",
    )
    assert report.screenshot.ok is False
    assert report.verified is False


# --- AC3: the invariant is enforced, not merely assumed ---------------------


def test_verified_true_without_gmat_attempted_raises():
    with pytest.raises(ValueError, match="GMAT was never attempted"):
        _assemble(gmat_availability=_availability(ok=False), gmat_run=None, gmat_final_state_si=None, comparison=None)


def test_verified_true_with_nonzero_exit_status_raises():
    with pytest.raises(ValueError, match="GMAT exit_status"):
        _assemble(gmat_run=_run(exit_status=1))


def test_verified_true_without_parsed_gmat_final_state_raises():
    with pytest.raises(ValueError, match="no parsed GMAT final state"):
        _assemble(gmat_final_state_si=None)


def test_verified_true_with_non_pass_comparison_raises():
    comparison = GMATComparisonResult("WARNING", 5.0, 0.0001, 1.0, 0.001, 10.0, "within warning margin")
    with pytest.raises(ValueError, match="comparison status is 'WARNING'"):
        _assemble(comparison=comparison)


def test_verified_true_without_comparison_raises():
    with pytest.raises(ValueError, match="comparison status is 'INCOMPLETE'"):
        _assemble(comparison=None)


def test_verified_true_with_invalid_screenshot_raises():
    with pytest.raises(ValueError, match="screenshot artifact is invalid"):
        _assemble(screenshot_result=_bad_screenshot())


# --- AC4: human-readable report distinguishes solver success from GMAT ------
# verification, and explains likely discrepancy causes.


def test_human_readable_report_distinguishes_solver_success_from_gmat_verification_on_pass():
    report = _assemble()
    text = report.to_human_readable()
    assert "SOLVER" in text and "SUCCEEDED" in text
    assert "INDEPENDENT VERIFICATION" in text
    assert "GMAT independently verified the candidate solution" in text
    assert "A solver success alone does NOT by itself constitute this independent verification" in text


def test_human_readable_report_distinguishes_solver_success_from_missing_gmat_verification():
    report = _assemble(
        gmat_availability=_availability(ok=False), gmat_run=None, gmat_final_state_si=None, comparison=None,
        failure_mode="MISSING_GMAT", verified=False, verification_status="NOT VERIFIED: MISSING_GMAT: evidence",
    )
    text = report.to_human_readable()
    assert "SOLVER" in text and "SUCCEEDED" in text
    assert "INDEPENDENT VERIFICATION: NOT PERFORMED" in text
    assert "is NOT the same as an independent GMAT verification" in text


def test_human_readable_report_explains_warning_as_likely_numerical_precision():
    comparison = GMATComparisonResult("WARNING", 5.0, 0.0001, 1.0, 0.001, 10.0, "within warning margin")
    report = _assemble(
        comparison=comparison, failure_mode="NUMERICAL_DISAGREEMENT", verified=False,
        verification_status="NOT VERIFIED: NUMERICAL_DISAGREEMENT (WARNING): within warning margin",
    )
    text = report.to_human_readable()
    assert "LIKELY CAUSE" in text
    assert "numerical/integrator precision" in text


def test_human_readable_report_explains_fail_as_likely_frame_or_unit_mismatch():
    comparison = GMATComparisonResult("FAIL", 500.0, 0.5, 1.0, 0.001, 10.0, "gross numerical disagreement")
    report = _assemble(
        comparison=comparison, failure_mode="NUMERICAL_DISAGREEMENT", verified=False,
        verification_status="NOT VERIFIED: NUMERICAL_DISAGREEMENT (FAIL): gross numerical disagreement",
    )
    text = report.to_human_readable()
    assert "LIKELY CAUSE" in text
    assert "frame/unit/state-ordering mismatch" in text


def test_human_readable_report_reports_missing_screenshot_distinctly():
    report = _assemble(
        screenshot_result=_bad_screenshot(), gmat_availability=_availability(ok=False), gmat_run=None,
        gmat_final_state_si=None, comparison=None, failure_mode="MISSING_GMAT", verified=False,
        verification_status="NOT VERIFIED: MISSING_GMAT: evidence",
    )
    text = report.to_human_readable()
    assert "SCREENSHOT: MISSING OR INVALID" in text


def test_to_dict_round_trips_json_serializable_fields():
    import json

    report = _assemble()
    serialized = json.dumps(report.to_dict())
    restored = json.loads(serialized)
    assert restored["verified"] is True
    assert restored["comparison"]["status"] == "PASS"
    assert restored["screenshot"]["ok"] is True
