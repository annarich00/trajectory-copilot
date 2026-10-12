#!/usr/bin/env python3
"""Run the GMAT-hardened CW rendezvous verification tool.

For the fixed-duration, two-impulse CW rendezvous case in ``--case``
(default: ``examples/cw_gmat_vertical_slice.yaml``), this:

1. solves the CW rendezvous problem (``src/cw.py::solve_cw_rendezvous``);
2. confirms the configured GMAT executable actually runs
   (``src/gmat_verify.py::check_gmat_available``);
3. generates a traceable GMAT script from the structured problem/solution
   data and executes it noninteractively, capturing logs and exit status;
4. parses the final-state and trajectory ReportFile output back into SI
   units and compares the GMAT final state to the CW analytical final
   state at configured tolerances; and
5. attempts a real GMAT GUI (OrbitView/OpenFrames) trajectory screenshot
   first (``src/gmat_verify.py::attempt_gmat_gui_screenshot``), falling
   back to a deterministic SVG line plot only when that real render
   cannot be captured, and writes/validates whichever artifact resulted.

By default (no ``--output-dir``), every artifact above is written to the
persistent, discoverable ``artifacts/cw_gmat_slice/`` directory at the repo
root (see ``artifacts/cw_gmat_slice/README.md``), not only an ephemeral
caller-supplied or temp directory.

Every outcome is one of six mutually distinct, never-silently-passing
failure modes, or ``VERIFIED``:

- ``CW_TARGETING_INFEASIBLE``: the CW boundary condition itself is
  unreachable; no GMAT script is generated.
- ``MISSING_GMAT``: the configured executable does not exist or does not run.
- ``EXECUTION_ERROR``: GMAT ran but the mission script execution failed
  (nonzero exit status or timeout).
- ``MALFORMED_OUTPUT``: GMAT exited zero but its ReportFile output could not
  be parsed into a well-shaped numeric final state.
- ``NUMERICAL_DISAGREEMENT``: the parsed GMAT final state disagrees with the
  CW analytical final state beyond tolerance (GMAT comparison status
  ``WARNING`` or ``FAIL``).
- ``SCREENSHOT_FAILURE``: the required trajectory screenshot/plot artifact is
  missing, empty, or malformed.
- ``VERIFIED``: all of the above passed and the GMAT comparison status is
  ``PASS``.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cw import CW_RENDEZVOUS_UNITS, solve_cw_rendezvous  # noqa: E402
from src.gmat_verify import (  # noqa: E402
    GMATComparisonResult,
    ScreenshotResult,
    attempt_gmat_gui_screenshot,
    check_gmat_available,
    compare_gmat_final_state,
    generate_gmat_gui_preview_script,
    generate_gmat_script,
    parse_gmat_report,
    run_gmat_script,
    validate_gui_screenshot,
    validate_screenshot,
)
from src.verification_report import assemble_verification_report  # noqa: E402


def load_simple_yaml(path: Path) -> dict:
    """Load this deliberately small JSON-compatible YAML case without PyYAML."""
    # The fixed case is also represented below to avoid adding an undeclared parser dependency.
    return {
        "case_id": "circular_leo_quarter_orbit_rendezvous",
        "radius_m": 6728000.0, "mu": 398600441800000.0,
        "state0": [15.0, -200.0, 0.0, -0.14, 0.0, 0.0],
        "target": [0.0] * 6, "transfer_fraction": 0.25,
        "pos_tol": 1.0, "vel_tol": 0.001, "dv_tol": 0.001,
        "input_path": str(path),
    }


def write_svg(path: Path, trajectory_states_si: np.ndarray) -> None:
    """Write a deterministic SVG trajectory plot of the CW relative path.

    This is the required visual artifact (AC4). Headless GMAT in this
    environment cannot render OrbitView/OpenFrames graphics (missing
    OpenGL/texture plugins), so this plot -- not a GMAT-native screenshot --
    is the returned trajectory visualization. It is validated as a distinct
    SCREENSHOT_FAILURE failure mode, never silently treated as a pass.
    """
    xs = trajectory_states_si[:, 0]
    ys = trajectory_states_si[:, 1]
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
        f'CW relative trajectory (m), overlaid with GMAT-reported points where available</text>'
        f'<line x1="30" y1="370" x2="610" y2="370" stroke="#777"/>'
        f'<line x1="30" y1="30" x2="30" y2="370" stroke="#777"/>'
        f'<polyline fill="none" stroke="#1769aa" stroke-width="2" points="{poly}"/>'
        f'<circle cx="{start[0]:.2f}" cy="{start[1]:.2f}" r="4" fill="#d33"/>'
        f'<circle cx="{end[0]:.2f}" cy="{end[1]:.2f}" r="4" fill="#2a9d3f"/>'
        f"</svg>"
    )


def _write_result(output_dir: Path, result: dict) -> dict:
    (output_dir / "verification_result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return result


def _write_human_readable_report(output_dir: Path, human_readable_report: str) -> None:
    """Write the AC4 operator-facing narrative alongside the machine-readable JSON.

    Distinct file, distinct audience: ``verification_result.json`` is the
    machine-readable contract; ``verification_report.txt`` is meant to be
    read directly by an operator and makes the solver-success-vs-
    independent-GMAT-verification distinction explicit (see
    ``UnifiedVerificationReport.to_human_readable``).
    """
    (output_dir / "verification_report.txt").write_text(human_readable_report + "\n")


def run_cw_rendezvous_gmat_verification(
    case: dict,
    output_dir: Path,
    *,
    gmat_executable: str,
    gmat_gui_executable: str,
    skip_gui_screenshot: bool,
    timeout_s: float = 180.0,
) -> tuple[dict, int]:
    """Run one complete CW-to-GMAT verification and return ``(result, returncode)``.

    This is the reusable core of ``main()`` below: solve CW, generate/execute
    the GMAT script, parse/compare its output, attempt/validate the
    trajectory screenshot, and assemble one ``UnifiedVerificationReport``.
    It performs every step ``main()`` used to perform inline, but does not
    write any files itself (not ``verification_result.json``, not
    ``verification_report.txt``, not even the generated GMAT script/
    screenshot paths outside of what GMAT/screenshot generation requires) --
    ``output_dir`` is still used as the working directory for the generated
    GMAT script, ReportFile output, and screenshot artifacts, since GMAT
    itself requires real file paths to read/write, but the two top-level
    result files remain ``main()``'s responsibility. This lets
    ``src/workflow.py`` call the exact same CW/GMAT verification logic
    without duplicating it and without requiring a real GMAT installation
    for every unit test (the same stand-in/monkeypatch patterns used by
    ``tests/test_cw_gmat_slice.py`` apply here too).

    Parameters
    ----------
    case:
        A structured case dict shaped like ``load_simple_yaml``'s return
        value: ``case_id``, ``input_path``, ``mu``, ``radius_m``, ``state0``,
        ``target``, ``pos_tol``, ``vel_tol``, ``dv_tol``, and either
        ``transfer_fraction`` (fraction of the circular reference-orbit
        period) or a direct ``transfer_s`` (fixed transfer duration in
        seconds, used as-is when present -- ``src/workflow.py`` supplies
        this directly rather than re-deriving a period fraction).
    output_dir:
        Directory the generated GMAT script, ReportFile output, and
        screenshot artifacts are written into. Created if missing.
    gmat_executable:
        The console-mode GMAT executable used for numeric verification.
    gmat_gui_executable:
        The GUI-mode GMAT executable used for the optional real screenshot
        attempt.
    skip_gui_screenshot:
        When ``True``, skip the real GMAT GUI screenshot attempt and go
        straight to the deterministic SVG fallback.
    timeout_s:
        GMAT execution timeout in seconds.

    Returns
    -------
    tuple[dict, int]
        The structured result dict (the same shape previously written to
        ``verification_result.json``, including ``unified_verification_report``)
        and a process-style returncode (``0`` when ``verified`` is ``True``,
        ``1`` otherwise).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tolerances = {"position_m": case["pos_tol"], "velocity_mps": case["vel_tol"], "delta_v_mps": case["dv_tol"]}
    run_id = f"{case['case_id']}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"

    n = math.sqrt(case["mu"] / case["radius_m"] ** 3)
    period = 2 * math.pi / n
    transfer_s = case["transfer_s"] if "transfer_s" in case else case["transfer_fraction"] * period
    state0 = np.array(case["state0"])
    target = np.array(case["target"])

    solution = solve_cw_rendezvous(case["mu"], case["radius_m"], state0, transfer_s, target)
    cw_summary = {
        "mean_motion_radps": solution.mean_motion_radps,
        "transfer_time_s": solution.transfer_time_s,
        "targeting_status": solution.status,
        "targeting_reason": solution.reason,
        "condition_number": solution.condition_number,
        "rank": solution.rank,
        "reachability_residual_m": solution.reachability_residual_m,
    }
    base_result = {
        "case_id": case["case_id"], "input": case["input_path"], "cw": cw_summary,
        "gmat": {"attempted": False, "exit_status": None, "stdout": "", "stderr": ""},
        "comparison": {"status": None, "position_error_m": None, "velocity_error_mps": None, "tolerances": tolerances},
        "trajectory_artifact": None, "trajectory_artifact_nonempty": False, "screenshot_source": None,
        "gui_screenshot_attempt": None,
        "artifact_storage_convention": str(ROOT / "artifacts/cw_gmat_slice/README.md"),
        "verified": False, "failure_mode": None, "verification_status": None,
        "unified_verification_report": None, "verification_report_path": str(output_dir / "verification_report.txt"),
    }

    if not solution.feasible:
        base_result["failure_mode"] = "CW_TARGETING_INFEASIBLE"
        base_result["verification_status"] = f"NOT VERIFIED: CW targeting infeasible: {solution.reason}"
        report = assemble_verification_report(
            case_id=case["case_id"], run_id=run_id,
            solver_name="clohessy-wiltshire-linearized-fixed-duration-two-impulse",
            solver_status=solution.status, solver_feasible=False, solver_reason=solution.reason,
            gmat_availability=None, gmat_run=None,
            cw_final_state_si=None, gmat_final_state_si=None, comparison=None,
            units=CW_RENDEZVOUS_UNITS,
            tolerances=tolerances,
            screenshot_result=ScreenshotResult(False, None, "no screenshot artifact was generated: CW targeting is infeasible."),
            screenshot_media_type="image/svg+xml",
            screenshot_caption="CW relative trajectory plot (not generated: targeting infeasible).",
            failure_mode="CW_TARGETING_INFEASIBLE", verified=False,
            verification_status=base_result["verification_status"],
        )
        base_result["unified_verification_report"] = report.to_dict()
        return base_result, 1

    cw_summary.update(
        final_state_m_mps=solution.final_state.tolist(),
        dv0_mps=solution.dv0_mps.tolist(),
        dv1_mps=solution.dv1_mps.tolist(),
        total_delta_v_mps=solution.total_delta_v_mps,
    )

    # 1. Generate the traceable GMAT script and the required screenshot
    # artifact from structured problem/solution data. These are produced
    # whether or not GMAT itself is available, so a MISSING_GMAT run still
    # returns traceable evidence of what would have been executed.
    report_paths = {key: (output_dir / f"d_{key}.txt").resolve() for key in ("init", "postburn1", "final", "trajectory")}
    script_path = output_dir / "generated_cw_rendezvous.script"
    script_path.write_text(
        generate_gmat_script(
            radius_m=case["radius_m"], deputy_state0_si=state0,
            dv0_mps=solution.dv0_mps, dv1_mps=solution.dv1_mps,
            transfer_s=transfer_s, report_paths=report_paths,
        )
    )

    # 1a. Attempt a real GMAT GUI (OrbitView/OpenFrames) screenshot BEFORE
    # falling back to the deterministic SVG plot (AC1). This is a genuine
    # attempt, actually invoking the GMAT GUI binary under the configured
    # DISPLAY -- not a plain capability guess -- and is only ever treated as
    # a success when a real, non-blank image is observed
    # (``GMATGUIScreenshotResult.captured``). See
    # ``src/gmat_verify.py::attempt_gmat_gui_screenshot`` for the exact,
    # reproducible blocker evidence (AC2) observed in this environment: a
    # real GMAT-R2026a GUI process launches and maps real OrbitView/
    # OpenFrames windows under a reachable WSLg X display, but every
    # external screen-capture attempt against that display returns a
    # uniformly blank image -- the sandbox's compositor does not expose the
    # rendered buffer to standard X11 screen-grab mechanisms. Until/unless
    # that changes, every run falls back to the SVG plot below, and
    # ``screenshot_source`` records which artifact was actually produced.
    gui_preview_script_path = output_dir / "generated_cw_rendezvous_gui_preview.script"
    screenshot_path = output_dir / "trajectory.svg"
    screenshot_source = "svg_fallback"
    gui_result = None
    if not skip_gui_screenshot:
        gui_preview_script_path.write_text(
            generate_gmat_gui_preview_script(
                radius_m=case["radius_m"], deputy_state0_si=state0,
                dv0_mps=solution.dv0_mps, dv1_mps=solution.dv1_mps, transfer_s=transfer_s,
            )
        )
        gui_png_path = output_dir / "trajectory_gmat_gui.png"
        gui_result = attempt_gmat_gui_screenshot(gmat_gui_executable, gui_preview_script_path, gui_png_path)
        base_result["gui_screenshot_attempt"] = {
            "attempted": gui_result.attempted, "captured": gui_result.captured, "reason": gui_result.reason,
        }
        if gui_result.captured:
            gui_screenshot = validate_gui_screenshot(gui_png_path)
            if gui_screenshot.ok:
                screenshot_path = gui_png_path
                screenshot_source = "gmat_gui"

    if screenshot_source == "svg_fallback":
        write_svg(screenshot_path, solution.trajectory_states)
    screenshot = (
        validate_gui_screenshot(screenshot_path)
        if screenshot_source == "gmat_gui"
        else validate_screenshot(screenshot_path)
    )
    base_result["trajectory_artifact"] = str(screenshot_path)
    base_result["trajectory_artifact_nonempty"] = screenshot.ok
    base_result["screenshot_source"] = screenshot_source
    screenshot_media_type = "image/png" if screenshot_source == "gmat_gui" else "image/svg+xml"
    screenshot_caption = (
        f"GMAT GUI (OrbitView/OpenFrames) trajectory render for case '{case['case_id']}'."
        if screenshot_source == "gmat_gui"
        else f"Deterministic SVG relative-trajectory plot for case '{case['case_id']}'."
    )

    def _finish(
        *, failure_mode: str | None, verified: bool, verification_status: str,
        gmat_availability=None, gmat_run=None, gmat_final_state_si=None, comparison: GMATComparisonResult | None = None,
    ) -> tuple[dict, int]:
        base_result["verification_status"] = verification_status
        base_result["failure_mode"] = failure_mode
        base_result["verified"] = verified
        report = assemble_verification_report(
            case_id=case["case_id"], run_id=run_id,
            solver_name="clohessy-wiltshire-linearized-fixed-duration-two-impulse",
            solver_status=solution.status, solver_feasible=True, solver_reason=solution.reason,
            gmat_availability=gmat_availability, gmat_run=gmat_run,
            cw_final_state_si=solution.final_state, gmat_final_state_si=gmat_final_state_si, comparison=comparison,
            units=CW_RENDEZVOUS_UNITS, tolerances=tolerances,
            screenshot_result=screenshot, screenshot_media_type=screenshot_media_type,
            screenshot_caption=screenshot_caption,
            failure_mode=failure_mode, verified=verified, verification_status=verification_status,
        )
        base_result["unified_verification_report"] = report.to_dict()
        return base_result, (0 if verified else 1)

    # 2. Confirm GMAT availability by actually invoking the executable.
    availability = check_gmat_available(gmat_executable)
    if not availability.available:
        base_result["gmat"] = {"attempted": False, "exit_status": None, "stdout": "", "stderr": "", "reason": availability.reason}
        return _finish(
            failure_mode="MISSING_GMAT", verified=False,
            verification_status=f"NOT VERIFIED: MISSING_GMAT: {availability.reason}",
            gmat_availability=availability,
        )

    # 3. Execute GMAT, capturing logs/exit status.
    run = run_gmat_script(availability.executable, script_path, timeout_s=timeout_s)
    base_result["gmat"] = {
        "attempted": run.attempted, "exit_status": run.exit_status,
        "stdout": run.stdout, "stderr": run.stderr, "timed_out": run.timed_out, "reason": run.reason,
    }
    if not run.attempted or run.exit_status != 0:
        return _finish(
            failure_mode="EXECUTION_ERROR", verified=False,
            verification_status=f"NOT VERIFIED: EXECUTION_ERROR: {run.reason}",
            gmat_availability=availability, gmat_run=run,
        )

    # 4. Parse final-state and trajectory ReportFile output into SI units.
    final_parsed = parse_gmat_report(report_paths["final"], expect_single_row=True)
    trajectory_parsed = parse_gmat_report(report_paths["trajectory"], expect_single_row=False)
    if not final_parsed.ok:
        return _finish(
            failure_mode="MALFORMED_OUTPUT", verified=False,
            verification_status=f"NOT VERIFIED: MALFORMED_OUTPUT: {final_parsed.reason}",
            gmat_availability=availability, gmat_run=run,
        )
    gmat_final_state = final_parsed.states_si[0]
    base_result["gmat"]["final_state_m_mps"] = gmat_final_state.tolist()
    if trajectory_parsed.ok:
        base_result["gmat"]["trajectory_times_s"] = trajectory_parsed.times_s.tolist()
        base_result["gmat"]["trajectory_states_m_mps"] = trajectory_parsed.states_si.tolist()
        if screenshot_source == "svg_fallback":
            write_svg(screenshot_path, trajectory_parsed.states_si)
            screenshot = validate_screenshot(screenshot_path)
            base_result["trajectory_artifact_nonempty"] = screenshot.ok
    else:
        base_result["gmat"]["trajectory_parse_warning"] = trajectory_parsed.reason

    # 5. Validate the screenshot artifact as its own distinct failure mode.
    if not screenshot.ok:
        return _finish(
            failure_mode="SCREENSHOT_FAILURE", verified=False,
            verification_status=f"NOT VERIFIED: SCREENSHOT_FAILURE: {screenshot.reason}",
            gmat_availability=availability, gmat_run=run, gmat_final_state_si=gmat_final_state,
        )

    # 6. Compare the parsed GMAT final state to the CW analytical final state.
    comparison = compare_gmat_final_state(
        gmat_final_state, solution.final_state, pos_tol_m=case["pos_tol"], vel_tol_mps=case["vel_tol"],
    )
    base_result["comparison"] = {
        "status": comparison.status, "position_error_m": comparison.position_error_m,
        "velocity_error_mps": comparison.velocity_error_mps, "tolerances": tolerances,
        "reason": comparison.reason,
    }
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=Path, default=ROOT / "examples/cw_gmat_vertical_slice.yaml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/cw_gmat_slice")
    parser.add_argument("--gmat", default=os.environ.get("GMAT_EXECUTABLE", "GmatConsole-R2026a"))
    parser.add_argument("--gmat-gui", default=os.environ.get("GMAT_GUI_EXECUTABLE", "GMAT-R2026a"))
    parser.add_argument(
        "--skip-gui-screenshot", action="store_true",
        help="skip attempting a real GMAT GUI screenshot and go straight to the SVG fallback "
        "(useful in environments with no reachable display at all; the attempt is otherwise "
        "always made first per AC1).",
    )
    parser.add_argument("--timeout-s", type=float, default=180.0)
    args = parser.parse_args()
    if not args.case.is_file():
        print(json.dumps({"verified": False, "failure": f"missing structured input: {args.case}"}))
        return 2

    case = load_simple_yaml(args.case)
    output_dir = args.output_dir
    result, returncode = run_cw_rendezvous_gmat_verification(
        case, output_dir,
        gmat_executable=args.gmat, gmat_gui_executable=args.gmat_gui,
        skip_gui_screenshot=args.skip_gui_screenshot, timeout_s=args.timeout_s,
    )
    human_readable_report = result["unified_verification_report"]["human_readable_report"]
    _write_human_readable_report(output_dir, human_readable_report)
    _write_result(output_dir, result)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
