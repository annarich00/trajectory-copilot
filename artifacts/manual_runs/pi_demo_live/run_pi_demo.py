#!/usr/bin/env python3
"""Self-contained, live-runnable demo script for presenting to your PI.

Runs the real, connected rendezvous pipeline (src/workflow.py::run_rendezvous_workflow)
against real installed GMAT executables -- no mocks, no monkeypatches. Three cases:

  --case one_period   The original request (one full orbital period, zero
                       terminal velocity): hits CW's singular transfer-time
                       boundary, lands NUMERICAL_DISAGREEMENT (WARNING, ~2.81 m)
                       against GMAT's full nonlinear propagation. Expected and
                       textbook; a good teaching moment, not a bug.

  --case quarter_period  The same scenario at T/4 instead of T: CW's linearized
                       prediction is accurate enough over this shorter arc to
                       pass GMAT's tolerance cleanly -- VERIFIED, with a real
                       GMAT GUI screenshot attempted by default (TJC-9).

  --case two_body      A separate, already-committed bounded two-body coast
                       case (not CW) showing src/twobody.py's own RK4
                       propagator lining up with GMAT's RungeKutta4 propagator
                       to millimeter-level agreement -- demonstrating that an
                       RK4 vs. RK4 comparison (same numerical method) agrees
                       far more tightly than CW's analytical linearization
                       vs. GMAT's full nonlinear RK4 does.

Run all three in sequence with --case all.

Usage:
    cd /home/anna_ford/projects/class_example_traj_copilot
    .venv/bin/python artifacts/manual_runs/pi_demo_live/run_pi_demo.py --case all
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.cw import mean_motion  # noqa: E402
from src.model_selector import ModelSelectionCase  # noqa: E402
from src.twobody import vis_viva_speed  # noqa: E402
from src.workflow import RendezvousCase, run_rendezvous_workflow  # noqa: E402

MU_EARTH = 398600441800000.0
R_EARTH = 6378137.0
ALT_400KM = 400000.0
LEO_RADIUS_M = R_EARTH + ALT_400KM
OUTPUT_ROOT = Path(__file__).resolve().parent / "results"


def _print_result(label: str, result) -> dict:
    data = result.to_dict()
    report = data["unified_verification_report"]
    comparison = report["comparison"] if report else None
    print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
    print(f"outcome            : {result.outcome}")
    print(f"verified           : {result.verified}")
    print(f"verification_status: {result.verification_status}")
    if comparison:
        print(f"comparison.status  : {comparison['status']}")
        print(f"position_error_m   : {comparison['position_error_m']}")
        print(f"velocity_error_mps : {comparison['velocity_error_mps']}")
    print(f"trust_statement    : {result.trust_statement}")
    print(f"screenshot_source  : {data['artifacts'].get('screenshot_source')}")
    print(f"trajectory artifact: {data['artifacts'].get('trajectory_screenshot')}")
    return data


def _cw_case(case_id: str, transfer_fraction: float) -> RendezvousCase:
    """One-thousand-metre along-track offset, zero terminal state, at
    transfer_fraction * (one orbital period)."""
    n = mean_motion(MU_EARTH, LEO_RADIUS_M)
    period = 2 * math.pi / n
    transfer_s = transfer_fraction * period
    model_case = ModelSelectionCase(
        circularity="supported", frame="supported", other_physics="supported",
        maneuver_assumptions="supported",
        reference_radius_m=LEO_RADIUS_M, relative_separation_m=1000.0,
        transfer_time_s=transfer_s, mean_motion_rad_s=n,
    )
    return RendezvousCase(
        case_id=case_id, readiness="READY_TO_SOLVE", model_selection_case=model_case,
        mu_m3_s2=MU_EARTH, reference_radius_m=LEO_RADIUS_M,
        initial_relative_state=[0.0, 1000.0, 0.0, 0.0, 0.0, 0.0],
        final_relative_state=[0.0] * 6,
        transfer_time_s=transfer_s,
        pos_tol_m=1.0, vel_tol_mps=0.001, dv_tol_mps=0.001,
    )


def _two_body_case() -> RendezvousCase:
    """A clearly CW-invalid (large/eccentric), bounded-two-body-fallback case."""
    leo_radius_m = 6778000.0
    offset_m = 1_000_000.0
    duration_s = 900.0
    chaser_radius_m = leo_radius_m + offset_m
    chaser_speed = vis_viva_speed(MU_EARTH, chaser_radius_m, chaser_radius_m)
    state0 = [chaser_radius_m, 0.0, 0.0, 0.0, chaser_speed, 0.0]
    model_case = ModelSelectionCase(
        circularity="supported", frame="supported", other_physics="violated",
        maneuver_assumptions="supported",
        reference_radius_m=leo_radius_m, relative_separation_m=offset_m,
        transfer_time_s=duration_s, mean_motion_rad_s=mean_motion(MU_EARTH, leo_radius_m),
        inertial_cartesian_state=state0, mu_m3_s2=MU_EARTH,
        coast_duration_s=duration_s, rk4_steps=2000,
    )
    return RendezvousCase(
        case_id="pi_demo_two_body_coast", readiness="READY_TO_SOLVE", model_selection_case=model_case,
        inertial_cartesian_state=state0, mu_m3_s2=MU_EARTH,
        coast_duration_s=duration_s, rk4_steps=2000,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case", choices=["one_period", "quarter_period", "two_body", "all"], default="all",
    )
    parser.add_argument("--gmat", default="GmatConsole-R2026a")
    parser.add_argument("--gmat-gui", default="GMAT-R2026a")
    parser.add_argument(
        "--no-gui-screenshot", action="store_true",
        help="Skip the real GMAT GUI screenshot attempt (faster, SVG-only).",
    )
    args = parser.parse_args()
    cases = (
        ["one_period", "quarter_period", "two_body"] if args.case == "all" else [args.case]
    )

    for name in cases:
        output_dir = OUTPUT_ROOT / name
        output_dir.mkdir(parents=True, exist_ok=True)
        if name == "one_period":
            case = _cw_case("pi_demo_one_period_cw", transfer_fraction=1.0)
            label = "CASE A: one full orbital period, zero terminal velocity (your original request)"
        elif name == "quarter_period":
            case = _cw_case("pi_demo_quarter_period_cw", transfer_fraction=0.25)
            label = "CASE B: same scenario at T/4 instead of T (clean VERIFIED comparison)"
        else:
            case = _two_body_case()
            label = "CASE C: bounded two-body RK4 coast vs. GMAT's own RK4 propagator"

        result = run_rendezvous_workflow(
            case, output_dir=output_dir,
            gmat_executable=args.gmat, gmat_gui_executable=args.gmat_gui,
            attempt_gui_screenshot=not args.no_gui_screenshot,
        )
        data = _print_result(label, result)
        (output_dir / "workflow_result.json").write_text(json.dumps(data, indent=2, default=str))

    print(f"\nAll artifacts written under: {OUTPUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
