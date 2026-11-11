"""Tests for the ``select_rendezvous_model`` pi tool's Python bridge script
(TJC-23.3).

``scripts/model_selector_tool_bridge.py`` is the thin CLI layer the
``.pi/extensions/orbital-model-selector-tool`` pi extension shells out to: it
reads the tool's structured JSON input, constructs a
``src.model_selector.ModelSelectionCase`` from it unmodified, calls
``src.model_selector.select_model``, and serializes the resulting
``ModelSelectionResult`` back to JSON. These tests confirm that
JSON<->dataclass adaptation is faithful -- not that the model-selection
*logic* itself works differently here (that is already covered by
``tests/test_model_selector.py``, whose CW-selected/bounded-two-body-
selected/UNSUPPORTED/NEEDS-MORE-INFORMATION scenarios this module reuses
directly as its own structured-JSON inputs).

Mirrors ``tests/test_cw_rendezvous_tool_bridge.py``'s structure/conventions
for the sibling ``solve_cw_rendezvous`` bridge script.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.model_selector_tool_bridge import BridgeInputError, run_bridge  # noqa: E402

MU_EARTH = 398_600_441_800_000.0
LEO_RADIUS_M = 6_728_000.0
GEO_RADIUS_M = 42_164_000.0


def _supported_leo_case(**overrides) -> dict:
    """The same fully-supported circular-LEO case as
    ``tests/test_model_selector.py::_supported_leo_case``: all six required
    assumption items supported, selects "CW rendezvous" unqualified."""
    n = math.sqrt(MU_EARTH / LEO_RADIUS_M**3)
    period = 2 * math.pi / n
    case = {
        "circularity": "supported",
        "frame": "supported",
        "other_physics": "supported",
        "maneuver_assumptions": "supported",
        "reference_radius_m": LEO_RADIUS_M,
        "relative_separation_m": 200.0,
        "transfer_time_s": 0.25 * period,
        "mean_motion_rad_s": n,
    }
    case.update(overrides)
    return case


def _geo_two_body_case(**overrides) -> dict:
    """The same GEO-scale, large-separation case as
    ``tests/test_model_selector.py::test_clearly_unsuitable_geo_case_routes_
    to_two_body_fallback``: violates a CW assumption but fits the bounded
    two-body coast contract, selects "bounded two-body fallback"."""
    case = {
        "circularity": "supported",
        "frame": "supported",
        "other_physics": "violated",
        "maneuver_assumptions": "supported",
        "reference_radius_m": GEO_RADIUS_M,
        "relative_separation_m": 14_000_000.0,
        "transfer_time_s": 3600.0,
        "mean_motion_rad_s": 7.29e-5,
        "inertial_cartesian_state": [GEO_RADIUS_M, 0.0, 0.0, 0.0, 3074.6, 0.0],
        "mu_m3_s2": MU_EARTH,
        "coast_duration_s": 3600.0,
        "rk4_steps": 2000,
    }
    case.update(overrides)
    return case


# ---------------------------------------------------------------------------
# AC1/AC4: six-item assessment and four-way selection result.
# ---------------------------------------------------------------------------


def test_run_bridge_all_supported_case_selects_cw_rendezvous():
    result = run_bridge(_supported_leo_case())
    assert result["selection"] == "CW rendezvous"
    assert result["qualified"] is False
    assert result["deterministic_tool"] == "src.cw.two_burn_targeting"
    assert result["concerns"] == []
    for item in ("circularity", "locality", "duration_regime", "frame", "other_physics", "maneuver_assumptions"):
        assert any(item in a for a in result["assumptions"])


def test_run_bridge_two_body_contract_case_selects_bounded_two_body_fallback():
    result = run_bridge(_geo_two_body_case())
    assert result["selection"] == "bounded two-body fallback"
    assert result["qualified"] is False
    assert result["deterministic_tool"] == "src.twobody.propagate_cartesian_state"


def test_run_bridge_violated_assumption_without_two_body_contract_is_unsupported():
    case = _supported_leo_case(locality="violated")
    result = run_bridge(case)
    assert result["selection"] == "UNSUPPORTED"
    assert result["deterministic_tool"] is None
    assert any("locality" in reason for reason in result["reasons"])


def test_run_bridge_unknown_item_yields_needs_more_information():
    case = {
        "circularity": "supported",
        "frame": "unknown",
        "other_physics": "supported",
        "maneuver_assumptions": "supported",
    }
    result = run_bridge(case)
    assert result["selection"] == "NEEDS MORE INFORMATION"
    assert result["deterministic_tool"] is None
    assert "frame" in result["missing_items"]
    assert "locality" in result["missing_items"]
    assert "duration_regime" in result["missing_items"]


def test_run_bridge_output_always_includes_required_fields():
    result = run_bridge(_supported_leo_case())
    assert set(result.keys()) >= {
        "selection",
        "qualified",
        "reasons",
        "assumptions",
        "concerns",
        "deterministic_tool",
        "missing_items",
    }
    assert isinstance(result["reasons"], list)
    assert isinstance(result["assumptions"], list)
    assert isinstance(result["concerns"], list)
    assert isinstance(result["missing_items"], list)


# ---------------------------------------------------------------------------
# Unrecognized/malformed input is a tool-input error, never silently coerced.
# ---------------------------------------------------------------------------


def test_run_bridge_rejects_unrecognized_field_name():
    case = _supported_leo_case()
    case["not_a_real_field"] = "oops"
    with pytest.raises(BridgeInputError, match="unrecognized field"):
        run_bridge(case)


def test_run_bridge_rejects_invalid_assessment_literal():
    case = _supported_leo_case(circularity="definitely")
    with pytest.raises(BridgeInputError, match="circularity"):
        run_bridge(case)


# ---------------------------------------------------------------------------
# End-to-end CLI invocation, mirroring the TypeScript tool's pi.exec call.
# ---------------------------------------------------------------------------


def test_cli_prints_structured_result_json_and_exits_zero_for_cw_rendezvous():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "model_selector_tool_bridge.py")],
        input=json.dumps(_supported_leo_case()), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["selection"] == "CW rendezvous"


def test_cli_prints_structured_result_json_and_exits_zero_for_bounded_two_body():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "model_selector_tool_bridge.py")],
        input=json.dumps(_geo_two_body_case()), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["selection"] == "bounded two-body fallback"


def test_cli_exits_nonzero_for_unsupported_selection():
    case = _supported_leo_case(locality="violated")
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "model_selector_tool_bridge.py")],
        input=json.dumps(case), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 1, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["selection"] == "UNSUPPORTED"


def test_cli_exits_nonzero_for_needs_more_information():
    case = {"circularity": "supported", "frame": "unknown", "other_physics": "supported", "maneuver_assumptions": "supported"}
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "model_selector_tool_bridge.py")],
        input=json.dumps(case), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 1, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["selection"] == "NEEDS MORE INFORMATION"


def test_cli_reports_invalid_json_input_as_explicit_error_not_a_crash():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "model_selector_tool_bridge.py")],
        input="not valid json", capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert "error" in payload


def test_cli_reports_unrecognized_field_as_explicit_error_not_a_crash():
    case = _supported_leo_case()
    case["not_a_real_field"] = "oops"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "model_selector_tool_bridge.py")],
        input=json.dumps(case), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert "error" in payload
    assert "unrecognized field" in payload["error"]
