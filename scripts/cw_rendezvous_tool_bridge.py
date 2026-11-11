#!/usr/bin/env python3
"""Thin CLI bridge between the ``solve_cw_rendezvous`` pi tool (TJC-23.4) and
the already-audited, deterministic ``src/cw.py`` CW targeting implementation.

This script performs NO new CW physics, no retiming, and no approximation of
its own. It only:

1. reads one structured case (the exact required inputs the retired
   ``.pi/skills/orbital-targeting-planner/SKILL.md`` documented: reference
   radius or mean motion, gravitational parameter, an explicit LVLH/RIC
   convention confirmation, initial/terminal relative states, a fixed
   positive transfer duration, and a model-selection note) as JSON from
   stdin or ``--case-json``;
2. calls ``src.cw.mean_motion`` (when a reference radius is given) and
   ``src.cw.two_burn_targeting`` with those exact inputs, unmodified; and
3. prints a structured JSON result to stdout: the two impulses and final
   state for a feasible solve, or a structured rejection (never a
   least-squares approximation) when the boundary condition is singular and
   unreachable or ``CWSingularTransferError`` is raised.

This is the Python-side half of the ``.pi/extensions/cw-rendezvous-tool`` pi
extension (TJC-23.4): the TypeScript tool's ``execute()`` shells out to this
script via ``pi.exec`` and relays its stdout JSON verbatim as the tool
result, mirroring ``scripts/gmat_tool_bridge.py``'s pattern for
``run_gmat_verification`` exactly.

Required input JSON fields:

- ``mu_m3_s2`` (float, positive gravitational parameter)
- ``lvlh_convention_confirmed`` (bool, must be ``true``; the caller confirms
  the right-handed LVLH/RIC convention -- x radial outward, y along-track in
  the chief's direction of motion, z cross-track/orbit-normal -- before any
  solve is attempted, per the retired skill's "Do not invent any missing
  input or coordinate convention" rule)
- ``initial_relative_state`` (6 floats, LVLH ``[x, y, z, x_dot, y_dot,
  z_dot]``, SI units: m, m/s)
- ``final_relative_state`` (6 floats, same convention/units)
- ``transfer_time_s`` (float, must be positive)
- ``model_selection_note`` (non-empty str: the assumption-based
  model-selection evidence that circularity, locality, duration/regime,
  frame, negligible perturbations, and impulsive-burn suitability were
  checked, per the retired skill's "Required inputs" list)

Exactly one of the following is also required:

- ``reference_radius_m`` (float, positive circular reference-orbit radius)
- ``mean_motion_rad_s`` (float, positive mean motion)

Usage::

    echo '{"mu_m3_s2": ..., ...}' | \\
        .venv/bin/python scripts/cw_rendezvous_tool_bridge.py

    .venv/bin/python scripts/cw_rendezvous_tool_bridge.py --case-json '{"mu_m3_s2": ...}'
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cw import CWSingularTransferError, mean_motion, two_burn_targeting  # noqa: E402

REQUIRED_FIELDS = (
    "mu_m3_s2",
    "lvlh_convention_confirmed",
    "initial_relative_state",
    "final_relative_state",
    "transfer_time_s",
    "model_selection_note",
)


class BridgeInputError(ValueError):
    """Raised when the structured case JSON is missing/malformed a required field.

    Kept distinct from a CW targeting rejection (singular/infeasible or
    ``CWSingularTransferError``): this is a tool-input validation error,
    caught by ``main()`` and reported as ``{"error": "..."}`` on stdout with
    a nonzero exit status, never silently treated as a CW targeting outcome.
    """


def _require_six_vector(structured_case: dict, field: str) -> list[float]:
    value = structured_case[field]
    if not isinstance(value, (list, tuple)) or len(value) != 6:
        raise BridgeInputError(f"{field} must be an array of exactly 6 numbers")
    try:
        return [float(x) for x in value]
    except (TypeError, ValueError) as exc:
        raise BridgeInputError(f"{field} must contain only numbers") from exc


def validate_case(structured_case: dict) -> dict:
    """Validate the structured case and return the exact inputs to solve with.

    No missing input or coordinate convention is invented: every field below
    is required explicitly, mirroring the retired
    ``.pi/skills/orbital-targeting-planner/SKILL.md``'s "Required inputs"
    list rather than defaulting any of them.
    """
    missing = [field for field in REQUIRED_FIELDS if field not in structured_case]
    if missing:
        raise BridgeInputError(f"missing required field(s): {missing}")

    if structured_case["lvlh_convention_confirmed"] is not True:
        raise BridgeInputError(
            "lvlh_convention_confirmed must be true: the right-handed LVLH/RIC "
            "convention (x radial outward, y along-track in the chief's direction "
            "of motion, z cross-track/orbit-normal) must be explicitly confirmed, "
            "never assumed."
        )

    if not isinstance(structured_case["model_selection_note"], str) or not structured_case["model_selection_note"].strip():
        raise BridgeInputError(
            "model_selection_note must be a non-empty string recording the "
            "assumption-based model-selection evidence (circularity, locality, "
            "duration/regime, frame, negligible perturbations, impulsive-burn "
            "suitability)."
        )

    mu = structured_case["mu_m3_s2"]
    if not isinstance(mu, (int, float)) or isinstance(mu, bool) or mu <= 0:
        raise BridgeInputError("mu_m3_s2 must be a positive number")

    transfer_time_s = structured_case["transfer_time_s"]
    if not isinstance(transfer_time_s, (int, float)) or isinstance(transfer_time_s, bool) or transfer_time_s <= 0:
        raise BridgeInputError("transfer_time_s must be a positive number")

    has_radius = "reference_radius_m" in structured_case and structured_case["reference_radius_m"] is not None
    has_mean_motion = "mean_motion_rad_s" in structured_case and structured_case["mean_motion_rad_s"] is not None
    if has_radius == has_mean_motion:
        raise BridgeInputError(
            "exactly one of reference_radius_m or mean_motion_rad_s must be provided"
        )

    if has_radius:
        reference_radius_m = structured_case["reference_radius_m"]
        if not isinstance(reference_radius_m, (int, float)) or isinstance(reference_radius_m, bool) or reference_radius_m <= 0:
            raise BridgeInputError("reference_radius_m must be a positive number")
        n = mean_motion(float(mu), float(reference_radius_m))
    else:
        mean_motion_rad_s = structured_case["mean_motion_rad_s"]
        if not isinstance(mean_motion_rad_s, (int, float)) or isinstance(mean_motion_rad_s, bool) or mean_motion_rad_s <= 0:
            raise BridgeInputError("mean_motion_rad_s must be a positive number")
        n = float(mean_motion_rad_s)

    initial_relative_state = _require_six_vector(structured_case, "initial_relative_state")
    final_relative_state = _require_six_vector(structured_case, "final_relative_state")

    return {
        "mu": float(mu),
        "n": n,
        "initial_relative_state": initial_relative_state,
        "final_relative_state": final_relative_state,
        "transfer_time_s": float(transfer_time_s),
        "model_selection_note": structured_case["model_selection_note"],
    }


def run_bridge(structured_case: dict) -> dict:
    """Run one fixed-duration two-impulse CW targeting solve and return a
    structured result dict: the two impulses and final state for a feasible
    solve, or an explicit, non-approximated rejection otherwise.
    """
    validated = validate_case(structured_case)
    state0 = np.array(validated["initial_relative_state"], dtype=float)
    target = np.array(validated["final_relative_state"], dtype=float)

    base = {
        "mean_motion_radps": validated["n"],
        "transfer_time_s": validated["transfer_time_s"],
        "model_selection_note": validated["model_selection_note"],
    }

    try:
        result = two_burn_targeting(state0, validated["n"], validated["transfer_time_s"], target)
    except CWSingularTransferError as exc:
        return {
            **base,
            "feasible": False,
            "singular": True,
            "non_unique": False,
            "status": "rejected",
            "reason": str(exc),
            "dv0_mps": None,
            "dv1_mps": None,
            "final_state": None,
        }

    if not result.feasible:
        return {
            **base,
            "feasible": False,
            "singular": result.singular,
            "non_unique": result.non_unique,
            "status": result.status,
            "reason": result.reason,
            "condition_number": result.condition_number,
            "rank": result.rank,
            "reachability_residual_m": result.reachability_residual_m,
            "dv0_mps": None,
            "dv1_mps": None,
            "final_state": None,
        }

    return {
        **base,
        "feasible": True,
        "singular": result.singular,
        "non_unique": result.non_unique,
        "status": result.status,
        "reason": result.reason,
        "condition_number": result.condition_number,
        "rank": result.rank,
        "reachability_residual_m": result.reachability_residual_m,
        "dv0_mps": result.dv0.tolist(),
        "dv1_mps": result.dv1.tolist(),
        "final_state": result.final_state.tolist(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case-json", default=None,
        help="structured case JSON (if omitted, read from stdin)",
    )
    args = parser.parse_args(argv)

    raw = args.case_json if args.case_json is not None else sys.stdin.read()
    try:
        structured_case = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"invalid JSON input: {exc}"}))
        return 2

    try:
        result = run_bridge(structured_case)
    except BridgeInputError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    print(json.dumps(result))
    return 0 if result.get("feasible") else 1


if __name__ == "__main__":
    raise SystemExit(main())
