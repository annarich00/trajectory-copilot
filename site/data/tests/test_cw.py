import math

import numpy as np
import pytest
from src.cw import (
    CW_RENDEZVOUS_FRAME,
    CW_RENDEZVOUS_STATE_ORDERING,
    CW_SVD_RESIDUAL_TOLERANCE,
    CWRendezvousSolution,
    CWTargetingResult,
    cw_stm,
    mean_motion,
    solve_cw_rendezvous,
    two_burn_targeting,
    unsupported_cw_rendezvous_request,
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


def test_solve_cw_rendezvous_reproduces_audited_leo_benchmark():
    """TJC-1.15 AC1/AC4: one orchestration call reproduces test_cw_rendezvous_benchmark.

    solve_cw_rendezvous composes mean_motion -> two_burn_targeting ->
    propagate_relative_state for the same quarter-orbit LEO case audited by
    test_cw_rendezvous_benchmark, and must match it within tight tolerances.
    """
    mu = 3.986004418e14
    r0 = 6378e3 + 350e3
    n_expected = mean_motion(mu, r0)
    t_final = 0.25 * (2 * math.pi / n_expected)
    state0 = np.array([15.0, -200.0, 0.0, -0.14, 0.0, 0.0])
    direct = two_burn_targeting(state0, n_expected, t_final)

    result = solve_cw_rendezvous(mu, r0, state0, t_final, trajectory_samples=25)

    assert isinstance(result, CWRendezvousSolution)
    assert result.status == "unique"
    assert result.feasible and not result.singular and not result.non_unique
    np.testing.assert_allclose(result.mean_motion_radps, n_expected, rtol=0.0, atol=0.0)
    assert result.transfer_time_s == t_final
    # Burn components, total delta-v, and final relative state match the
    # audited direct two_burn_targeting call exactly (same deterministic path).
    np.testing.assert_allclose(result.dv0_mps, direct.dv0, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(result.dv1_mps, direct.dv1, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(result.final_state, direct.final_state, rtol=0.0, atol=0.0)
    assert result.total_delta_v_mps == pytest.approx(
        float(np.linalg.norm(direct.dv0) + np.linalg.norm(direct.dv1))
    )
    # Declared physical-plausibility tolerances from the audited benchmark.
    assert np.linalg.norm(result.dv0_mps) < 1.0
    assert np.linalg.norm(result.dv1_mps) < 1.0
    assert np.linalg.norm(result.final_state[:3]) < 1e-6
    assert np.linalg.norm(result.final_state[3:]) < 1e-6
    # Relative trajectory and time of flight.
    assert result.trajectory_times_s.shape == (25,)
    assert result.trajectory_states.shape == (25, 6)
    assert result.trajectory_times_s[0] == 0.0
    assert result.trajectory_times_s[-1] == t_final
    np.testing.assert_allclose(result.trajectory_states[0, :3], state0[:3], rtol=0.0, atol=1e-9)
    # The sampled coast arc is the post-burn-1, pre-burn-2 trajectory: its final
    # position matches the targeted final position by construction of dv0, while
    # its arrival velocity is the pre-burn-2 velocity that dv1 subsequently nulls.
    np.testing.assert_allclose(result.trajectory_states[-1, :3], result.final_state[:3], rtol=0.0, atol=1e-6)


def test_solve_cw_rendezvous_exposes_units_frame_assumptions_and_status():
    """TJC-1.15 AC2: every result exposes units, frame, assumptions, and status."""
    mu = 3.986004418e14
    r0 = 6378e3 + 350e3
    n = mean_motion(mu, r0)
    t_final = 0.25 * (2 * math.pi / n)
    state0 = np.array([15.0, -200.0, 0.0, -0.14, 0.0, 0.0])
    result = solve_cw_rendezvous(mu, r0, state0, t_final)

    assert result.frame == CW_RENDEZVOUS_FRAME
    assert result.state_ordering == CW_RENDEZVOUS_STATE_ORDERING
    assert result.dynamics
    unit_names = {name for name, _ in result.units}
    for required in ("position", "velocity", "time", "mean_motion", "delta_v", "gravitational_parameter"):
        assert required in unit_names
    assert len(result.assumptions) >= 5
    assert result.status in ("unique", "singular-reachable", "singular-infeasible")


def test_solve_cw_rendezvous_singular_infeasible_boundary_fails_explicitly():
    """TJC-1.15 AC3: an unreachable singular boundary fails explicitly, no fallback.

    No least-squares substitute is returned and the requested transfer time
    is never changed.
    """
    mu = 3.986004418e14
    n = 0.001
    r0 = (mu / n**2) ** (1.0 / 3.0)
    t_final = 2 * math.pi / n
    state0 = np.zeros(6)
    target = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    result = solve_cw_rendezvous(mu, r0, state0, t_final, target)

    assert result.status == "singular-infeasible"
    assert not result.feasible and result.singular
    assert result.transfer_time_s == t_final  # never silently retimed
    assert result.dv0_mps is None and result.dv1_mps is None
    assert result.total_delta_v_mps is None
    assert result.trajectory_times_s is None and result.trajectory_states is None
    assert result.final_state is None
    assert "outside the Phi_rv column space" in result.reason
    # Metadata is still present for a non-fabricated failure report.
    assert result.frame == CW_RENDEZVOUS_FRAME
    assert result.units
    assert result.assumptions


def test_solve_cw_rendezvous_singular_reachable_boundary_uses_svd_minimum_norm():
    """TJC-1.15 AC3: a reachable singular boundary surfaces non-unique SVD metadata."""
    mu = 3.986004418e14
    geo_radius_m = 42_164e3
    n = mean_motion(mu, geo_radius_m)
    t_final = 2 * math.pi / n
    state0 = np.array([0.0, -100e3, 0.0, 0.0, 0.0, 0.0])
    target = np.zeros(6)

    result = solve_cw_rendezvous(mu, geo_radius_m, state0, t_final, target)

    assert result.status == "singular-reachable"
    assert result.feasible and result.singular and result.non_unique
    assert result.transfer_time_s == t_final
    assert result.rank < 3
    assert result.reachability_residual_m <= CW_SVD_RESIDUAL_TOLERANCE
    np.testing.assert_allclose(result.final_state[:3], target[:3], atol=1e-6)
    assert result.dv0_mps is not None and result.dv1_mps is not None


def test_solve_cw_rendezvous_rejects_invalid_structured_inputs():
    """TJC-1.15: malformed inputs raise explicitly rather than producing a result."""
    mu = 3.986004418e14
    r0 = 6378e3 + 350e3
    state0 = np.array([15.0, -200.0, 0.0, -0.14, 0.0, 0.0])

    with pytest.raises(ValueError, match="mu must be"):
        solve_cw_rendezvous(-mu, r0, state0, 100.0)
    with pytest.raises(ValueError, match="reference_radius_m must be"):
        solve_cw_rendezvous(mu, 0.0, state0, 100.0)
    with pytest.raises(ValueError, match="t_final must be"):
        solve_cw_rendezvous(mu, r0, state0, -5.0)
    with pytest.raises(ValueError, match="t_final must be"):
        solve_cw_rendezvous(mu, r0, state0, math.nan)
    with pytest.raises(ValueError, match="trajectory_samples must be"):
        solve_cw_rendezvous(mu, r0, state0, 100.0, trajectory_samples=1)


def test_unsupported_cw_rendezvous_request_rejects_optimization_and_other_dynamics():
    """TJC-1.15 AC5: optimization/unsupported-dynamics requests are rejected, not solved."""
    for request in (
        "Minimize total delta-v over all transfer times.",
        "Produce a Pareto front of delta-v versus transfer time.",
        "Solve this rendezvous with an eccentric chief orbit.",
        "Model continuous low-thrust propulsion instead of impulsive burns.",
    ):
        result = unsupported_cw_rendezvous_request(request)
        assert result.status == "UNSUPPORTED"
        assert result.request == request
        assert result.limitation
        assert result.recommended_next_step
