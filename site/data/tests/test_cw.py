import math

import numpy as np
import pytest

from src.cw import (
    CWSingularTransferError,
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
    dv0, dv1, final_state = two_burn_targeting(state0, n, t_final)
    assert np.isfinite(dv0).all()
    assert np.isfinite(dv1).all()
    # Physical plausibility: delta-v magnitudes should be small and bounded,
    # consistent with a ~15-200 m proximity rendezvous (not the unbounded
    # values produced by a near-singular Phi_rv solve).
    assert np.linalg.norm(dv0) < 1.0
    assert np.linalg.norm(dv1) < 1.0
    assert np.linalg.norm(final_state[:3]) < 1e-6
    assert np.linalg.norm(final_state[3:]) < 1e-6


def test_cw_exact_one_orbit_targeting_is_rejected():
    """Exact one-orbit (n*t = 2*pi) two-impulse targeting must be rejected.

    At this transfer time, sin(n*t) ~ 0 and Phi_rv is singular/ill-
    conditioned (see reference/SOURCE.md, "Known singularities"), so
    two_burn_targeting must raise CWSingularTransferError rather than
    silently returning a least-squares pseudo-solution with unbounded,
    physically meaningless delta-v.
    """
    mu = 3.986004418e14
    r0 = 6378e3 + 350e3
    n = mean_motion(mu, r0)
    state0 = np.array([15.0, -200.0, 0.0, -0.14, 0.0, 0.0])
    with pytest.raises(CWSingularTransferError):
        two_burn_targeting(state0, n, 2 * math.pi / n)


def test_cw_validation_basic():
    mu = 3.986004418e14
    r0 = 6378e3 + 350e3
    n = mean_motion(mu, r0)
    validity = validate_cw_use(r0, np.array([15.0, -200.0, 0.0]), 6000.0, n=n)
    assert validity.valid
