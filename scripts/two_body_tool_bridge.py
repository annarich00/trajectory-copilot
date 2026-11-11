#!/usr/bin/env python3
"""Thin CLI bridge between the ``propagate_two_body_coast`` pi tool (TJC-23.5)
and the already-audited bounded point-mass two-body coast propagation in
``src/twobody.py``.

This script performs NO propagation, validation, or singularity-handling
logic of its own. It only:

1. reads one structured case (the same six required fields the
   ``.pi/skills/orbital-two-body-rendezvous/SKILL.md`` fallback documented:
   an initial SI inertial Cartesian state, a positive ``mu``, a finite
   coast duration, and a positive fixed RK4 step count, plus an optional
   epoch) as JSON from stdin or ``--case-json``;
2. calls ``src/twobody.py::propagate_cartesian_state`` with those exact
   inputs, unmodified; and
3. prints the final SI inertial Cartesian state plus the stable
   frame/central_body/dynamics/integrator metadata as one JSON object to
   stdout, or an explicit ``{"error": ...}`` (never an improvised result)
   when ``propagate_cartesian_state`` rejects the input -- non-finite
   values, non-positive ``mu``/``steps``, or the zero-radius point-mass
   singularity.

This is the Python-side half of the ``.pi/extensions/two-body-rendezvous-tool``
pi extension: the TypeScript tool's ``execute()`` shells out to this script
via ``pi.exec`` and relays its stdout JSON verbatim as the tool result,
rather than reimplementing any two-body propagation logic in TypeScript.

Required input JSON fields:

- ``initial_state_m_mps`` (6 floats, SI inertial Cartesian ``[x, y, z, vx, vy, vz]``)
- ``mu_m3_s2`` (float, positive gravitational parameter)
- ``duration_s`` (float, finite coast duration)
- ``steps`` (int, positive fixed RK4 step count)

Optional input JSON fields:

- ``epoch`` (str, passed through unchanged for external verification)

Usage::

    echo '{"initial_state_m_mps": [...], "mu_m3_s2": ..., "duration_s": ..., "steps": ...}' | \\
        .venv/bin/python scripts/two_body_tool_bridge.py

    .venv/bin/python scripts/two_body_tool_bridge.py --case-json '{"initial_state_m_mps": [...], ...}'
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.twobody import CENTRAL_BODY, STATE_FRAME, propagate_cartesian_state  # noqa: E402

REQUIRED_FIELDS = ("initial_state_m_mps", "mu_m3_s2", "duration_s", "steps")

DYNAMICS = "point-mass-two-body"
INTEGRATOR = "fixed-step-rk4"


class BridgeInputError(ValueError):
    """Raised when the structured case JSON is missing a required field or malformed.

    Kept distinct from a ``propagate_cartesian_state`` rejection (non-finite
    inputs, non-positive mu/steps, zero-radius singularity): this is a
    tool-input validation error, caught by ``main()`` and reported as
    ``{"error": "..."}`` on stdout with a nonzero exit status, never
    silently treated as a propagation outcome.
    """


def run_bridge(structured_case: dict) -> dict:
    """Propagate ``structured_case`` through ``propagate_cartesian_state`` and
    return the final SI inertial Cartesian state plus stable metadata.

    Raises ``BridgeInputError`` for a malformed/incomplete request shape, and
    lets ``propagate_cartesian_state``'s own ``ValueError`` (non-finite
    inputs, non-positive mu/steps, zero-radius singularity) propagate
    unchanged so ``main()`` reports it as an explicit rejection rather than
    an improvised result.
    """
    missing = [field for field in REQUIRED_FIELDS if field not in structured_case]
    if missing:
        raise BridgeInputError(f"missing required field(s): {missing}")

    initial_state = structured_case["initial_state_m_mps"]
    if not isinstance(initial_state, (list, tuple)) or len(initial_state) != 6:
        raise BridgeInputError("initial_state_m_mps must be an array of exactly 6 numbers")

    final_state = propagate_cartesian_state(
        initial_state,
        structured_case["mu_m3_s2"],
        structured_case["duration_s"],
        steps=structured_case["steps"],
    )

    return {
        "final_state_m_mps": final_state.tolist(),
        "frame": STATE_FRAME,
        "central_body": CENTRAL_BODY,
        "dynamics": DYNAMICS,
        "integrator": INTEGRATOR,
        "epoch": structured_case.get("epoch"),
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
    except (BridgeInputError, ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
