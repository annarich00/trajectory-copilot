import math

import numpy as np
from src.cw import (
    CW_SVD_RESIDUAL_TOLERANCE,
    CWTargetingResult,
    cw_stm,
    mean_motion,
    two_burn_targeting,
    validate_cw_use,
)


def test_cw_stm_identity_at_zero_time():
    """The cited CW solution is identity at t=0 within double precision."""
    n = 0.00113
    np.testing.assert_allclose(cw_stm(n, 0.0), np.eye(6), rtol=0.0, atol=1e-15)


def test_cw_stm_blocks_match_cited_quarter_orbit_terms_and_units():
    """Regression mapping for all four blocks; see docs/cw-stm-audit.md."""
    n = 0.002
    t = math.pi / (2 * n)
    phi = cw_stm(n, t)
    expected_rr = np.array([[4.0, 0.0, 0.0], [6.0 * (1 - math.pi / 2), 1.0, 0.0], [0.0, 0.0, 0.0]])
    expected_rv = np.array([[1 / n, 2 / n, 0.0], [-2 / n, (4 - 3 * math.pi / 2) / n, 0.0], [0.0, 0.0, 1 / n]])
    expected_vr = np.array([[3 * n, 0.0, 0.0], [-6 * n, 0.0, 0.0], [0.0, 0.0, -n]])
    expected_vv = np.array([[0.0, 2.0, 0.0], [-2.0, -3.0, 0.0], [0.0, 0.0, 0.0]])
    np.testing.assert_allclose(phi[:3, :3], expected_rr, rtol=0.0, atol=1e-14)
    np.testing.assert_allclose(phi[:3, 3:], expected_rv, rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(phi[3:, :3], expected_vr, rtol=0.0, atol=1e-14)
    np.testing.assert_allclose(phi[3:, 3:], expected_vv, rtol=0.0, atol=1e-14)


def test_cw_rendezvous_benchmark():
    """Two-impulse CW rendezvous at a non-singular, well-conditioned transfer time.

    A quarter-orbit transfer (n*t = pi/2) keeps Phi_rv far from the known
    CW targeting singularities at n*t = k*pi (see reference/SOURCE.md,
    "Known singularities"), so the resulting delta-v is physically
    plausible rather than an artifact of a near-singular solve.
    """
    mu = 3.986004418e14
    r0 = 6378e3 + 350e3
    n = mean_motion(mu, r0)
    t_final = 0.25 * (2 * math.pi / n)  # quarter orbital period
    state0 = np.array([15.0, -200.0, 0.0, -0.14, 0.0, 0.0])
    result = two_burn_targeting(state0, n, t_final)
    assert result.status == "unique"
    assert result.feasible and not result.singular and not result.non_unique
    assert np.isfinite(result.dv0).all()
    assert np.isfinite(result.dv1).all()
    # Physical plausibility: delta-v magnitudes should be small and bounded,
    # consistent with a ~15-200 m proximity rendezvous (not the unbounded
    # values produced by a near-singular Phi_rv solve).
    assert np.linalg.norm(result.dv0) < 1.0
    assert np.linalg.norm(result.dv1) < 1.0
    assert np.linalg.norm(result.final_state[:3]) < 1e-6
    assert np.linalg.norm(result.final_state[3:]) < 1e-6


def test_cw_geo_integer_period_reachable_cases_use_minimum_norm_svd_solution():
    """Integer-period GEO targeting is reachable but non-unique for this boundary."""
    mu = 3.986004418e14
    geo_radius_m = 42_164e3
    n = mean_motion(mu, geo_radius_m)
    state0 = np.array([0.0, -100e3, 0.0, 0.0, 0.0, 0.0])
    target = np.zeros(6)
    delta_v_totals = []
    for periods in (1, 2, 3):
        result = two_burn_targeting(state0, n, periods * 2 * math.pi / n, target)
        assert result.status == "singular-reachable"
        assert result.feasible and result.singular and result.non_unique
        assert result.rank < 3
        assert result.reachability_residual_m <= CW_SVD_RESIDUAL_TOLERANCE
        np.testing.assert_allclose(result.final_state[:3], target[:3], atol=1e-6)
        delta_v_totals.append(np.linalg.norm(result.dv0) + np.linalg.norm(result.dv1))
    assert delta_v_totals[0] > delta_v_totals[1] > delta_v_totals[2]


def test_cw_integer_period_unreachable_boundary_returns_metadata_not_exception():
    """A generic boundary outside Phi_rv's column space is explicitly infeasible."""
    n = 0.001
    state0 = np.zeros(6)
    target = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    result = two_burn_targeting(state0, n, 2 * math.pi / n, target)
    assert isinstance(result, CWTargetingResult)
    assert result.status == "singular-infeasible"
    assert not result.feasible and result.singular
    assert result.dv0 is None and result.dv1 is None and result.final_state is None
    assert "outside the Phi_rv column space" in result.reason
    assert result.reachability_residual_m > 0.0


def test_cw_validation_basic():
    mu = 3.986004418e14
    r0 = 6378e3 + 350e3
    n = mean_motion(mu, r0)
    validity = validate_cw_use(r0, np.array([15.0, -200.0, 0.0]), 6000.0, n=n)
    assert validity.valid
