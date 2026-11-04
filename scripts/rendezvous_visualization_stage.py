#!/usr/bin/env python3
"""Generate one TJC-16 visualization artifact for a CW rendezvous pipeline stage (TJC-16.5).

``.pi/prompts/rendezvous.md`` runs the CW GMAT step through the separate
``run_gmat_verification`` pi tool rather than ``run_rendezvous_workflow``, so
that prompt calls this CLI between its visible steps to produce and report each
artifact as soon as its stage completes:

- ``scene``: after model selection, BEFORE the GMAT-verification step;
- ``trajectory``: after the deterministic solve, BEFORE GMAT execution;
- ``comparison``: after GMAT execution/parsing, from the same ``--output-dir``
  the ``run_gmat_verification`` call wrote its ``d_trajectory.txt`` into.

This script holds no plotting or physics logic; it forwards to
``src/workflow_visualization.py`` (the same functions ``src/workflow.py::
run_rendezvous_workflow`` calls) and prints one record as JSON:
``{"stage", "status": "generated"|"not_generated", "paths", "reason"}``.

The structured case uses the same JSON fields as ``scripts/gmat_tool_bridge.py``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.gmat_tool_bridge import BridgeInputError, build_slice_case  # noqa: E402
from src.cw import solve_cw_rendezvous  # noqa: E402
from src.workflow_visualization import comparison_stage, scene_stage, trajectory_stage  # noqa: E402

import numpy as np  # noqa: E402


def _solve(slice_case: dict):
    return solve_cw_rendezvous(
        slice_case["mu"], slice_case["radius_m"], np.array(slice_case["state0"]),
        slice_case["transfer_s"], np.array(slice_case["target"]),
    )


def run_stage(stage: str, structured_case: dict, output_dir: Path, comparison_status: str) -> dict:
    slice_case = build_slice_case(structured_case)
    if stage == "scene":
        return scene_stage(slice_case["state0"], slice_case["radius_m"], output_dir)
    solution = _solve(slice_case)
    if stage == "trajectory":
        return trajectory_stage(solution, output_dir)
    return comparison_stage(
        case_id=slice_case["case_id"], solution=solution, initial_relative_state=slice_case["state0"],
        comparison_status=comparison_status, pos_tol_m=structured_case.get("pos_tol_m", 1.0),
        vel_tol_mps=structured_case.get("vel_tol_mps", 0.001),
        gmat_trajectory_report=output_dir / "d_trajectory.txt", output_dir=output_dir,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("scene", "trajectory", "comparison"))
    parser.add_argument("--case-json", required=True, help="structured case JSON (gmat_tool_bridge.py fields)")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--comparison-status", default="INCOMPLETE",
        help="comparison.status from the run_gmat_verification result (PASS/WARNING/FAIL/INCOMPLETE); comparison stage only",
    )
    args = parser.parse_args(argv)
    try:
        structured_case = json.loads(args.case_json)
        record = run_stage(args.stage, structured_case, args.output_dir, args.comparison_status)
    except (json.JSONDecodeError, BridgeInputError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
