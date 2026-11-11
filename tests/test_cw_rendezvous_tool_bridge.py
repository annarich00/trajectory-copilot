"""Tests for the ``solve_cw_rendezvous`` pi tool's Python bridge script (TJC-23.4).

``scripts/cw_rendezvous_tool_bridge.py`` is the thin CLI layer the
``.pi/extensions/cw-rendezvous-tool`` pi extension shells out to: it
validates the tool's structured JSON input (the exact required inputs the
retired ``.pi/skills/orbital-targeting-planner/SKILL.md`` documented) and
calls ``src.cw.mean_motion``/``two_burn_targeting`` with those inputs
unmodified. These tests confirm that validation/dispatch is faithful and
that singular-transfer rejections are surfaced as structured rejections,
never approximated -- not that the underlying CW physics itself works
differently here (that is already covered by ``tests/test_cw.py`` and
``tests/test_cw_targeting_singularities.py``).

Mirrors ``tests/test_gmat_tool_bridge.py``'s structure/conventions for the
sibling ``run_gmat_verification`` bridge script.
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

from scripts.cw_rendezvous_tool_bridge import BridgeInputError, run_bridge, validate_case  # noqa: E402

MU_EARTH = 398_600_441_800_000.0
LEO_RADIUS_M = 6_728_000.0
GEO_RADIUS_M = 42_164_000.0


def _leo_quarter_orbit_case(**overrides) -> dict:
    """The same quarter-orbit LEO proximity case as
    ``tests/test_cw.py::test_cw_rendezvous_benchmark``: well-conditioned,
    non-singular, status == "unique"."""
    n = math.sqrt(MU_EARTH / LEO_RADIUS_M**3)
    t_final = 0.25 * (2 * math.pi / n)
    case = {
        "mu_m3_s2": MU_EARTH,
        "reference_radius_m": LEO_RADIUS_M,
        "lvlh_convention_confirmed": True,
        "initial_relative_state": [15.0, -200.0, 0.0, -0.14, 0.0, 0.0],
        "final_relative_state": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "transfer_time_s": t_final,
        "model_selection_note": (
            "Circular LEO chief, local proximity separation (<=200 m vs. "
            "~6728 km radius), quarter-orbit duration, right-handed LVLH "
            "frame, perturbations neglected, impulsive two-burn maneuver "
            "assumed suitable."
        ),
    }
    case.update(overrides)
    return case


def _geo_whole_period_unreachable_case(**overrides) -> dict:
    """The same whole-period GEO unreachable-radial-target case as
    ``tests/test_cw.py::test_cw_integer_period_unreachable_boundary_returns_
    metadata_not_exception`` / ``test_cw_targeting_singularities.py``'s
    whole-period family: status == "singular-infeasible"."""
    n = math.sqrt(MU_EARTH / GEO_RADIUS_M**3)
    t_final = 2 * math.pi / n
    case = {
        "mu_m3_s2": MU_EARTH,
        "reference_radius_m": GEO_RADIUS_M,
        "lvlh_convention_confirmed": True,
        "initial_relative_state": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "final_relative_state": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "transfer_time_s": t_final,
        "model_selection_note": (
            "Circular GEO chief, local separation, one full orbital period "
            "transfer, right-handed LVLH frame, perturbations neglected, "
            "impulsive two-burn maneuver assumed suitable -- flagged for "
            "whole-period singularity review."
        ),
    }
    case.update(overrides)
    return case


# ---------------------------------------------------------------------------
# AC1/AC4: normal two-impulse solve.
# ---------------------------------------------------------------------------


def test_validate_case_requires_structured_fields_not_free_text():
    """A case missing any required structured field is rejected explicitly,
    never silently defaulted or coerced from free text."""
    incomplete = {"mu_m3_s2": 1.0}
    with pytest.raises(BridgeInputError, match="missing required field"):
        validate_case(incomplete)


def test_validate_case_requires_explicit_lvlh_confirmation():
    case = _leo_quarter_orbit_case(lvlh_convention_confirmed=False)
    with pytest.raises(BridgeInputError, match="lvlh_convention_confirmed must be true"):
        validate_case(case)


def test_validate_case_requires_exactly_one_of_radius_or_mean_motion():
    both = _leo_quarter_orbit_case()
    both["mean_motion_rad_s"] = 0.001
    with pytest.raises(BridgeInputError, match="exactly one of"):
        validate_case(both)

    neither = _leo_quarter_orbit_case()
    del neither["reference_radius_m"]
    with pytest.raises(BridgeInputError, match="exactly one of"):
        validate_case(neither)


def test_validate_case_requires_nonempty_model_selection_note():
    case = _leo_quarter_orbit_case(model_selection_note="  ")
    with pytest.raises(BridgeInputError, match="model_selection_note"):
        validate_case(case)


def test_run_bridge_normal_two_impulse_solve_returns_both_burns_and_final_state():
    """AC1: a well-conditioned, non-singular fixed-duration transfer returns
    the two impulses and final state as a structured result."""
    result = run_bridge(_leo_quarter_orbit_case())

    assert result["feasible"] is True
    assert result["status"] == "unique"
    assert result["singular"] is False
    assert result["non_unique"] is False
    assert result["dv0_mps"] is not None and len(result["dv0_mps"]) == 3
    assert result["dv1_mps"] is not None and len(result["dv1_mps"]) == 3
    assert result["final_state"] is not None and len(result["final_state"]) == 6
    # Final state reaches the requested rendezvous target within tight tolerance.
    assert all(abs(x) < 1e-6 for x in result["final_state"][:3])
    assert all(abs(x) < 1e-6 for x in result["final_state"][3:])
    assert result["model_selection_note"] == _leo_quarter_orbit_case()["model_selection_note"]


def test_run_bridge_accepts_mean_motion_directly_instead_of_reference_radius():
    case = _leo_quarter_orbit_case()
    n = math.sqrt(MU_EARTH / LEO_RADIUS_M**3)
    del case["reference_radius_m"]
    case["mean_motion_rad_s"] = n

    result = run_bridge(case)

    assert result["feasible"] is True
    assert result["mean_motion_radps"] == n


# ---------------------------------------------------------------------------
# AC2: CWSingularTransferError / infeasible singular transfer surfaces as a
# structured rejection, never an approximation.
# ---------------------------------------------------------------------------


def test_run_bridge_rejects_unreachable_singular_transfer_without_fabricating_a_result():
    """AC2: a whole-period transfer with a boundary condition outside
    Phi_rv's column space returns a structured rejection -- no fabricated
    dv0/dv1/final_state, and status/singular reflect the actual
    infeasibility, not a least-squares substitute."""
    result = run_bridge(_geo_whole_period_unreachable_case())

    assert result["feasible"] is False
    assert result["status"] == "singular-infeasible"
    assert result["singular"] is True
    assert result["dv0_mps"] is None
    assert result["dv1_mps"] is None
    assert result["final_state"] is None
    assert "reason" in result and result["reason"]


def test_cli_prints_structured_rejection_json_and_exits_nonzero_for_infeasible(tmp_path):
    """End-to-end CLI invocation (as the TypeScript tool's ``pi.exec`` call
    will actually run it): JSON on stdin, JSON result on stdout, nonzero
    exit status for an infeasible outcome -- never a false 0/feasible."""
    case = _geo_whole_period_unreachable_case()
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "cw_rendezvous_tool_bridge.py")],
        input=json.dumps(case), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 1, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["feasible"] is False
    assert payload["status"] == "singular-infeasible"


def test_cli_prints_structured_result_json_and_exits_zero_for_feasible(tmp_path):
    case = _leo_quarter_orbit_case()
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "cw_rendezvous_tool_bridge.py")],
        input=json.dumps(case), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["feasible"] is True
    assert payload["status"] == "unique"


def test_cli_reports_invalid_json_input_as_explicit_error_not_a_crash():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "cw_rendezvous_tool_bridge.py")],
        input="not valid json", capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert "error" in payload


def test_cli_reports_missing_field_as_explicit_error_not_a_crash():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "cw_rendezvous_tool_bridge.py")],
        input=json.dumps({"mu_m3_s2": 1.0}), capture_output=True, text=True, cwd=ROOT, check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert "error" in payload
    assert "missing required field" in payload["error"]
