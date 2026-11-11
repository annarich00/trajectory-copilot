#!/usr/bin/env python3
"""Thin CLI bridge between the ``select_rendezvous_model`` pi tool (TJC-23.3)
and the already-audited, deterministic ``src/model_selector.py`` combination
logic.

This script performs NO new assumption-assessment or model-selection logic
of its own. It only:

1. reads one structured case (the six required assumption items plus the
   optional supporting fields the retired
   ``.pi/skills/orbital-model-selector/SKILL.md`` documented and
   ``src.model_selector.ModelSelectionCase`` already accepts) as JSON from
   stdin or ``--case-json``;
2. constructs a ``src.model_selector.ModelSelectionCase`` from those exact
   fields, unmodified, and calls ``src.model_selector.select_model`` with
   it; and
3. prints the resulting ``ModelSelectionResult`` (selection, qualified,
   reasons, assumptions, concerns, deterministic_tool, missing_items) as one
   JSON object to stdout, unmodified.

This is the Python-side half of the
``.pi/extensions/orbital-model-selector-tool`` pi extension (TJC-23.3): the
TypeScript tool's ``execute()`` shells out to this script via ``pi.exec``
and relays its stdout JSON verbatim as the tool result, mirroring
``scripts/cw_rendezvous_tool_bridge.py``'s/``scripts/gmat_tool_bridge.py``'s
identical pattern.

Deciding each of the six assumption items' 'supported'/'violated'/
'boundary'/'unknown' value from a natural-language or formalizer-output
case is itself LLM judgment -- the calling LLM must do that reasoning (the
same judgment the retired SKILL.md asked an agent to apply free-form)
*before* calling this tool; this script never infers an assessment from
free text itself (see ``.pi/extensions/orbital-model-selector-tool/index.ts``
for the full mapping discussion).

Accepted input JSON fields exactly match
``src.model_selector.ModelSelectionCase``'s fields (all optional; a field
absent from the input keeps that dataclass field's own default):

- ``circularity``, ``frame``, ``other_physics``, ``maneuver_assumptions``
  (each ``'supported'|'violated'|'boundary'|'unknown'``, default
  ``'unknown'``)
- ``locality``, ``duration_regime``, ``targeting_conditioning`` (each
  ``'supported'|'violated'|'boundary'|'unknown'`` or omitted/``null`` to
  compute from the numeric fields below)
- ``reference_radius_m``, ``relative_separation_m`` (used to compute
  ``locality`` when it is omitted)
- ``transfer_time_s``, ``mean_motion_rad_s`` (used to compute
  ``duration_regime``, and together with the relative-state fields below,
  the optional ``targeting_conditioning`` signal)
- ``initial_relative_state``, ``final_relative_state`` (6-number arrays,
  LVLH SI units)
- ``inertial_cartesian_state`` (6-number array), ``mu_m3_s2``,
  ``coast_duration_s``, ``rk4_steps``, ``is_coast_only_request`` (bool,
  default ``true``) -- the bounded two-body coast contract fields
- ``notes`` (str)

Usage::

    echo '{"circularity": "supported", ...}' | \\
        .venv/bin/python scripts/model_selector_tool_bridge.py

    .venv/bin/python scripts/model_selector_tool_bridge.py --case-json '{"circularity": "supported", ...}'
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.model_selector import ModelSelectionCase, select_model  # noqa: E402

ALLOWED_FIELDS = {f.name for f in dataclasses.fields(ModelSelectionCase)}
ASSESSMENT_FIELDS = (
    "circularity",
    "locality",
    "duration_regime",
    "frame",
    "other_physics",
    "maneuver_assumptions",
    "targeting_conditioning",
)
VALID_ASSESSMENTS = {"supported", "violated", "boundary", "unknown"}


class BridgeInputError(ValueError):
    """Raised when the structured case JSON has an unrecognized field or an
    illegal value for a field with a fixed vocabulary.

    Kept distinct from any model-selection outcome (UNSUPPORTED, NEEDS MORE
    INFORMATION, etc.): this is a tool-input validation error, caught by
    ``main()`` and reported as ``{"error": "..."}`` on stdout with a nonzero
    exit status, never silently treated as a selection result.
    """


def _require_six_vector_or_none(structured_case: dict, field: str) -> None:
    if field not in structured_case or structured_case[field] is None:
        return
    value = structured_case[field]
    if not isinstance(value, (list, tuple)) or len(value) != 6:
        raise BridgeInputError(f"{field} must be an array of exactly 6 numbers, or omitted/null")
    try:
        [float(x) for x in value]
    except (TypeError, ValueError) as exc:
        raise BridgeInputError(f"{field} must contain only numbers") from exc


def build_case(structured_case: dict) -> ModelSelectionCase:
    """Validate the structured case and construct the exact
    ``ModelSelectionCase`` to select with. No field is invented or coerced
    beyond what ``ModelSelectionCase``'s own defaults already supply.
    """
    unrecognized = sorted(set(structured_case) - ALLOWED_FIELDS)
    if unrecognized:
        raise BridgeInputError(f"unrecognized field(s): {unrecognized}")

    for field in ASSESSMENT_FIELDS:
        if field not in structured_case or structured_case[field] is None:
            continue
        value = structured_case[field]
        if value not in VALID_ASSESSMENTS:
            raise BridgeInputError(
                f"{field} must be one of {sorted(VALID_ASSESSMENTS)} (or omitted/null), got {value!r}"
            )

    _require_six_vector_or_none(structured_case, "initial_relative_state")
    _require_six_vector_or_none(structured_case, "final_relative_state")
    _require_six_vector_or_none(structured_case, "inertial_cartesian_state")

    kwargs = {key: value for key, value in structured_case.items() if value is not None}
    return ModelSelectionCase(**kwargs)


def run_bridge(structured_case: dict) -> dict:
    """Run one deterministic model-selection combination and return
    ``select_model``'s result as a plain JSON-serializable dict.
    """
    case = build_case(structured_case)
    result = select_model(case)
    return {
        "selection": result.selection,
        "qualified": result.qualified,
        "reasons": list(result.reasons),
        "assumptions": list(result.assumptions),
        "concerns": list(result.concerns),
        "deterministic_tool": result.deterministic_tool,
        "missing_items": list(result.missing_items),
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
    return 0 if result["selection"] == "CW rendezvous" or result["selection"] == "bounded two-body fallback" else 1


if __name__ == "__main__":
    raise SystemExit(main())
