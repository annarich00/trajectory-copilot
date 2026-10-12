import json
import os
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


def _run(tmp_path, gmat="definitely-not-gmat", monkeypatch=None, argv_extra=None, skip_gui_screenshot=True):
    import sys as _sys

    argv = ["run_cw_gmat_slice.py", "--output-dir", str(tmp_path), "--gmat", gmat]
    if skip_gui_screenshot:
        argv += ["--skip-gui-screenshot"]
    if argv_extra:
        argv += argv_extra
    if monkeypatch is not None:
        monkeypatch.setattr(_sys, "argv", argv)
        return slice_runner.main()
    completed = subprocess.run(
        [sys.executable, "scripts/run_cw_gmat_slice.py", *argv[1:]],
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
    assert result["screenshot_source"] == "svg_fallback"
    assert (tmp_path / "generated_cw_rendezvous.script").stat().st_size > 0
    assert result["cw"]["targeting_status"] == "unique"
    assert result["cw"]["total_delta_v_mps"] > 0
    assert result["comparison"]["tolerances"]["position_m"] == 1.0
    # TJC-1.19: the unified report structure is assembled for every outcome.
    unified = result["unified_verification_report"]
    assert unified["failure_mode"] == "MISSING_GMAT"
    assert unified["verified"] is False
    assert unified["screenshot"]["ok"] is True
    assert unified["screenshot"]["media_type"] == "image/svg+xml"
    assert "SOLVER" in unified["human_readable_report"]
    assert (tmp_path / "verification_report.txt").is_file()


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
    # TJC-1.19: the unified report structure is still assembled for the
    # earliest failure mode, with an honestly invalid (not-generated) screenshot.
    unified = result["unified_verification_report"]
    assert unified["failure_mode"] == "CW_TARGETING_INFEASIBLE"
    assert unified["verified"] is False
    assert unified["screenshot"]["ok"] is False
    assert unified["solver"]["feasible"] is False


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
    unified = result["unified_verification_report"]
    assert unified["failure_mode"] == "EXECUTION_ERROR"
    assert unified["verified"] is False
    assert "INDEPENDENT VERIFICATION: NOT PERFORMED" in unified["human_readable_report"]


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
    unified = result["unified_verification_report"]
    assert unified["failure_mode"] == "MALFORMED_OUTPUT"
    assert unified["verified"] is False
    assert unified["comparison"]["status"] == "INCOMPLETE"


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
    unified = result["unified_verification_report"]
    assert unified["failure_mode"] == "NUMERICAL_DISAGREEMENT"
    assert unified["verified"] is False
    assert unified["comparison"]["status"] in ("WARNING", "FAIL")
    assert "LIKELY CAUSE" in unified["human_readable_report"]


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
    unified = result["unified_verification_report"]
    assert unified["failure_mode"] == "SCREENSHOT_FAILURE"
    assert unified["verified"] is False
    assert unified["screenshot"]["ok"] is False
    assert "SCREENSHOT: MISSING OR INVALID" in unified["human_readable_report"]


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
    unified = result["unified_verification_report"]
    assert unified["verified"] is True
    assert unified["comparison"]["status"] == "PASS"
    assert "GMAT independently verified the candidate solution" in unified["human_readable_report"]
    assert (tmp_path / "verification_report.txt").is_file()


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


def test_validate_gui_screenshot_distinguishes_missing_small_and_well_formed_png(tmp_path):
    missing = gmat_verify.validate_gui_screenshot(tmp_path / "missing.png")
    assert missing.ok is False and "does not exist" in missing.reason

    too_small = tmp_path / "tiny.png"
    too_small.write_bytes(b"\x89PNG\r\n\x1a\n")
    assert gmat_verify.validate_gui_screenshot(too_small).ok is False

    not_png = tmp_path / "not_png.png"
    not_png.write_bytes(b"not a png file" + b"\x00" * 200)
    assert gmat_verify.validate_gui_screenshot(not_png).ok is False

    real_png = tmp_path / "real.png"
    real_png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)
    assert gmat_verify.validate_gui_screenshot(real_png).ok is True


def test_attempt_gmat_gui_screenshot_reports_missing_display_without_launching():
    """No DISPLAY configured at all: distinct, explicit reason, no launch attempted."""
    result = gmat_verify.attempt_gmat_gui_screenshot(
        "definitely-not-a-real-gmat-gui-binary", Path("/tmp/does-not-matter.script"),
        Path("/tmp/does-not-matter.png"), display="",
    )
    assert result.attempted is False
    assert result.captured is False
    assert "DISPLAY" in result.reason


def test_attempt_gmat_gui_screenshot_reports_missing_executable(monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    result = gmat_verify.attempt_gmat_gui_screenshot(
        "definitely-not-a-real-gmat-gui-binary", Path("/tmp/does-not-matter.script"), Path("/tmp/does-not-matter.png"),
    )
    assert result.attempted is False
    assert result.captured is False
    assert "was not found" in result.reason


@pytest.mark.skipif(
    not os.environ.get("DISPLAY"),
    reason="no DISPLAY environment variable configured in this environment; a real GMAT GUI "
    "screenshot capture attempt requires a reachable X display (e.g. this sandboxed WSLg "
    "DISPLAY=:0, or a genuine Xvfb-backed display elsewhere).",
)
def test_attempt_real_gmat_gui_screenshot_documents_observed_sandbox_blocker(tmp_path):
    """(g) Real end-to-end attempt at a GMAT GUI screenshot under this environment's actual
    reachable display. Actually launches GMAT-R2026a and actually attempts a screen capture --
    does not assume the outcome. As investigated and documented in
    ``src/gmat_verify.py::attempt_gmat_gui_screenshot``'s docstring, this sandboxed WSLg
    environment's compositor does not expose the rendered OpenFrames/OrbitView buffer to
    external X11 screen capture, so ``captured`` is expected to be ``False`` here with an
    explicit reason -- but ``attempted`` must still be ``True`` (GMAT GUI really launches and
    maps real windows), and if a future environment change makes real capture possible, this
    test will observe ``captured is True`` without needing to be rewritten.
    """
    script_path = tmp_path / "gui_preview.script"
    script_path.write_text(
        gmat_verify.generate_gmat_gui_preview_script(
            radius_m=6728000.0,
            deputy_state0_si=np.array([15.0, -200.0, 0.0, -0.14, 0.0, 0.0]),
            dv0_mps=np.array([0.0, 0.01, 0.0]),
            dv1_mps=np.array([0.0, -0.01, 0.0]),
            transfer_s=1373.0,
        )
    )
    result = gmat_verify.attempt_gmat_gui_screenshot(
        "GMAT-R2026a", script_path, tmp_path / "trajectory_gmat_gui.png", render_wait_s=6.0,
    )
    assert result.attempted is True, result.reason
    if result.captured:
        assert gmat_verify.validate_gui_screenshot(Path(result.path)).ok is True
    else:
        assert result.reason, "a non-captured attempt must still explain why, not merely assert failure"


def test_slice_distinguishes_screenshot_source_gmat_gui_from_svg_fallback(tmp_path, monkeypatch):
    """AC5: the structured result's ``screenshot_source`` field distinguishes a real captured
    GMAT GUI render from the SVG fallback, and only exists as of TJC-2."""
    assert _run(tmp_path / "fallback_run", gmat="definitely-not-gmat") == 1
    fallback_result = _result(tmp_path / "fallback_run")
    assert fallback_result["screenshot_source"] == "svg_fallback"
    assert fallback_result["trajectory_artifact"].endswith(".svg")

    def fake_gui_capture(gui_executable, script_path, output_path, **kwargs):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)
        return gmat_verify.GMATGUIScreenshotResult(True, True, str(output_path), "captured a non-blank render.")

    monkeypatch.setattr(slice_runner, "attempt_gmat_gui_screenshot", fake_gui_capture)
    gui_run_dir = tmp_path / "gui_run"
    assert _run(gui_run_dir, gmat="definitely-not-gmat", monkeypatch=monkeypatch, skip_gui_screenshot=False) == 1
    gui_result = _result(gui_run_dir)
    assert gui_result["screenshot_source"] == "gmat_gui"
    assert gui_result["trajectory_artifact"].endswith(".png")
    assert gui_result["trajectory_artifact_nonempty"] is True
    assert gui_result["gui_screenshot_attempt"] == {
        "attempted": True, "captured": True, "reason": "captured a non-blank render.",
    }


def test_slice_default_output_dir_is_the_persistent_artifacts_location():
    """AC3: the documented, persistent default output location (no --output-dir override) is
    actually ``artifacts/cw_gmat_slice`` at the repo root, with a tracked README explaining the
    convention."""
    import inspect as _inspect

    source = _inspect.getsource(slice_runner.main)
    assert '"--output-dir", type=Path, default=ROOT / "artifacts/cw_gmat_slice"' in source
    readme = ROOT / "artifacts" / "cw_gmat_slice" / "README.md"
    assert readme.is_file(), "artifacts/cw_gmat_slice/README.md must document the persistent output convention"
    assert "gitignore" in readme.read_text().lower()
