import math

import numpy as np
import pytest

from src.twobody import (
    CENTRAL_BODY,
    FALLBACK_LIMITATIONS,
    STATE_FRAME,
    TwoBodyCase,
    orbital_period,
    propagate_cartesian_state,
    specific_angular_momentum,
    specific_orbital_energy,
    unsupported_request,
    vis_viva_speed,
)

MU_EARTH = 3.986004418e14
RADIUS_M = 6778e3
CIRCULAR_SPEED_MPS = math.sqrt(MU_EARTH / RADIUS_M)
CIRCULAR_STATE = np.array([RADIUS_M, 0.0, 0.0, 0.0, CIRCULAR_SPEED_MPS, 0.0])


def test_orbital_period_positive():
    assert orbital_period(MU_EARTH, RADIUS_M) > 0


def test_circular_orbit_matches_analytical_state_after_one_period():
    period_s = orbital_period(MU_EARTH, RADIUS_M)
    final_state = propagate_cartesian_state(CIRCULAR_STATE, MU_EARTH, period_s, steps=2000)
    np.testing.assert_allclose(final_state[:3], CIRCULAR_STATE[:3], atol=0.02)
    np.testing.assert_allclose(final_state[3:], CIRCULAR_STATE[3:], atol=2e-5)


def test_energy_and_angular_momentum_are_conserved_over_supported_duration():
    period_s = orbital_period(MU_EARTH, RADIUS_M)
    final_state = propagate_cartesian_state(CIRCULAR_STATE, MU_EARTH, 3.0 * period_s, steps=6000)
    assert abs(specific_orbital_energy(final_state, MU_EARTH) - specific_orbital_energy(CIRCULAR_STATE, MU_EARTH)) < 1e-3
    np.testing.assert_allclose(specific_angular_momentum(final_state), specific_angular_momentum(CIRCULAR_STATE), atol=1.0)


def test_cw_invalid_large_separation_case_has_deterministic_two_body_result():
    # A 1,000 km radial separation is not local CW proximity motion, but each
    # absolute state remains a valid point-mass coast propagation input.
    deputy_state = CIRCULAR_STATE.copy()
    deputy_state[0] += 1_000_000.0
    deputy_state[4] = vis_viva_speed(MU_EARTH, deputy_state[0], deputy_state[0])
    duration_s = 900.0
    first = propagate_cartesian_state(deputy_state, MU_EARTH, duration_s, steps=900)
    second = propagate_cartesian_state(deputy_state, MU_EARTH, duration_s, steps=900)
    np.testing.assert_array_equal(first, second)
    assert np.isfinite(first).all()


def test_like_for_like_case_metadata_is_stable_si_cartesian_contract():
    case = TwoBodyCase("circular-leo", tuple(CIRCULAR_STATE), MU_EARTH, 60.0, 200)
    assert case.frame == STATE_FRAME == "inertial-cartesian"
    assert case.central_body == CENTRAL_BODY == "Earth"
    assert case.dynamics == "point-mass-two-body"
    assert case.integrator == "fixed-step-rk4"
    assert len(case.state0_m_mps) == 6
    assert FALLBACK_LIMITATIONS


def test_unsupported_targeting_request_is_explicit():
    result = unsupported_request("Optimize a two-burn rendezvous maneuver.")
    assert result.status == "UNSUPPORTED"
    assert "does not target rendezvous" in result.limitation
    assert result.recommended_next_step


@pytest.mark.parametrize(
    ("state", "mu", "duration", "steps"),
    [
        (np.zeros(6), MU_EARTH, 60.0, 10),
        (CIRCULAR_STATE, 0.0, 60.0, 10),
        (CIRCULAR_STATE, MU_EARTH, math.nan, 10),
        (CIRCULAR_STATE, MU_EARTH, 60.0, 0),
    ],
)
def test_invalid_propagation_inputs_are_rejected(state, mu, duration, steps):
    with pytest.raises(ValueError):
        propagate_cartesian_state(state, mu, duration, steps=steps)
