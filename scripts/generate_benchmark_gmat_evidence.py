#!/usr/bin/env python3
"""Generate the committed GMAT evidence for TJC-1.9's benchmark cases (b) and (c).

This script is a thin, benchmark-specific *caller* of the already-audited,
already-hardened GMAT verification machinery in ``src/gmat_verify.py``,
``src/cw.py``, and ``src/twobody.py`` -- it does not modify, re-implement, or
change the behavior or output shape of any of those modules, and it does not
touch ``scripts/run_cw_gmat_slice.py`` (that script's committed example run
is reused as-is for benchmark case (a); see
``examples/cw_gmat_slice_example/``).

It produces, for AC3's two remaining solvable benchmark categories:

- case (b), boundary: the same quarter-period CW rendezvous case but at a
  half-orbital-period transfer time, where ``src/cw.py::two_burn_targeting``
  reports a singular-but-reachable ``Phi_rv`` (see
  ``evaluations/benchmark/case_b_boundary_cw.yaml``); and
- case (c), CW-invalid/two-body: a declared point-mass coast case (a LEO
  chaser offset radially by 1,000 km -- clearly not local CW proximity
  motion) that ``src/model_selector.py`` routes to the bounded two-body
  fallback (see ``evaluations/benchmark/case_c_two_body.yaml``).

Each case's committed output directory (``examples/benchmark_case_b_boundary/``,
``examples/benchmark_case_c_two_body/``) mirrors the existing
``examples/cw_gmat_slice_example/`` convention: a parsed/compared
``verification_result.json`` and a required SVG trajectory screenshot are
committed; the generated GMAT script and intermediate ReportFile output are
written to a temporary directory per run (not committed), exactly as
``examples/cw_gmat_slice_example/`` commits only its result/screenshot, not
its generated script.

Usage::

    .venv/bin/python scripts/generate_benchmark_gmat_evidence.py --gmat GmatConsole-R2026a
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cw import mean_motion, solve_cw_rendezvous  # noqa: E402
from src.gmat_verify import (  # noqa: E402
    check_gmat_available,
    compare_gmat_final_state,
    generate_gmat_script,
    parse_gmat_report,
    run_gmat_script,
    validate_screenshot,
)
from src.twobody import propagate_cartesian_state, vis_viva_speed  # noqa: E402

MU_EARTH = 398600441800000.0

# Case (c)'s GMAT script reports the inertial EarthMJ2000Eq frame directly
# (the same frame src/twobody.py declares, reference/SOURCE.md Sec A.2), not
# the CW-specific LVLH-relative columns src/gmat_verify.py::REPORT_COLUMNS
# expects. That function is left untouched (it is a different, LVLH-specific
# contract used by scripts/run_cw_gmat_slice.py for cases (a)/(b)); this is a
# small, local parser for this benchmark script's own report shape only.
_TWO_BODY_REPORT_COLUMNS = (
    "ElapsedSecs", "EarthMJ2000Eq.X", "EarthMJ2000Eq.Y", "EarthMJ2000Eq.Z",
    "EarthMJ2000Eq.VX", "EarthMJ2000Eq.VY", "EarthMJ2000Eq.VZ",
)


def _parse_inertial_report(path: Path) -> np.ndarray | None:
    """Parse one single-row EarthMJ2000Eq ReportFile into an SI 6-vector."""
    if not path.is_file():
        return None
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    if len(lines) != 2:
        return None
    header = lines[0].split()
    if len(header) != len(_TWO_BODY_REPORT_COLUMNS):
        return None
    for column, header_field in zip(_TWO_BODY_REPORT_COLUMNS, header):
        if column not in header_field:
            return None
    fields = lines[1].split()
    if len(fields) != len(_TWO_BODY_REPORT_COLUMNS):
        return None
    values = np.array([float(f) for f in fields[1:]], dtype=float)
    if not np.isfinite(values).all():
        return None
    return np.hstack([values[:3] * 1000.0, values[3:] * 1000.0])


def write_svg(path: Path, trajectory_states_si: np.ndarray, title: str) -> None:
    """Deterministic SVG trajectory plot, matching scripts/run_cw_gmat_slice.py::write_svg."""
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
        f'<text x="20" y="24" font-family="sans-serif" font-size="16">{title}</text>'
        f'<line x1="30" y1="370" x2="610" y2="370" stroke="#777"/>'
        f'<line x1="30" y1="30" x2="30" y2="370" stroke="#777"/>'
        f'<polyline fill="none" stroke="#1769aa" stroke-width="2" points="{poly}"/>'
        f'<circle cx="{start[0]:.2f}" cy="{start[1]:.2f}" r="4" fill="#d33"/>'
        f'<circle cx="{end[0]:.2f}" cy="{end[1]:.2f}" r="4" fill="#2a9d3f"/>'
        f"</svg>"
    )


def run_boundary_case(output_dir: Path, work_dir: Path, gmat_executable: str, timeout_s: float) -> dict:
    """Case (b): half-orbital-period CW transfer (singular-reachable Phi_rv)."""
    radius_m = 6728000.0
    n = mean_motion(MU_EARTH, radius_m)
    period = 2 * math.pi / n
    transfer_s = period / 2.0
    state0 = np.array([15.0, -200.0, 0.0, -0.14, 0.0, 0.0])
    target = np.zeros(6)

    solution = solve_cw_rendezvous(MU_EARTH, radius_m, state0, transfer_s, target)
    result = {
        "case_id": "benchmark_case_b_boundary_cw",
        "cw": {
            "mean_motion_radps": solution.mean_motion_radps,
            "transfer_time_s": solution.transfer_time_s,
            "targeting_status": solution.status,
            "targeting_reason": solution.reason,
            "condition_number": solution.condition_number,
            "rank": solution.rank,
            "reachability_residual_m": solution.reachability_residual_m,
            "dv0_mps": solution.dv0_mps.tolist(),
            "dv1_mps": solution.dv1_mps.tolist(),
            "total_delta_v_mps": solution.total_delta_v_mps,
            "final_state_m_mps": solution.final_state.tolist(),
        },
        "gmat": {"attempted": False},
        "comparison": {"status": None},
        "verified": False,
        "failure_mode": None,
        "verification_status": None,
    }
    tolerances = {"position_m": 1.0, "velocity_mps": 0.001, "delta_v_mps": 0.001}
    result["comparison"]["tolerances"] = tolerances

    report_paths = {key: (work_dir / f"d_{key}.txt").resolve() for key in ("init", "postburn1", "final", "trajectory")}
    script_path = work_dir / "generated_boundary_cw.script"
    script_path.write_text(
        generate_gmat_script(
            radius_m=radius_m, deputy_state0_si=state0,
            dv0_mps=solution.dv0_mps, dv1_mps=solution.dv1_mps,
            transfer_s=transfer_s, report_paths=report_paths,
        )
    )

    screenshot_path = output_dir / "trajectory.svg"
    write_svg(screenshot_path, solution.trajectory_states, "Boundary case: half-period CW transfer (singular-reachable Phi_rv)")
    screenshot = validate_screenshot(screenshot_path)
    result["trajectory_artifact"] = str(screenshot_path.resolve().relative_to(ROOT))
    result["trajectory_artifact_nonempty"] = screenshot.ok
    result["screenshot_source"] = "svg_fallback"

    availability = check_gmat_available(gmat_executable)
    if not availability.available:
        result["failure_mode"] = "MISSING_GMAT"
        result["verification_status"] = f"NOT VERIFIED: MISSING_GMAT: {availability.reason}"
        return result

    run = run_gmat_script(availability.executable, script_path, timeout_s=timeout_s)
    result["gmat"] = {"attempted": run.attempted, "exit_status": run.exit_status, "reason": run.reason}
    if not run.attempted or run.exit_status != 0:
        result["failure_mode"] = "EXECUTION_ERROR"
        result["verification_status"] = f"NOT VERIFIED: EXECUTION_ERROR: {run.reason}"
        return result

    final_parsed = parse_gmat_report(report_paths["final"], expect_single_row=True)
    if not final_parsed.ok:
        result["failure_mode"] = "MALFORMED_OUTPUT"
        result["verification_status"] = f"NOT VERIFIED: MALFORMED_OUTPUT: {final_parsed.reason}"
        return result
    gmat_final_state = final_parsed.states_si[0]
    result["gmat"]["final_state_m_mps"] = gmat_final_state.tolist()

    comparison = compare_gmat_final_state(
        gmat_final_state, solution.final_state, pos_tol_m=tolerances["position_m"], vel_tol_mps=tolerances["velocity_mps"],
    )
    result["comparison"] = {
        "status": comparison.status, "position_error_m": comparison.position_error_m,
        "velocity_error_mps": comparison.velocity_error_mps, "tolerances": tolerances, "reason": comparison.reason,
    }
    if comparison.status != "PASS":
        result["failure_mode"] = "NUMERICAL_DISAGREEMENT"
        result["verification_status"] = f"NOT VERIFIED: NUMERICAL_DISAGREEMENT ({comparison.status}): {comparison.reason}"
        return result

    result["verified"] = True
    result["verification_status"] = "VERIFIED"
    return result


def run_two_body_case(output_dir: Path, work_dir: Path, gmat_executable: str, timeout_s: float) -> dict:
    """Case (c): a declared point-mass coast state, cross-checked against GMAT's EarthMJ2000Eq propagator."""
    leo_radius_m = 6778000.0
    offset_m = 1_000_000.0
    duration_s = 900.0
    circular_speed = vis_viva_speed(MU_EARTH, leo_radius_m, leo_radius_m)
    chaser_radius_m = leo_radius_m + offset_m
    chaser_speed = vis_viva_speed(MU_EARTH, chaser_radius_m, chaser_radius_m)
    state0 = np.array([chaser_radius_m, 0.0, 0.0, 0.0, chaser_speed, 0.0])

    final_state = propagate_cartesian_state(state0, MU_EARTH, duration_s, steps=2000)
    result = {
        "case_id": "benchmark_case_c_two_body",
        "twobody": {
            "frame": "inertial-cartesian",
            "central_body": "Earth",
            "dynamics": "point-mass-two-body",
            "integrator": "fixed-step-rk4",
            "mu_m3_s2": MU_EARTH,
            "duration_s": duration_s,
            "steps": 2000,
            "initial_state_m_mps": state0.tolist(),
            "final_state_m_mps": final_state.tolist(),
            "reference_leo_radius_m": leo_radius_m,
            "reference_leo_circular_speed_mps": circular_speed,
        },
        "gmat": {"attempted": False},
        "comparison": {"status": None},
        "verified": False,
        "failure_mode": None,
        "verification_status": None,
    }
    tolerances = {"position_m": 1.0, "velocity_mps": 0.001}
    result["comparison"]["tolerances"] = tolerances

    script_path = work_dir / "generated_two_body_coast.script"
    final_report_path = (work_dir / "d_final.txt").resolve()
    traj_report_path = (work_dir / "d_trajectory.txt").resolve()
    x_km, y_km, z_km = (state0[:3] / 1000.0).tolist()
    vx_kms, vy_kms, vz_kms = (state0[3:] / 1000.0).tolist()
    script_path.write_text(
        f"""% Generated by scripts/generate_benchmark_gmat_evidence.py for the TJC-1.9
% CW-invalid/two-body benchmark case; units: km, km/s, seconds. Cross-checks
% src/twobody.py::propagate_cartesian_state's point-mass RK4 coast against
% GMAT's own two-body (zero-degree/order gravity field) numerical propagator
% in the inertial EarthMJ2000Eq frame -- the same frame/state convention
% src/twobody.py declares (reference/SOURCE.md Sec A.2).
Create Spacecraft Sat;
Sat.DateFormat = UTCGregorian;
Sat.Epoch = '01 Jan 2026 00:00:00.000';
Sat.CoordinateSystem = EarthMJ2000Eq;
Sat.DisplayStateType = Cartesian;
Sat.X = {x_km:.15f};
Sat.Y = {y_km:.15f};
Sat.Z = {z_km:.15f};
Sat.VX = {vx_kms:.18f};
Sat.VY = {vy_kms:.18f};
Sat.VZ = {vz_kms:.18f};

Create ForceModel FM;
FM.CentralBody = Earth;
FM.PrimaryBodies = {{Earth}};
FM.GravityField.Earth.Degree = 0;
FM.GravityField.Earth.Order = 0;

Create Propagator Prop;
Prop.FM = FM;
Prop.Type = RungeKutta4;
Prop.InitialStepSize = 1.0;
Prop.MinStep = 1.0;
Prop.MaxStep = 1.0;

Create ReportFile RFFinal RFTrajectory;
RFFinal.Filename = '{final_report_path}';
RFFinal.Precision = 16;
RFFinal.Add = {{Sat.ElapsedSecs, Sat.EarthMJ2000Eq.X, Sat.EarthMJ2000Eq.Y, Sat.EarthMJ2000Eq.Z, Sat.EarthMJ2000Eq.VX, Sat.EarthMJ2000Eq.VY, Sat.EarthMJ2000Eq.VZ}};
RFFinal.WriteReport = false;
RFTrajectory.Filename = '{traj_report_path}';
RFTrajectory.Precision = 16;
RFTrajectory.Add = {{Sat.ElapsedSecs, Sat.EarthMJ2000Eq.X, Sat.EarthMJ2000Eq.Y, Sat.EarthMJ2000Eq.Z, Sat.EarthMJ2000Eq.VX, Sat.EarthMJ2000Eq.VY, Sat.EarthMJ2000Eq.VZ}};
RFTrajectory.WriteReport = false;

BeginMissionSequence;
RFTrajectory.WriteReport = true;
Propagate Prop(Sat) {{Sat.ElapsedSecs = {duration_s:.9f}}};
RFTrajectory.WriteReport = false;
RFFinal.WriteReport = true;
Report RFFinal Sat.ElapsedSecs Sat.EarthMJ2000Eq.X Sat.EarthMJ2000Eq.Y Sat.EarthMJ2000Eq.Z Sat.EarthMJ2000Eq.VX Sat.EarthMJ2000Eq.VY Sat.EarthMJ2000Eq.VZ;
RFFinal.WriteReport = false;
"""
    )

    screenshot_path = output_dir / "trajectory.svg"
    traj_states_rel = np.array([[0.0, 0.0, 0.0], [final_state[0] - state0[0], final_state[1] - state0[1], 0.0]])
    write_svg(screenshot_path, traj_states_rel, "CW-invalid two-body coast case: inertial displacement over 900 s")
    screenshot = validate_screenshot(screenshot_path)
    result["trajectory_artifact"] = str(screenshot_path.resolve().relative_to(ROOT))
    result["trajectory_artifact_nonempty"] = screenshot.ok
    result["screenshot_source"] = "svg_fallback"

    availability = check_gmat_available(gmat_executable)
    if not availability.available:
        result["failure_mode"] = "MISSING_GMAT"
        result["verification_status"] = f"NOT VERIFIED: MISSING_GMAT: {availability.reason}"
        return result

    run = run_gmat_script(availability.executable, script_path, timeout_s=timeout_s)
    result["gmat"] = {"attempted": run.attempted, "exit_status": run.exit_status, "reason": run.reason}
    if not run.attempted or run.exit_status != 0:
        result["failure_mode"] = "EXECUTION_ERROR"
        result["verification_status"] = f"NOT VERIFIED: EXECUTION_ERROR: {run.reason}"
        return result

    # This script's own 7-column report shape (ElapsedSecs + 6 inertial
    # Cartesian components) uses GMAT's EarthMJ2000Eq frame directly, not
    # the CW-specific LVLH ReportFile shape src/gmat_verify.py::parse_gmat_report
    # expects, so it is parsed by this script's own small local parser above.
    gmat_final_state = _parse_inertial_report(final_report_path)
    if gmat_final_state is None:
        result["failure_mode"] = "MALFORMED_OUTPUT"
        result["verification_status"] = f"NOT VERIFIED: MALFORMED_OUTPUT: could not parse {final_report_path}"
        return result
    result["gmat"]["final_state_m_mps"] = gmat_final_state.tolist()

    comparison = compare_gmat_final_state(
        gmat_final_state, final_state, pos_tol_m=tolerances["position_m"], vel_tol_mps=tolerances["velocity_mps"],
    )
    result["comparison"] = {
        "status": comparison.status, "position_error_m": comparison.position_error_m,
        "velocity_error_mps": comparison.velocity_error_mps, "tolerances": tolerances, "reason": comparison.reason,
    }
    if comparison.status != "PASS":
        result["failure_mode"] = "NUMERICAL_DISAGREEMENT"
        result["verification_status"] = f"NOT VERIFIED: NUMERICAL_DISAGREEMENT ({comparison.status}): {comparison.reason}"
        return result

    result["verified"] = True
    result["verification_status"] = "VERIFIED"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gmat", default=os.environ.get("GMAT_EXECUTABLE", "GmatConsole-R2026a"))
    parser.add_argument("--timeout-s", type=float, default=180.0)
    parser.add_argument("--boundary-output-dir", type=Path, default=ROOT / "examples/benchmark_case_b_boundary")
    parser.add_argument("--two-body-output-dir", type=Path, default=ROOT / "examples/benchmark_case_c_two_body")
    args = parser.parse_args()

    args.boundary_output_dir.mkdir(parents=True, exist_ok=True)
    args.two_body_output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="tjc19_boundary_") as boundary_work_dir, \
            tempfile.TemporaryDirectory(prefix="tjc19_two_body_") as two_body_work_dir:
        boundary_result = run_boundary_case(args.boundary_output_dir, Path(boundary_work_dir), args.gmat, args.timeout_s)
        two_body_result = run_two_body_case(args.two_body_output_dir, Path(two_body_work_dir), args.gmat, args.timeout_s)

    (args.boundary_output_dir / "verification_result.json").write_text(json.dumps(boundary_result, indent=2) + "\n")
    print("boundary case:", boundary_result["verification_status"])

    (args.two_body_output_dir / "verification_result.json").write_text(json.dumps(two_body_result, indent=2) + "\n")
    print("two-body case:", two_body_result["verification_status"])

    if boundary_result["verification_status"] != "VERIFIED" or two_body_result["verification_status"] != "VERIFIED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
