import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.run_cw_gmat_slice as slice_runner  # noqa: E402
from src import gmat_verify  # noqa: E402


def _run(tmp_path, gmat="definitely-not-gmat", monkeypatch=None, argv_extra=None):
    import sys as _sys

    argv = ["run_cw_gmat_slice.py", "--output-dir", str(tmp_path), "--gmat", gmat]
    if argv_extra:
        argv += argv_extra
    if monkeypatch is not None:
        monkeypatch.setattr(_sys, "argv", argv)
        return slice_runner.main()
    completed = subprocess.run(
        [sys.executable, "scripts/run_cw_gmat_slice.py", "--output-dir", str(tmp_path), "--gmat", gmat],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    return completed.returncode


def _result(tmp_path):
    return json.loads((tmp_path / "verification_result.json").read_text())


def test_slice_reports_missing_gmat_without_false_verification(tmp_path):
    """(a) GMAT executable missing: script/screenshot are still generated as
    traceable evidence, but the result is never a false PASS."""
    returncode = _run(tmp_path, gmat="definitely-not-gmat")
    assert returncode == 1
    result = _result(tmp_path)
    assert result["verified"] is False
    assert result["failure_mode"] == "MISSING_GMAT"
    assert result["gmat"]["attempted"] is False
    assert result["trajectory_artifact_nonempty"] is True
    assert (tmp_path / "generated_cw_rendezvous.script").stat().st_size > 0
    assert result["cw"]["targeting_status"] == "unique"
    assert result["cw"]["total_delta_v_mps"] > 0
    assert result["comparison"]["tolerances"]["position_m"] == 1.0


def test_slice_reports_infeasible_structured_targeting_without_gmat_or_artifact(tmp_path, monkeypatch):
    """CW-targeting-infeasible remains its own, earlier failure mode: no
    GMAT script and no screenshot are produced for an unreachable boundary
    condition."""
    infeasible_solution = SimpleNamespace(
        status="singular-infeasible",
        feasible=False,
        reason="terminal position is unreachable",
        mean_motion_radps=0.001,
        transfer_time_s=100.0,
        condition_number=float("inf"),
        rank=1,
        reachability_residual_m=2.0,
    )
    monkeypatch.setattr(slice_runner, "solve_cw_rendezvous", lambda *args, **kwargs: infeasible_solution)
    assert _run(tmp_path, monkeypatch=monkeypatch) == 1
    result = _result(tmp_path)
    assert result["verified"] is False
    assert result["failure_mode"] == "CW_TARGETING_INFEASIBLE"
    assert result["cw"]["targeting_status"] == "singular-infeasible"
    assert "targeting infeasible" in result["verification_status"]
    assert result["gmat"]["attempted"] is False
    assert result["trajectory_artifact"] is None
    assert result["trajectory_artifact_nonempty"] is False
    assert not (tmp_path / "generated_cw_rendezvous.script").exists()


def test_slice_reports_execution_error_distinct_from_missing_gmat(tmp_path, monkeypatch):
    """(b) GMAT execution error: a found-but-failing executable is a
    distinct failure mode from MISSING_GMAT."""
    monkeypatch.setattr(
        slice_runner,
        "check_gmat_available",
        lambda executable, timeout_s=30.0: gmat_verify.GMATAvailability(
            True, "/stand-in/gmat", "GMAT stand-in", "stand-in available"
        ),
    )
    monkeypatch.setattr(
        slice_runner,
        "run_gmat_script",
        lambda executable, script_path, timeout_s=180.0: gmat_verify.GMATRunResult(
            True, 1, "", "simulated GMAT interpreter error", False, "GMAT exited with status 1."
        ),
    )
    assert _run(tmp_path, monkeypatch=monkeypatch) == 1
    result = _result(tmp_path)
    assert result["verified"] is False
    assert result["failure_mode"] == "EXECUTION_ERROR"
    assert result["gmat"]["attempted"] is True
    assert result["gmat"]["exit_status"] == 1
    assert (tmp_path / "generated_cw_rendezvous.script").stat().st_size > 0


def test_slice_reports_malformed_output_when_report_is_corrupt(tmp_path, monkeypatch):
    """(c) GMAT exits zero but the final-state ReportFile is malformed:
    distinguishable from EXECUTION_ERROR."""
    monkeypatch.setattr(
        slice_runner,
        "check_gmat_available",
        lambda executable, timeout_s=30.0: gmat_verify.GMATAvailability(
            True, "/stand-in/gmat", "GMAT stand-in", "stand-in available"
        ),
    )

    def fake_run(executable, script_path, timeout_s=180.0):
        # Simulate GMAT exiting 0 but corrupting its own final-state report.
        for key in ("init", "postburn1", "trajectory"):
            (tmp_path / f"d_{key}.txt").write_text("header line only, no data\n")
        (tmp_path / "d_final.txt").write_text("not,a,valid,gmat,report\n1 2 three 4 5 6 7\n")
        return gmat_verify.GMATRunResult(True, 0, "ok", "", False, "GMAT exited successfully.")

    monkeypatch.setattr(slice_runner, "run_gmat_script", fake_run)
    assert _run(tmp_path, monkeypatch=monkeypatch) == 1
    result = _result(tmp_path)
    assert result["verified"] is False
    assert result["failure_mode"] == "MALFORMED_OUTPUT"
    assert result["gmat"]["exit_status"] == 0


def test_slice_reports_numerical_disagreement_when_gmat_state_is_perturbed(tmp_path, monkeypatch):
    """(d) GMAT output parses cleanly but disagrees with the CW analytical
    final state beyond tolerance: distinguishable from MALFORMED_OUTPUT."""
    monkeypatch.setattr(
        slice_runner,
        "check_gmat_available",
        lambda executable, timeout_s=30.0: gmat_verify.GMATAvailability(
            True, "/stand-in/gmat", "GMAT stand-in", "stand-in available"
        ),
    )

    def fake_run(executable, script_path, timeout_s=180.0):
        for key in ("init", "postburn1"):
            (tmp_path / f"d_{key}.txt").write_text(
                "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n0 0 0 0 0 0 0\n"
            )
        (tmp_path / "d_trajectory.txt").write_text(
            "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
            "0 0 0 0 0 0 0\n1000 0 0 0 0 0 0\n"
        )
        # Perturb the final state far beyond the configured tolerances (km units).
        (tmp_path / "d_final.txt").write_text(
            "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
            "1373.0298005070088 0.5 0.5 0.0 0.01 0.01 0.0\n"
        )
        return gmat_verify.GMATRunResult(True, 0, "ok", "", False, "GMAT exited successfully.")

    monkeypatch.setattr(slice_runner, "run_gmat_script", fake_run)
    assert _run(tmp_path, monkeypatch=monkeypatch) == 1
    result = _result(tmp_path)
    assert result["verified"] is False
    assert result["failure_mode"] == "NUMERICAL_DISAGREEMENT"
    assert result["comparison"]["status"] in ("WARNING", "FAIL")
    assert result["comparison"]["position_error_m"] > result["comparison"]["tolerances"]["position_m"]


def test_slice_reports_screenshot_failure_when_svg_writer_is_corrupted(tmp_path, monkeypatch):
    """(e) The required screenshot artifact missing/corrupt is its own
    distinct failure mode, never silently a pass."""
    monkeypatch.setattr(
        slice_runner,
        "check_gmat_available",
        lambda executable, timeout_s=30.0: gmat_verify.GMATAvailability(
            True, "/stand-in/gmat", "GMAT stand-in", "stand-in available"
        ),
    )

    def fake_run(executable, script_path, timeout_s=180.0):
        for key in ("init", "postburn1"):
            (tmp_path / f"d_{key}.txt").write_text(
                "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n0 0 0 0 0 0 0\n"
            )
        (tmp_path / "d_trajectory.txt").write_text(
            "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
            "0 1.5e-05 -2e-04 0 -1.4e-04 0 0\n1373.0298005070088 0 0 0 0 0 0\n"
        )
        (tmp_path / "d_final.txt").write_text(
            "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
            "1373.0298005070088 0 0 0 0 0 0\n"
        )
        return gmat_verify.GMATRunResult(True, 0, "ok", "", False, "GMAT exited successfully.")

    def corrupt_svg_writer(path, trajectory_states_si):
        Path(path).write_text("")

    monkeypatch.setattr(slice_runner, "run_gmat_script", fake_run)
    monkeypatch.setattr(slice_runner, "write_svg", corrupt_svg_writer)
    assert _run(tmp_path, monkeypatch=monkeypatch) == 1
    result = _result(tmp_path)
    assert result["verified"] is False
    assert result["failure_mode"] == "SCREENSHOT_FAILURE"
    assert result["trajectory_artifact_nonempty"] is False


@pytest.mark.skipif(
    gmat_verify.check_gmat_available("GmatConsole-R2026a").available is False,
    reason="GmatConsole-R2026a is not available/runnable in this environment",
)
def test_slice_real_gmat_run_matches_cw_analytical_final_state(tmp_path):
    """(f) Real end-to-end run against GmatConsole-R2026a for the proven
    quarter-period CW benchmark case. Actually executes GMAT; asserts the
    real observed outcome rather than assuming success."""
    returncode = _run(tmp_path, gmat="GmatConsole-R2026a")
    result = _result(tmp_path)
    assert result["gmat"]["attempted"] is True, result["gmat"]
    assert result["gmat"]["exit_status"] == 0, result["gmat"].get("stderr")
    assert result["failure_mode"] is None, result
    assert result["verified"] is True, result["verification_status"]
    assert result["comparison"]["status"] == "PASS"
    # Matches the previously-proven residual scale (~5.6e-6 m / ~5e-9 m/s class).
    assert result["comparison"]["position_error_m"] < 1.0
    assert result["comparison"]["velocity_error_mps"] < 0.001
    assert returncode == 0


def test_generate_gmat_script_requires_absolute_report_paths(tmp_path):
    with pytest.raises(ValueError, match="absolute"):
        gmat_verify.generate_gmat_script(
            radius_m=6728000.0,
            deputy_state0_si=np.array([15.0, -200.0, 0.0, -0.14, 0.0, 0.0]),
            dv0_mps=np.zeros(3),
            dv1_mps=np.zeros(3),
            transfer_s=1000.0,
            report_paths={
                "init": Path("relative/init.txt"),
                "postburn1": (tmp_path / "postburn1.txt"),
                "final": (tmp_path / "final.txt"),
                "trajectory": (tmp_path / "trajectory.txt"),
            },
        )


def test_parse_gmat_report_rejects_wrong_row_count_as_malformed(tmp_path):
    report = tmp_path / "report.txt"
    report.write_text(
        "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
        "0 0 0 0 0 0 0\n1 0 0 0 0 0 0\n"
    )
    result = gmat_verify.parse_gmat_report(report, expect_single_row=True)
    assert result.ok is False
    assert "one data row" in result.reason


def test_parse_gmat_report_rejects_non_numeric_fields_as_malformed(tmp_path):
    report = tmp_path / "report.txt"
    report.write_text(
        "ElapsedSecs LVLH.X LVLH.Y LVLH.Z LVLH.VX LVLH.VY LVLH.VZ\n"
        "0 0 0 abc 0 0 0\n"
    )
    result = gmat_verify.parse_gmat_report(report, expect_single_row=True)
    assert result.ok is False
    assert "non-numeric" in result.reason


def test_compare_gmat_final_state_distinguishes_pass_warning_fail():
    cw_final = np.zeros(6)
    close = gmat_verify.compare_gmat_final_state(np.full(6, 1e-6), cw_final, pos_tol_m=1.0, vel_tol_mps=0.001)
    assert close.status == "PASS"
    warn = gmat_verify.compare_gmat_final_state(
        np.array([5.0, 0, 0, 0, 0, 0]), cw_final, pos_tol_m=1.0, vel_tol_mps=0.001
    )
    assert warn.status == "WARNING"
    fail = gmat_verify.compare_gmat_final_state(
        np.array([500.0, 0, 0, 0, 0, 0]), cw_final, pos_tol_m=1.0, vel_tol_mps=0.001
    )
    assert fail.status == "FAIL"


def test_validate_screenshot_distinguishes_missing_empty_and_well_formed(tmp_path):
    missing = gmat_verify.validate_screenshot(tmp_path / "missing.svg")
    assert missing.ok is False and "does not exist" in missing.reason

    empty = tmp_path / "empty.svg"
    empty.write_text("")
    assert gmat_verify.validate_screenshot(empty).ok is False

    malformed = tmp_path / "malformed.svg"
    malformed.write_text("not an svg at all")
    assert gmat_verify.validate_screenshot(malformed).ok is False

    good = tmp_path / "good.svg"
    good.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    assert gmat_verify.validate_screenshot(good).ok is True
