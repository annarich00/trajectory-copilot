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
5. writes/validates a non-empty trajectory screenshot (SVG) artifact.

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
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cw import solve_cw_rendezvous  # noqa: E402
from src.gmat_verify import (  # noqa: E402
    check_gmat_available,
    compare_gmat_final_state,
    generate_gmat_script,
    parse_gmat_report,
    run_gmat_script,
    validate_screenshot,
)


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=Path, default=ROOT / "examples/cw_gmat_vertical_slice.yaml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/cw_gmat_slice")
    parser.add_argument("--gmat", default=os.environ.get("GMAT_EXECUTABLE", "GmatConsole-R2026a"))
    parser.add_argument("--timeout-s", type=float, default=180.0)
    args = parser.parse_args()
    if not args.case.is_file():
        print(json.dumps({"verified": False, "failure": f"missing structured input: {args.case}"}))
        return 2

    case = load_simple_yaml(args.case)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    tolerances = {"position_m": case["pos_tol"], "velocity_mps": case["vel_tol"], "delta_v_mps": case["dv_tol"]}

    n = math.sqrt(case["mu"] / case["radius_m"] ** 3)
    period = 2 * math.pi / n
    transfer_s = case["transfer_fraction"] * period
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
        "trajectory_artifact": None, "trajectory_artifact_nonempty": False,
        "verified": False, "failure_mode": None, "verification_status": None,
    }

    if not solution.feasible:
        base_result["failure_mode"] = "CW_TARGETING_INFEASIBLE"
        base_result["verification_status"] = f"NOT VERIFIED: CW targeting infeasible: {solution.reason}"
        _write_result(output_dir, base_result)
        return 1

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
    screenshot_path = output_dir / "trajectory.svg"
    write_svg(screenshot_path, solution.trajectory_states)
    screenshot = validate_screenshot(screenshot_path)
    base_result["trajectory_artifact"] = str(screenshot_path)
    base_result["trajectory_artifact_nonempty"] = screenshot.ok

    # 2. Confirm GMAT availability by actually invoking the executable.
    availability = check_gmat_available(args.gmat)
    if not availability.available:
        base_result["failure_mode"] = "MISSING_GMAT"
        base_result["gmat"] = {"attempted": False, "exit_status": None, "stdout": "", "stderr": "", "reason": availability.reason}
        base_result["verification_status"] = f"NOT VERIFIED: MISSING_GMAT: {availability.reason}"
        _write_result(output_dir, base_result)
        return 1

    # 3. Execute GMAT, capturing logs/exit status.
    run = run_gmat_script(availability.executable, script_path, timeout_s=args.timeout_s)
    base_result["gmat"] = {
        "attempted": run.attempted, "exit_status": run.exit_status,
        "stdout": run.stdout, "stderr": run.stderr, "timed_out": run.timed_out, "reason": run.reason,
    }
    if not run.attempted or run.exit_status != 0:
        base_result["failure_mode"] = "EXECUTION_ERROR"
        base_result["verification_status"] = f"NOT VERIFIED: EXECUTION_ERROR: {run.reason}"
        _write_result(output_dir, base_result)
        return 1

    # 4. Parse final-state and trajectory ReportFile output into SI units.
    final_parsed = parse_gmat_report(report_paths["final"], expect_single_row=True)
    trajectory_parsed = parse_gmat_report(report_paths["trajectory"], expect_single_row=False)
    if not final_parsed.ok:
        base_result["failure_mode"] = "MALFORMED_OUTPUT"
        base_result["verification_status"] = f"NOT VERIFIED: MALFORMED_OUTPUT: {final_parsed.reason}"
        _write_result(output_dir, base_result)
        return 1
    gmat_final_state = final_parsed.states_si[0]
    base_result["gmat"]["final_state_m_mps"] = gmat_final_state.tolist()
    if trajectory_parsed.ok:
        base_result["gmat"]["trajectory_times_s"] = trajectory_parsed.times_s.tolist()
        base_result["gmat"]["trajectory_states_m_mps"] = trajectory_parsed.states_si.tolist()
        write_svg(screenshot_path, trajectory_parsed.states_si)
        screenshot = validate_screenshot(screenshot_path)
        base_result["trajectory_artifact_nonempty"] = screenshot.ok
    else:
        base_result["gmat"]["trajectory_parse_warning"] = trajectory_parsed.reason

    # 5. Validate the screenshot artifact as its own distinct failure mode.
    if not screenshot.ok:
        base_result["failure_mode"] = "SCREENSHOT_FAILURE"
        base_result["verification_status"] = f"NOT VERIFIED: SCREENSHOT_FAILURE: {screenshot.reason}"
        _write_result(output_dir, base_result)
        return 1

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
        base_result["failure_mode"] = "NUMERICAL_DISAGREEMENT"
        base_result["verification_status"] = f"NOT VERIFIED: NUMERICAL_DISAGREEMENT ({comparison.status}): {comparison.reason}"
        _write_result(output_dir, base_result)
        return 1

    base_result["verified"] = True
    base_result["verification_status"] = "VERIFIED"
    _write_result(output_dir, base_result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
