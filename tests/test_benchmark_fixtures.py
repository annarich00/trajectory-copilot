"""Schema validation for the TJC-1.9 four-category rendezvous benchmark.

Validates every fixture in ``evaluations/benchmark/`` against the required
fields in AC1-AC5 of TJC-1.9: exactly one case per required category
(straightforward CW, boundary, CW-invalid/two-body, ambiguous/incomplete),
each JSON case recording the request, expected structured problem, expected
model, a reference numerical result or expected clarification questions,
GMAT tolerances, and expected explanation behavior; the boundary case
qualifying rather than flatly passing/failing; and every fixture declaring
explicit schema/case versioning.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

BENCHMARK_DIR = Path(__file__).parents[1] / "evaluations/benchmark"

REQUIRED_CATEGORIES = {
    "straightforward_cw": "case_a_straightforward_cw.json",
    "boundary": "case_b_boundary_cw.json",
    "cw_invalid_two_body": "case_c_two_body.json",
}

VALID_SELECTIONS = (
    "CW rendezvous",
    "bounded two-body fallback",
    "UNSUPPORTED",
    "NEEDS MORE INFORMATION",
)

REQUIRED_JSON_FIXTURE_FIELDS = (
    "schema_version",
    "case_version",
    "case_id",
    "category",
    "provenance",
    "request",
    "expected_structured_problem",
    "expected_model",
    "reference_numerical_result",
    "gmat_tolerance",
    "expected_explanation_behavior",
    "solvable",
)

REQUIRED_REQUEST_FIELDS = ("natural_language", "structured_input")
REQUIRED_EXPECTED_MODEL_FIELDS = ("selection", "qualified", "deterministic_tool", "assumptions_assessed")
REQUIRED_EXPLANATION_FIELDS = ("summary", "must_state", "must_not_state")


def _load_json_fixtures() -> dict[str, dict]:
    return {
        path.name: json.loads(path.read_text())
        for path in sorted(BENCHMARK_DIR.glob("*.json"))
    }


def test_exactly_one_case_per_required_json_category():
    """AC1: at least (here, exactly) one case per solvable required category."""
    fixtures = _load_json_fixtures()
    categories = {name: data["category"] for name, data in fixtures.items()}
    for category, expected_file in REQUIRED_CATEGORIES.items():
        matching = [name for name, cat in categories.items() if cat == category]
        assert matching == [expected_file], (category, matching)


def test_ambiguous_text_fixture_exists_and_is_the_fourth_category():
    """AC1: the ambiguous/incomplete category exists in the evaluations/formalizer/ text-block style."""
    fixture = BENCHMARK_DIR / "case_d_ambiguous.txt"
    assert fixture.is_file()
    text = fixture.read_text()
    assert "CATEGORY: ambiguous_incomplete" in text
    assert "EXPECTED READINESS:\nNEEDS CLARIFICATION" in text


@pytest.mark.parametrize("fixture_name", sorted(REQUIRED_CATEGORIES.values()))
def test_json_fixture_has_required_ac2_fields(fixture_name):
    """AC2: each case records request, expected structured problem, expected
    model, a reference numerical result (or clarification questions), GMAT
    tolerance, and expected explanation behavior."""
    data = json.loads((BENCHMARK_DIR / fixture_name).read_text())
    for field in REQUIRED_JSON_FIXTURE_FIELDS:
        assert field in data, f"{fixture_name} missing required field {field!r}"
    assert isinstance(data["schema_version"], str) and data["schema_version"]
    assert isinstance(data["case_version"], int) and data["case_version"] >= 1

    request = data["request"]
    for field in REQUIRED_REQUEST_FIELDS:
        assert field in request
    assert isinstance(request["natural_language"], str) and request["natural_language"].strip()

    structured = data["expected_structured_problem"]
    assert "readiness" in structured
    assert isinstance(structured.get("blocking_issues"), list)
    assert isinstance(structured.get("clarification_questions"), list)

    model = data["expected_model"]
    for field in REQUIRED_EXPECTED_MODEL_FIELDS:
        assert field in model
    assert model["selection"] in VALID_SELECTIONS
    assert isinstance(model["qualified"], bool)
    assert isinstance(model["assumptions_assessed"], dict) and model["assumptions_assessed"]

    tolerance = data["gmat_tolerance"]
    assert isinstance(tolerance.get("position_m"), (int, float)) and tolerance["position_m"] > 0
    assert isinstance(tolerance.get("velocity_mps"), (int, float)) and tolerance["velocity_mps"] > 0

    explanation = data["expected_explanation_behavior"]
    for field in REQUIRED_EXPLANATION_FIELDS:
        assert field in explanation
    assert isinstance(explanation["must_state"], list) and explanation["must_state"]
    assert isinstance(explanation["must_not_state"], list) and explanation["must_not_state"]

    assert isinstance(data["solvable"], bool)
    if data["solvable"]:
        reference = data["reference_numerical_result"]
        assert "summary" in reference and isinstance(reference["summary"], dict)
        assert "reproducible_evidence" in data
        evidence = data["reproducible_evidence"]
        for field in ("reproduce_command", "gmat_script_reference", "verification_result_reference", "trajectory_screenshot_reference"):
            assert field in evidence and evidence[field]


def test_straightforward_cw_case_is_unqualified_and_ready():
    """AC1/AC2: the straightforward case cleanly selects CW with no boundary concerns."""
    data = json.loads((BENCHMARK_DIR / "case_a_straightforward_cw.json").read_text())
    assert data["expected_structured_problem"]["readiness"] == "READY_TO_SOLVE"
    model = data["expected_model"]
    assert model["selection"] == "CW rendezvous"
    assert model["qualified"] is False
    assert model["concerns"] == []


def test_boundary_case_is_qualified_without_inventing_a_universal_threshold():
    """AC4: the boundary case must be qualified=True with surfaced concerns,
    and must not assert a universal numeric validity threshold."""
    data = json.loads((BENCHMARK_DIR / "case_b_boundary_cw.json").read_text())
    model = data["expected_model"]
    assert model["selection"] == "CW rendezvous"
    assert model["qualified"] is True
    assert model["concerns"], "a qualified decision must surface concerns, not pass silently"
    assert "documented_borderline_assumption" in model
    note = model.get("AC4_note", "")
    assert "universal numeric validity threshold" in note


def test_two_body_case_routes_to_bounded_fallback_not_cw():
    """AC1: the CW-invalid/two-body case must route to the bounded fallback,
    not CW, and must record which assumptions were violated."""
    data = json.loads((BENCHMARK_DIR / "case_c_two_body.json").read_text())
    model = data["expected_model"]
    assert model["selection"] == "bounded two-body fallback"
    assert model["deterministic_tool"] == "src.twobody.propagate_cartesian_state"
    assumptions = model["assumptions_assessed"]
    assert assumptions["locality"] == "violated"


def test_ambiguous_case_expects_clarification_not_a_model_choice():
    """AC1/AC2: the ambiguous/incomplete case must expect NEEDS CLARIFICATION
    and NEEDS MORE INFORMATION, with no model selected."""
    text = (BENCHMARK_DIR / "case_d_ambiguous.txt").read_text()
    assert "EXPECTED READINESS:\nNEEDS CLARIFICATION" in text
    assert "Selection: NEEDS MORE INFORMATION" in text
    assert "deterministic_tool=None" in text
    for question_fragment in (
        "Which central body",
        "What circular reference-orbit altitude",
        "Which LVLH axis/sign convention",
        "complete initial relative position and velocity",
    ):
        assert question_fragment in text


def test_boundary_and_two_body_fixtures_match_live_select_model_output():
    """AC2/AC4: the recorded expected_model for cases (b)/(c) must match a
    live src.model_selector.select_model call built from each fixture's own
    recorded assumptions_assessed, not just a hand-copied value."""
    import math

    from src.cw import mean_motion
    from src.model_selector import ModelSelectionCase, select_model
    from src.twobody import vis_viva_speed

    mu = 398600441800000.0

    boundary = json.loads((BENCHMARK_DIR / "case_b_boundary_cw.json").read_text())
    radius_m = boundary["expected_structured_problem"]["reference_orbit"]["radius_m"]["value"]
    n = mean_motion(mu, radius_m)
    state0 = boundary["expected_structured_problem"]["relative_frame_and_state"]["initial_relative_position_m"]["value"] + \
        boundary["expected_structured_problem"]["relative_frame_and_state"]["initial_relative_velocity_mps"]["value"]
    transfer_s = boundary["expected_structured_problem"]["timing_and_maneuvers"]["time_of_flight_s"]["value"]
    case = ModelSelectionCase(
        circularity="supported", frame="supported", other_physics="supported", maneuver_assumptions="supported",
        reference_radius_m=radius_m, relative_separation_m=200.0, transfer_time_s=transfer_s,
        mean_motion_rad_s=n, initial_relative_state=state0,
    )
    result = select_model(case)
    assert result.selection == boundary["expected_model"]["selection"]
    assert result.qualified == boundary["expected_model"]["qualified"]
    assert result.deterministic_tool == boundary["expected_model"]["deterministic_tool"]

    two_body = json.loads((BENCHMARK_DIR / "case_c_two_body.json").read_text())
    leo_radius_m = 6778000.0
    offset_m = 1_000_000.0
    chaser_radius_m = leo_radius_m + offset_m
    chaser_speed = vis_viva_speed(mu, chaser_radius_m, chaser_radius_m)
    inertial_state = [chaser_radius_m, 0.0, 0.0, 0.0, chaser_speed, 0.0]
    case = ModelSelectionCase(
        circularity="supported", frame="supported", other_physics="violated", maneuver_assumptions="supported",
        reference_radius_m=leo_radius_m, relative_separation_m=offset_m, transfer_time_s=900.0,
        mean_motion_rad_s=math.sqrt(mu / leo_radius_m**3),
        inertial_cartesian_state=inertial_state, mu_m3_s2=mu, coast_duration_s=900.0, rk4_steps=2000,
    )
    result = select_model(case)
    assert result.selection == two_body["expected_model"]["selection"]
    assert result.deterministic_tool == two_body["expected_model"]["deterministic_tool"]


def test_committed_gmat_evidence_matches_fixture_references():
    """AC3: solvable cases' referenced GMAT script/result/screenshot files
    actually exist and are non-empty."""
    root = BENCHMARK_DIR.parents[1]
    for fixture_name in REQUIRED_CATEGORIES.values():
        data = json.loads((BENCHMARK_DIR / fixture_name).read_text())
        evidence = data["reproducible_evidence"]
        result_path = root / evidence["verification_result_reference"]
        screenshot_path = root / evidence["trajectory_screenshot_reference"]
        assert result_path.is_file() and result_path.stat().st_size > 0, result_path
        assert screenshot_path.is_file() and screenshot_path.stat().st_size > 0, screenshot_path
        result = json.loads(result_path.read_text())
        assert result.get("verified") is True, f"{fixture_name}: {result_path} is not verified"
        assert result.get("verification_status") == "VERIFIED"
