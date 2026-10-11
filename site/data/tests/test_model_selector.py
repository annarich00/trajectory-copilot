"""Tests for the assumption-based CW/two-body model selector.

Covers the acceptance criteria in TJC-1.14: evaluation of all required
assumption items, clearly-suitable and clearly-unsuitable selection,
boundary/qualified decisions that surface assumptions and verification
sensitivity, missing-information clarification instead of a model choice,
and the required output-record shape.
"""

import math

import pytest

from src.cw import mean_motion
from src.model_selector import (
    REQUIRED_ITEMS,
    ModelSelectionCase,
    ModelSelectionResult,
    select_model,
)

MU_EARTH = 398600441800000.0
LEO_RADIUS_M = 6728000.0
GEO_RADIUS_M = 42164000.0


def _supported_leo_case(**overrides) -> ModelSelectionCase:
    n = mean_motion(MU_EARTH, LEO_RADIUS_M)
    period = 2 * math.pi / n
    defaults = dict(
        circularity="supported",
        frame="supported",
        other_physics="supported",
        maneuver_assumptions="supported",
        reference_radius_m=LEO_RADIUS_M,
        relative_separation_m=200.0,
        transfer_time_s=0.25 * period,
        mean_motion_rad_s=n,
    )
    defaults.update(overrides)
    return ModelSelectionCase(**defaults)


def test_clearly_suitable_case_selects_cw_rendezvous():
    """A fully-supported local circular-LEO case selects CW, unqualified."""
    result = select_model(_supported_leo_case())
    assert result.selection == "CW rendezvous"
    assert result.qualified is False
    assert result.deterministic_tool == "src.cw.two_burn_targeting"
    assert result.concerns == ()
    for item in REQUIRED_ITEMS:
        assert any(item in a for a in result.assumptions)


def test_clearly_unsuitable_geo_case_routes_to_two_body_fallback():
    """A GEO-scale, large-separation case that fits the coast contract
    routes to the bounded two-body fallback, not CW."""
    case = ModelSelectionCase(
        circularity="supported",
        frame="supported",
        other_physics="violated",
        maneuver_assumptions="supported",
        reference_radius_m=GEO_RADIUS_M,
        relative_separation_m=14_000_000.0,
        transfer_time_s=3600.0,
        mean_motion_rad_s=7.29e-5,
        inertial_cartesian_state=[GEO_RADIUS_M, 0.0, 0.0, 0.0, 3074.6, 0.0],
        mu_m3_s2=MU_EARTH,
        coast_duration_s=3600.0,
        rk4_steps=2000,
    )
    result = select_model(case)
    assert result.selection == "bounded two-body fallback"
    assert result.qualified is False
    assert result.deterministic_tool == "src.twobody.propagate_cartesian_state"
    assert any("locality" in reason or "other_physics" in reason for reason in result.reasons)


def test_clearly_unsuitable_case_without_two_body_contract_is_unsupported():
    """A clearly CW-unsuitable case that also fails the bounded two-body
    coast contract is UNSUPPORTED, not an improvised model choice."""
    case = _supported_leo_case(locality="violated")
    result = select_model(case)
    assert result.selection == "UNSUPPORTED"
    assert result.deterministic_tool is None
    assert any("locality" in reason for reason in result.reasons)


def test_boundary_separation_returns_qualified_decision_with_concerns():
    """A boundary/ambiguous assumption produces a qualified CW decision
    that surfaces assumptions and verification sensitivity, not a silent
    pass or a flat threshold cut."""
    case = _supported_leo_case(locality="boundary")
    result = select_model(case)
    assert result.selection == "CW rendezvous"
    assert result.qualified is True
    assert result.concerns  # verification sensitivity must be visible
    assert any("verify" in concern.lower() for concern in result.concerns)
    assert any("locality" in concern for concern in result.concerns)


def test_near_singular_targeting_conditioning_qualifies_the_decision():
    """A half-period transfer makes Phi_rv singular; a reachable boundary
    makes the CW decision qualified via the targeting-conditioning signal
    alone, without a required item being individually marked boundary."""
    n = mean_motion(MU_EARTH, LEO_RADIUS_M)
    period = 2 * math.pi / n
    case = _supported_leo_case(
        transfer_time_s=period / 2,
        initial_relative_state=[15.0, -200.0, 0.0, -0.14, 0.0, 0.0],
    )
    result = select_model(case)
    assert result.selection == "CW rendezvous"
    assert result.qualified is True
    assert any("targeting_conditioning: boundary" in a for a in result.assumptions)
    assert result.concerns


def test_missing_information_yields_clarification_not_a_model_choice():
    """An unknown required assumption produces NEEDS MORE INFORMATION, with
    no model selected and no deterministic tool handoff."""
    case = ModelSelectionCase(
        circularity="supported",
        frame="unknown",
        other_physics="supported",
        maneuver_assumptions="supported",
    )
    result = select_model(case)
    assert result.selection == "NEEDS MORE INFORMATION"
    assert result.deterministic_tool is None
    assert "frame" in result.missing_items
    assert "locality" in result.missing_items
    assert "duration_regime" in result.missing_items
    assert result.reasons


def test_missing_information_surfaces_already_known_violations_as_concerns():
    """A known violation alongside missing information is surfaced as a
    concern, but still does not force a premature model selection."""
    case = ModelSelectionCase(
        circularity="violated",
        frame="unknown",
        other_physics="supported",
        maneuver_assumptions="supported",
    )
    result = select_model(case)
    assert result.selection == "NEEDS MORE INFORMATION"
    assert any("circularity" in concern for concern in result.concerns)


@pytest.mark.parametrize(
    "case",
    [
        _supported_leo_case(),
        _supported_leo_case(locality="boundary"),
        _supported_leo_case(locality="violated"),
        ModelSelectionCase(circularity="supported", frame="unknown"),
    ],
)
def test_output_shape_always_includes_required_fields(case):
    """Every outcome branch returns the required output record: selection,
    reasons, assumptions, concerns, and a deterministic tool (or None)."""
    result = select_model(case)
    assert isinstance(result, ModelSelectionResult)
    assert result.selection in (
        "CW rendezvous",
        "bounded two-body fallback",
        "UNSUPPORTED",
        "NEEDS MORE INFORMATION",
    )
    assert isinstance(result.qualified, bool)
    assert isinstance(result.reasons, tuple) and len(result.reasons) >= 1
    assert isinstance(result.assumptions, tuple) and len(result.assumptions) >= len(REQUIRED_ITEMS)
    assert isinstance(result.concerns, tuple)
    assert result.deterministic_tool is None or isinstance(result.deterministic_tool, str)
    assert isinstance(result.missing_items, tuple)
