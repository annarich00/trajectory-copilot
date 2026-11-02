"""Hypothesis property-based tests for the CW and two-body physics core (TJC-6).

This module extends the existing example-based regression tests in
``tests/test_cw.py``, ``tests/test_twobody.py``, ``tests/test_validation.py``,
and ``tests/test_model_selector.py`` with generated-input property tests. It
does not replace or duplicate those example-based tests: each property test
below is restricted to the governing module's own documented physical
validity domain (circular/near-circular reference, finite non-degenerate
states, positive mean motion, etc.) rather than swept over arbitrary ranges,
and CW-targeting singularity/near-singular conditioning is deliberately
**excluded** here -- it is tracked separately by the linked TJC-6.1 subtask.

TJC-5 (red-then-green TDD evidence) and the project's evidence-gated
finalization convention require, per test, recorded: physical rationale,
governing equation/lecture citation, initial conditions and units, expected
result with tolerance and its justification, actual result, pass/fail, and
assumptions/limitations. Each test function's docstring below records this
explicitly; "actual result" and "pass/fail" reflect the final green run
recorded in this task's Backlog implementation notes (not reproduced inline
per-run, since Hypothesis resamples on every invocation).

Known limitation (recorded once, applies to AC4/AC8 and this whole module):
a closed-form Lagrange-coefficient (F/G/Ft/Gt, MIT 16.346 Lecture 4) two-body
oracle was considered as an additional independent reference for AC8/AC4 and
explicitly deferred. GMAT already independently checks both position and
velocity for the scoped benchmark/workflow cases this project runs
end-to-end (``src/gmat_verify.py::compare_gmat_final_state``), but this
Hypothesis sweep's own conservation checks (AC4: energy/angular-momentum)
do not, by themselves, independently establish phase/timing accuracy for
every generated case -- a propagator could in principle conserve energy and
angular momentum while still landing at the wrong point along the orbit.
AC8 partially closes this gap with an independent `scipy.integrate.solve_ivp`
(DOP853) position/velocity oracle, but a closed-form Lagrange-coefficient
check across the *full* generated domain remains undone. This is a known,
explicitly recorded limitation, not a silently closed concern.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from scipy.integrate import solve_ivp

from src.cw import CWSingularTransferError, cw_stm, mean_motion, two_burn_targeting
from src.model_selector import ModelSelectionCase, select_model
from src.twobody import (
    propagate_cartesian_state,
    specific_angular_momentum,
    specific_orbital_energy,
)
from src.verify import _absolute_to_rel_lvlh, _rel_lvlh_to_absolute

MU_EARTH = 398_600_441_800_000.0
LEO_RADIUS_M = 6_728_000.0

# Shared settings keeping the whole new module well under the "well under
# 60s" budget from the task brief while still exercising many generated
# cases per property.
_FAST = settings(max_examples=40, deadline=2000)
_SLOW_ORACLE = settings(max_examples=15, deadline=5000)


# ---------------------------------------------------------------------------
# AC2: cw_stm composition and inverse-partition identity.
# Governing source: MIT 16.346 Astrodynamics, Lectures 19 and 26 (CW/Hill
# relative-motion state-transition matrix and its block-partition inverse);
# see also docs/cw-stm-audit.md for the repository's own cited block mapping.
# ---------------------------------------------------------------------------


def _closed_form_cw_stm_inverse(n: float, t: float) -> np.ndarray:
    """Return Phi(t, t0) independently, by substituting ``-t`` *algebraically*
    into the cited block formulas (docs/cw-stm-audit.md), not by calling
    ``cw_stm(n, -t)`` -- that would make this check compare the
    implementation to itself rather than to an independently derived closed
    form. ``sin(-n*t) = -sin(n*t)`` and ``cos(-n*t) = cos(n*t)`` are applied
    by hand term-by-term; this is algebra, not code reuse.
    """
    nt = n * t
    s = math.sin(nt)
    c = math.cos(nt)
    s_neg = -s
    theta_neg = -nt
    phi_rr = np.array([
        [4 - 3 * c, 0.0, 0.0],
        [6 * (s_neg - theta_neg), 1.0, 0.0],
        [0.0, 0.0, c],
    ])
    phi_rv = np.array([
        [s_neg / n, 2 * (1 - c) / n, 0.0],
        [2 * (c - 1) / n, (4 * s_neg - 3 * theta_neg) / n, 0.0],
        [0.0, 0.0, s_neg / n],
    ])
    phi_vr = np.array([
        [3 * n * s_neg, 0.0, 0.0],
        [6 * n * (c - 1), 0.0, 0.0],
        [0.0, 0.0, -n * s_neg],
    ])
    phi_vv = np.array([
        [c, 2 * s_neg, 0.0],
        [-2 * s_neg, 4 * c - 3, 0.0],
        [0.0, 0.0, c],
    ])
    top = np.hstack([phi_rr, phi_rv])
    bottom = np.hstack([phi_vr, phi_vv])
    return np.vstack([top, bottom])


# n*t values within this distance (radians) of an integer multiple of pi are
# excluded: those are the documented CW targeting (Phi_rv) singularities
# (reference/SOURCE.md "Known singularities"; docs/cw-stm-audit.md), tracked
# separately by TJC-6.1. This STM composition/inverse property is about the
# STM itself (always invertible, det(Phi)=1 for the CW LTI system), not
# targeting feasibility, but singular-neighborhood n*t is excluded anyway to
# keep this property test's scope cleanly disjoint from TJC-6.1's.
_SINGULARITY_GUARD_RAD = 0.2


@given(
    n=st.floats(min_value=1e-4, max_value=1e-2, allow_nan=False, allow_infinity=False),
    t1=st.floats(min_value=1.0, max_value=3000.0, allow_nan=False, allow_infinity=False),
    t2=st.floats(min_value=1.0, max_value=3000.0, allow_nan=False, allow_infinity=False),
)
@_FAST
def test_cw_stm_composition_and_inverse_partition_identity(n: float, t1: float, t2: float) -> None:
    """AC2: cw_stm composition and the STM inverse-partition identity.

    Physical rationale: Phi(n, t) is the state-transition matrix of a
    linear time-invariant (LTI) system (the circular-chief CW equations),
    so semigroup composition Phi(t2)@Phi(t1) = Phi(t1+t2) and invertibility
    Phi(t, t0) = Phi(t0, t)^-1 are structural LTI-STM properties, not
    incidental numerical coincidences. Governing source: MIT 16.346 Lectures
    19 (CW/Hill relative motion, STM derivation) and 26 (STM composition and
    inverse properties for linear relative-motion systems).

    ICs/units: n in [1e-4, 1e-2] rad/s (sub-GEO through sub-LEO mean
    motion), t1, t2 in [1, 3000] s, SI throughout. n*t1, n*t2, and
    n*(t1+t2) are each kept at least 0.2 rad away from an integer multiple
    of pi, away from the documented CW targeting singularities
    (reference/SOURCE.md), which are this STM's own structural feature, not
    a defect, and are scoped to TJC-6.1 instead.

    Expected result/tolerance: both residuals at or below 1e-9 absolute in
    the max-norm of the 6x6 matrix difference. Justification: exploration
    found residuals of order 1e-12 to 1e-13 relative for this closed-form
    trigonometric STM in double precision; 1e-9 leaves comfortable margin
    for the generated range without being a razor-thin, flaky threshold.

    Assumptions/limitations: circular-chief CW only (this module's own
    stated scope); this property does not re-validate targeting feasibility
    or conditioning (TJC-6.1's scope).
    """
    for theta in (n * t1, n * t2, n * (t1 + t2)):
        rem = theta % math.pi
        assume(rem > _SINGULARITY_GUARD_RAD and rem < math.pi - _SINGULARITY_GUARD_RAD)

    phi_t1 = cw_stm(n, t1)
    phi_t2 = cw_stm(n, t2)
    phi_sum = cw_stm(n, t1 + t2)

    composed = phi_t2 @ phi_t1
    np.testing.assert_allclose(composed, phi_sum, rtol=0.0, atol=1e-9)

    phi_forward = cw_stm(n, t1)
    phi_inverse_closed_form = _closed_form_cw_stm_inverse(n, t1)
    identity_check = phi_forward @ phi_inverse_closed_form
    np.testing.assert_allclose(identity_check, np.eye(6), rtol=0.0, atol=1e-9)


# ---------------------------------------------------------------------------
# AC3: dedicated symplectic property test.
# Governing source: MIT 16.346 Lecture 19 (CW rotating-frame Lagrangian and
# canonical structure of relative motion).
# ---------------------------------------------------------------------------


def _canonical_momentum_transform(n: float) -> np.ndarray:
    """Return T mapping [x, y, z, xdot, ydot, zdot] -> [x, y, z, px, py, pz].

    Derivation (Euler-Lagrange on the CW rotating-frame Lagrangian):
    L = (1/2)[(xdot - n*y)^2 + (ydot + n*x)^2 + zdot^2] - V(x, y, z), where
    the rotating-frame kinetic term already includes the Coriolis/transport
    cross terms from a frame rotating at rate n about z (the cross-track
    axis), consistent with this repository's z = cross-track, y =
    along-track convention (reference/SOURCE.md Sec A.1; src/cw.py
    docstring). The canonical momenta are:
        p_x = dL/d(xdot) = xdot - n*y
        p_y = dL/d(ydot) = ydot + n*x
        p_z = dL/d(zdot) = zdot
    These match the state ordering [x, y, z, xdot, ydot, zdot] with no
    unexplained sign flip: the sign on the y-term in p_x and the x-term in
    p_y both come directly from differentiating the same quadratic
    rotating-frame kinetic energy, and both carry the same +n sense as the
    frame's rotation rate used to build Phi(n, t).
    """
    t_matrix = np.eye(6)
    t_matrix[3, 1] = -n  # p_x = xdot - n*y
    t_matrix[4, 0] = n  # p_y = ydot + n*x
    return t_matrix


_CANONICAL_J = np.block([
    [np.zeros((3, 3)), np.eye(3)],
    [-np.eye(3), np.zeros((3, 3))],
])


@given(
    n=st.floats(min_value=1e-4, max_value=1e-2, allow_nan=False, allow_infinity=False),
    t=st.floats(min_value=1.0, max_value=5000.0, allow_nan=False, allow_infinity=False),
)
@_FAST
def test_cw_stm_symplectic_property_in_canonical_momentum_coordinates(n: float, t: float) -> None:
    """AC3: Phi_w = T @ Phi @ T^-1 is symplectic (Phi_w^T J Phi_w = J); the raw
    position/velocity STM is NOT.

    Physical rationale: the CW/Hill relative-motion dynamics derive from a
    Hamiltonian system in canonical (position, momentum) coordinates; the
    flow map of any such system is symplectic with respect to the canonical
    J. ``cw_stm`` returns the STM in raw position/velocity coordinates
    [x, y, z, xdot, ydot, zdot], which are *not* canonical because the
    rotating-frame kinetic energy's Coriolis cross term ties velocity to
    position (see T's off-diagonal n terms above): differentiating velocity
    does not directly give a canonical momentum until that Coriolis term is
    removed by the T transform. This is why AC3(d) explicitly expects the
    raw STM to fail J-preservation while the T-transformed STM passes it.
    Governing source: MIT 16.346 Lecture 19.

    (a)/(b): see ``_canonical_momentum_transform`` docstring for the
    Euler-Lagrange derivation of T and its state-ordering/sign consistency
    with this repository's [x, y, z, xdot, ydot, zdot] convention; T and
    Phi(n, t) use the same n in the same generated case, built below.

    (c) ICs/units: n in [1e-4, 1e-2] rad/s, t in [1, 5000] s, SI.
    Expected result/tolerance: ||Phi_w^T J Phi_w - J||_max <= 1e-8.
    Justification: exploration observed deviations of order 1e-12 to 1e-13
    for this closed-form trigonometric STM; 1e-8 leaves ample margin without
    being razor-thin.

    (d) Documented reason the RAW STM is not expected to be symplectic:
    Coriolis coupling (the n*x, n*y cross terms) makes velocity and
    canonical momentum different quantities in a rotating frame; applying J
    directly to raw velocity-ordered coordinates tests the wrong canonical
    structure. Exploration confirmed this by measuring the raw STM's own
    deviation from J, which is asserted explicitly below as part of this
    test (not merely described in prose) and was observed to be of order
    10^1-10^2 or larger in max-norm once n*t exceeds about 0.5 rad (excluded
    below only because the raw STM is still close to the trivially-
    symplectic identity for very small n*t, not because the claim is
    n*t-dependent) -- i.e., genuinely not symplectic, not merely slightly
    off due to floating point.

    Assumptions/limitations: circular-chief CW only; this is a structural
    canonical-transform property, independent of targeting singularities
    (TJC-6.1's separate scope); AC3(d)'s own raw-deviation assertion
    additionally excludes n*t <= 0.5 rad (near-identity STM) via
    ``assume``, which does not narrow AC3(a)-(c)'s scope.
    """
    phi = cw_stm(n, t)
    t_matrix = _canonical_momentum_transform(n)
    t_inverse = np.linalg.inv(t_matrix)
    phi_canonical = t_matrix @ phi @ t_inverse

    transformed_deviation = phi_canonical.T @ _CANONICAL_J @ phi_canonical - _CANONICAL_J
    np.testing.assert_allclose(transformed_deviation, np.zeros((6, 6)), rtol=0.0, atol=1e-8)

    # AC3(d): the untransformed STM is genuinely non-symplectic in raw
    # position/velocity coordinates away from t=0 (where Phi is trivially
    # the identity, and the identity is itself always symplectic) -- assert
    # this is large, not merely "not exactly zero" from floating point
    # noise. n*t < 0.5 rad is excluded because the raw STM is still close
    # to identity there and the deviation has not yet grown large; this
    # does not weaken the property, since AC3(d)'s claim is about the
    # generic non-canonical behavior of the raw STM, not about t=0.
    assume(n * t > 0.5)
    raw_deviation = phi.T @ _CANONICAL_J @ phi - _CANONICAL_J
    assert np.abs(raw_deviation).max() > 1.0


# ---------------------------------------------------------------------------
# AC4: two-body conservation of specific orbital energy and angular momentum.
# Governing source: MIT 16.346 Lectures 1 and 2 (two-body problem, energy and
# angular-momentum integrals of motion).
# ---------------------------------------------------------------------------


def _random_bound_two_body_state(mu: float, radius_m: float, speed_fraction: float, direction: np.ndarray) -> np.ndarray:
    r_hat = direction / np.linalg.norm(direction)
    r_vec = r_hat * radius_m
    v_circular = math.sqrt(mu / radius_m)
    v_vec = (direction[::-1] + 1.0) * speed_fraction * v_circular
    # Re-derive a clean, non-degenerate velocity direction that is not
    # collinear with r_vec (collinear velocity still integrates fine, so no
    # exclusion is physically required -- this is only to avoid a
    # degenerate rectilinear orbit not representative of the AC4 sweep).
    v_dir = np.cross(direction, np.array([1.0, 0.0, 0.0]))
    if np.linalg.norm(v_dir) < 1e-6:
        v_dir = np.cross(direction, np.array([0.0, 1.0, 0.0]))
    v_dir = v_dir / np.linalg.norm(v_dir)
    v_vec = v_dir * v_circular * speed_fraction
    return np.hstack([r_vec, v_vec])


@given(
    mu=st.floats(min_value=1e13, max_value=1e15, allow_nan=False, allow_infinity=False),
    radius_m=st.floats(min_value=5e6, max_value=5e7, allow_nan=False, allow_infinity=False),
    speed_fraction=st.floats(min_value=0.5, max_value=1.3, allow_nan=False, allow_infinity=False),
    direction=st.tuples(
        st.floats(min_value=-1.0, max_value=1.0),
        st.floats(min_value=-1.0, max_value=1.0),
        st.floats(min_value=-1.0, max_value=1.0),
    ).filter(lambda d: np.linalg.norm(d) > 0.2),
    dt=st.floats(min_value=10.0, max_value=3000.0, allow_nan=False, allow_infinity=False),
)
@_FAST
def test_two_body_propagation_conserves_energy_and_angular_momentum(
    mu: float, radius_m: float, speed_fraction: float, direction: tuple, dt: float
) -> None:
    """AC4: propagate_cartesian_state conserves specific orbital energy and
    specific angular momentum across generated valid two-body cases.

    Physical rationale: for an unperturbed point-mass two-body system,
    specific orbital energy ``eps = v^2/2 - mu/r`` and specific angular
    momentum ``h = r x v`` are exact integrals of motion (Kepler's
    first-integral results). A numerically-integrated trajectory that
    conserves both to high relative precision is consistent with correctly
    implementing the two-body acceleration law, not merely a specific
    hand-picked circular-LEO case. Governing source: MIT 16.346 Lectures 1
    (two-body equations of motion) and 2 (energy and angular-momentum
    integrals).

    ICs/units: mu in [1e13, 1e15] m^3/s^2 (sub-lunar through super-Earth
    scale), radius_m in [5e6, 5e7] m, speed_fraction in [0.5, 1.3] (fraction
    of local circular speed, covering both bound ellipse and some weakly
    hyperbolic cases), dt in [10, 3000] s, SI throughout. direction is a
    generated unit vector for r0 (filtered away from the zero vector).

    Expected result/tolerance: relative energy error <= 1e-6 and relative
    angular-momentum error <= 1e-6, at steps=4000 (matches exploration's
    confirmed step count). Justification: exploration observed errors of
    order 1e-9 to 1e-13 across this exact generated domain at 4000 RK4
    steps; 1e-6 is conservative margin chosen to avoid flakiness from
    Hypothesis's wider example coverage while still being far tighter than
    any plausible implementation defect would produce.

    Assumptions/limitations: point-mass central gravity only (src/twobody.py
    docstring); this conservation check does not independently establish
    phase/timing accuracy for every generated case (see module-level
    docstring's deferred Lagrange-coefficient-oracle note) -- AC8 below
    partially covers that gap via an independent position/velocity oracle.
    """
    state0 = _random_bound_two_body_state(mu, radius_m, speed_fraction, np.array(direction))
    energy0 = specific_orbital_energy(state0, mu)
    h0 = specific_angular_momentum(state0)

    state_f = propagate_cartesian_state(state0, mu, dt, steps=4000)
    energy_f = specific_orbital_energy(state_f, mu)
    h_f = specific_angular_momentum(state_f)

    energy_scale = max(1.0, abs(energy0))
    h_scale = max(1.0, float(np.linalg.norm(h0)))
    assert abs(energy_f - energy0) / energy_scale <= 1e-6
    assert float(np.linalg.norm(h_f - h0)) / h_scale <= 1e-6


# ---------------------------------------------------------------------------
# AC5: src.verify LVLH-inertial round-trip property.
# ---------------------------------------------------------------------------


@given(
    chief_radius_m=st.floats(min_value=6.6e6, max_value=4.3e7, allow_nan=False, allow_infinity=False),
    chief_pos_dir=st.tuples(
        st.floats(min_value=-1.0, max_value=1.0),
        st.floats(min_value=-1.0, max_value=1.0),
        st.floats(min_value=-1.0, max_value=1.0),
    ).filter(lambda d: np.linalg.norm(d) > 0.2),
    chief_vel_dir=st.tuples(
        st.floats(min_value=-1.0, max_value=1.0),
        st.floats(min_value=-1.0, max_value=1.0),
        st.floats(min_value=-1.0, max_value=1.0),
    ).filter(lambda d: np.linalg.norm(d) > 0.2),
    chief_speed_mps=st.floats(min_value=1000.0, max_value=9000.0, allow_nan=False, allow_infinity=False),
    n=st.floats(min_value=1e-4, max_value=1e-2, allow_nan=False, allow_infinity=False),
    rel_pos_m=st.tuples(
        st.floats(min_value=-5000.0, max_value=5000.0),
        st.floats(min_value=-5000.0, max_value=5000.0),
        st.floats(min_value=-5000.0, max_value=5000.0),
    ),
    rel_vel_mps=st.tuples(
        st.floats(min_value=-5.0, max_value=5.0),
        st.floats(min_value=-5.0, max_value=5.0),
        st.floats(min_value=-5.0, max_value=5.0),
    ),
)
@_FAST
def test_lvlh_inertial_round_trip_holds_for_generated_nondegenerate_states(
    chief_radius_m, chief_pos_dir, chief_vel_dir, chief_speed_mps, n, rel_pos_m, rel_vel_mps
) -> None:
    """AC5: _absolute_to_rel_lvlh(_rel_lvlh_to_absolute(...)) round-trips the
    relative LVLH state, across generated non-degenerate chief/relative
    states (not only the single fixed example in tests/test_validation.py).

    Physical rationale: _rel_lvlh_to_absolute and _absolute_to_rel_lvlh are
    meant to be exact inverses of each other (rotation into/out of the
    chief's LVLH frame plus the rotating-frame transport-term correction);
    this is a basic self-consistency requirement for any verification
    pipeline that moves between CW-relative and inertial representations
    (src/verify.py::validate_against_two_body depends on this).

    ICs/units: chief position/velocity directions are generated unit-like
    vectors (filtered away from the zero vector) scaled to a chief radius in
    [6.6e6, 4.3e7] m (sub-LEO to super-GEO) and chief speed in
    [1000, 9000] m/s; chief position and velocity directions are generated
    independently, so most generated cases are non-collinear (the rare
    near-collinear draws, where chief_pos and chief_vel are degenerate for
    defining the LVLH frame, are excluded via ``assume``, matching
    _lvlh_basis's own documented precondition). n in [1e-4, 1e-2] rad/s.
    rel_pos_m in [-5000, 5000] m per axis, rel_vel_mps in [-5, 5] m/s per
    axis (local relative-motion scale, consistent with this module's LVLH
    contract). SI units throughout.

    Expected result/tolerance: round-trip absolute error <= 1e-6 (position,
    m) and <= 1e-9 (velocity, m/s). Justification: exploration observed
    round-trip errors up to ~3.7e-9 (max-norm, mixed position/velocity
    scale) across this generated domain; separate position/velocity
    tolerances at these levels leave comfortable margin given the up-to-
    4.3e7 m position scale involved (dominating any absolute floating-point
    tolerance), while still being far tighter than any plausible
    inverse-transform defect.

    Assumptions/limitations: requires non-degenerate chief position/velocity
    (nonzero, non-collinear) -- degenerate inputs are explicitly rejected by
    _lvlh_basis with LVLHTransformationError and are covered by the existing
    example-based test, not this property.
    """
    chief_pos = np.array(chief_pos_dir) / np.linalg.norm(chief_pos_dir) * chief_radius_m
    chief_vel_direction = np.array(chief_vel_dir) / np.linalg.norm(chief_vel_dir)
    chief_vel = chief_vel_direction * chief_speed_mps
    assume(float(np.linalg.norm(np.cross(chief_pos, chief_vel))) > 1e3)

    relative_state = np.hstack([rel_pos_m, rel_vel_mps])
    deputy_pos, deputy_vel = _rel_lvlh_to_absolute(chief_pos, chief_vel, relative_state, n)
    recovered = _absolute_to_rel_lvlh(chief_pos, chief_vel, deputy_pos, deputy_vel, n)

    np.testing.assert_allclose(recovered[:3], relative_state[:3], rtol=0.0, atol=1e-6)
    np.testing.assert_allclose(recovered[3:], relative_state[3:], rtol=0.0, atol=1e-9)


# ---------------------------------------------------------------------------
# AC6: two_burn_targeting final-state-matches-target property, excluding
# singular/near-singular cases (which are TJC-6.1's scope).
# ---------------------------------------------------------------------------


@given(
    radius_m=st.floats(min_value=6.6e6, max_value=4.3e7, allow_nan=False, allow_infinity=False),
    t_final=st.floats(min_value=60.0, max_value=20000.0, allow_nan=False, allow_infinity=False),
    state0=st.tuples(*([st.floats(min_value=-1000.0, max_value=1000.0)] * 3 + [st.floats(min_value=-1.0, max_value=1.0)] * 3)),
    target=st.tuples(*([st.floats(min_value=-1000.0, max_value=1000.0)] * 3 + [st.floats(min_value=-1.0, max_value=1.0)] * 3)),
)
@_FAST
def test_two_burn_targeting_reaches_target_for_nonsingular_transfers(
    radius_m: float, t_final: float, state0: tuple, target: tuple
) -> None:
    """AC6: two_burn_targeting's returned final relative state matches the
    requested target to numerical tolerance, for generated non-singular
    (n, t_final, state0, target) combinations.

    Physical rationale: two_burn_targeting's "unique" solution branch solves
    the fixed-duration two-impulse CW boundary-value problem exactly (up to
    floating point), by construction of the linear STM solve
    (src/cw.py::two_burn_targeting, Phi_rv v0+ = b); a property test that the
    returned final_state matches the requested target confirms this holds
    broadly, not only at the single hand-picked quarter-orbit case in
    tests/test_cw.py::test_cw_rendezvous_benchmark.

    This property explicitly EXCLUDES singular/near-singular transfer
    times: those are intentionally the responsibility of the linked TJC-6.1
    subtask ("Add CW targeting singularity and conditioning property
    coverage"), not this one. n*t_final within 0.3 rad of an integer
    multiple of pi (the documented Phi_rv singularity locations;
    reference/SOURCE.md "Known singularities") is skipped via ``assume``,
    and any non-"unique" targeting status (singular-reachable or
    singular-infeasible) causes the generated example to be discarded via
    ``assume`` as well, so this test only exercises -- and only asserts
    about -- the well-conditioned unique-solution branch.

    ICs/units: radius_m in [6.6e6, 4.3e7] m (used with MU_EARTH to derive a
    circular mean motion n), t_final in [60, 20000] s, state0/target
    position components in [-1000, 1000] m, velocity components in [-1, 1]
    m/s -- a local proximity-operations scale consistent with this module's
    CW linearization assumptions (reference/SOURCE.md Sec B.1). SI
    throughout.

    Expected result/tolerance: ||final_state - target||_max <= 1e-6 (mixed
    position-m/velocity-m/s scale). Justification: two_burn_targeting's
    unique branch is an exact linear-algebra solve of the same STM used to
    compute final_state, so the only expected residual is floating-point
    roundoff; exploration observed no case exceeding this bound across
    thousands of generated non-singular samples.

    Assumptions/limitations: circular-chief CW only; excludes singular/
    near-singular transfer times by design (TJC-6.1's scope, not
    duplicated or substituted here).
    """
    n = mean_motion(MU_EARTH, radius_m)
    theta = n * t_final
    rem = theta % math.pi
    assume(rem > 0.3 and rem < math.pi - 0.3)

    state0_arr = np.array(state0, dtype=float)
    target_arr = np.array(target, dtype=float)

    try:
        result = two_burn_targeting(state0_arr, n, t_final, target_arr)
    except CWSingularTransferError:
        assume(False)
        return
    assume(result.status == "unique")

    np.testing.assert_allclose(result.final_state, target_arr, rtol=0.0, atol=1e-6)


# ---------------------------------------------------------------------------
# AC7: model_selector.select_model monotonicity over relative_separation_m.
# ---------------------------------------------------------------------------


def _leo_case_with_separation(separation_m: float) -> ModelSelectionCase:
    n = mean_motion(MU_EARTH, LEO_RADIUS_M)
    period = 2 * math.pi / n
    return ModelSelectionCase(
        circularity="supported",
        frame="supported",
        other_physics="supported",
        maneuver_assumptions="supported",
        reference_radius_m=LEO_RADIUS_M,
        relative_separation_m=separation_m,
        transfer_time_s=0.25 * period,
        mean_motion_rad_s=n,
    )


# "CW rendezvous" is the clearly-local outcome, "UNSUPPORTED" the clearly-
# nonlocal one for this fixed held-supported case (see
# tests/test_model_selector.py's analogous fixtures); monotonic means the
# sweep visits "CW rendezvous" first, then transitions at most once to
# "UNSUPPORTED", never oscillating back.
_SELECTION_RANK = {"CW rendezvous": 0, "UNSUPPORTED": 1}


@given(
    separations_m=st.lists(
        st.floats(min_value=1.0, max_value=6.7e6, allow_nan=False, allow_infinity=False),
        min_size=5,
        max_size=15,
    )
)
@_FAST
def test_model_selection_is_monotonic_in_relative_separation(separations_m: list) -> None:
    """AC7: select_model's selection is monotonic (non-oscillating) as
    relative_separation_m increases, holding all other required assumption
    items supported.

    Physical rationale: relative_separation_m vs. reference_radius_m is a
    single scalar locality signal (src/model_selector.py's _separation_signal,
    backed by src/cw.py::validate_cw_use's 1% separation-ratio heuristic); a
    selector built on a monotonic numeric threshold applied to a single
    increasing input should never transition from the "local" outcome to
    the "nonlocal" outcome and back again as that one input increases,
    while every other required assumption item is held fixed at
    "supported". Oscillation would indicate a selection-logic defect (e.g.
    an unintended interaction with floating-point formatting of the
    separation value), not a property of the physical heuristic itself.

    ICs/units: relative_separation_m values are generated in [1, 6.7e6] m
    (sub-meter-scale proximity operations through Earth-radius scale), with
    reference_radius_m fixed at LEO_RADIUS_M = 6,728,000 m and transfer_time_s
    fixed at a quarter orbital period -- matching this project's existing
    test_model_selector.py LEO fixture convention. All other required
    assumption items (circularity, frame, other_physics,
    maneuver_assumptions) are held "supported".

    Expected result/tolerance: after sorting the generated separations
    ascending and mapping each selection outcome to a rank (0 = "CW
    rendezvous", 1 = "UNSUPPORTED"), the rank sequence is non-decreasing.
    This is an exact/discrete property (no numeric tolerance applies).
    Justification: exploration spot-checked a dense geometric sweep from 1 m
    to 6.7e6 m and always found exactly one "CW rendezvous" -> "UNSUPPORTED"
    transition with no oscillation.

    Assumptions/limitations: "boundary"/"qualified" selection outcomes are
    possible in general (see test_model_selector.py's boundary test) but do
    not arise for this specific held-supported LEO fixture across the
    generated separation range, since _separation_signal only returns
    "supported" or "violated" (no "boundary" branch) -- confirmed by
    inspection of src/model_selector.py::_separation_signal.
    """
    sorted_separations = sorted(separations_m)
    ranks = [
        _SELECTION_RANK[select_model(_leo_case_with_separation(sep)).selection]
        for sep in sorted_separations
    ]
    assert ranks == sorted(ranks)


# ---------------------------------------------------------------------------
# AC8: RK4 global-error convergence order vs. an independent scipy oracle.
# Governing source: MIT 16.346 Lecture 33 (numerical integration accuracy
# and convergence order for orbital propagation).
# ---------------------------------------------------------------------------


def _solve_ivp_two_body_oracle(state0: np.ndarray, mu: float, dt: float) -> np.ndarray:
    """Independent high-accuracy two-body reference via scipy's adaptive
    DOP853 integrator (8th-order Runge-Kutta with error control), used as
    the oracle this test's RK4 implementation is checked against -- not a
    finer run of the same RK4 code."""

    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        r = y[:3]
        v = y[3:]
        a = -mu * r / np.linalg.norm(r) ** 3
        return np.hstack([v, a])

    solution = solve_ivp(rhs, (0.0, dt), state0, method="DOP853", rtol=1e-13, atol=1e-13)
    return solution.y[:, -1]


@given(
    mu=st.floats(min_value=1e13, max_value=1e15, allow_nan=False, allow_infinity=False),
    radius_m=st.floats(min_value=5e6, max_value=5e7, allow_nan=False, allow_infinity=False),
    speed_fraction=st.floats(min_value=0.85, max_value=1.15, allow_nan=False, allow_infinity=False),
    direction=st.tuples(
        st.floats(min_value=-1.0, max_value=1.0),
        st.floats(min_value=-1.0, max_value=1.0),
        st.floats(min_value=-1.0, max_value=1.0),
    ).filter(lambda d: np.linalg.norm(d) > 0.2),
    period_fraction=st.floats(min_value=0.05, max_value=0.2, allow_nan=False, allow_infinity=False),
)
@_SLOW_ORACLE
def test_rk4_global_error_converges_at_approximately_fourth_order(
    mu: float, radius_m: float, speed_fraction: float, direction: tuple, period_fraction: float
) -> None:
    """AC8: RK4 (propagate_cartesian_state) global-error convergence order,
    checked against an independent scipy.integrate.solve_ivp (DOP853)
    reference, not a finer run of the same RK4 implementation.

    Physical rationale: classical fixed-step RK4's global truncation error
    scales as O(h^4) for smooth right-hand sides such as the two-body
    acceleration law (away from near-singular close approaches); halving the
    step size h should reduce the global error by a factor of approximately
    2^4 = 16, i.e. an observed convergence order near 4. Governing source:
    MIT 16.346 Lecture 33 (numerical integration accuracy/convergence order).

    ICs/units: mu in [1e13, 1e15] m^3/s^2, radius_m in [5e6, 5e7] m,
    speed_fraction in [0.85, 1.15] of local circular speed (kept close to
    circular so dt as a period_fraction maps to a well-behaved, non-near-
    singular arc), period_fraction in [0.05, 0.2] of the orbital period
    (dt is derived from the osculating bound orbit's own period so the
    propagated arc length is physically comparable across very different mu
    /radius draws). direction is a generated unit-like vector (filtered
    away from zero) for r0. SI throughout. Cases where the generated
    (mu, radius_m, speed_fraction) combination is not bound (specific
    energy >= 0, i.e. escape/parabolic) are skipped via ``assume``, since
    "orbital period" is undefined for them and this test's RK4-vs-h/2
    convergence-order property does not depend on boundedness anyway --
    excluding them just keeps the generated dt physically well-scaled.

    Expected result/tolerance: observed order = log2(err_h / err_h2) in
    [3.0, 5.0], where err_h/err_h2 are position-error norms at steps=60 and
    steps=120 against the DOP853 oracle. Justification: exploration swept
    this exact generated domain (mu, radius, near-circular speed_fraction,
    dt as a small period fraction, steps=60) and consistently found orders
    in roughly [3.98, 4.02] with no outliers; [3.0, 5.0] is deliberately
    wider than that observed band specifically because Hypothesis will
    sample cases exploration did not, and a razor-thin band around 4.0
    risks flakiness per the task brief's explicit guidance. Cases where
    either error is already below 1e-5 m (i.e. RK4 is already at or near
    floating-point/oracle-tolerance noise floor at steps=60) are skipped via
    ``assume``, since the convergence-order ratio becomes numerically
    meaningless once both errors are dominated by noise rather than
    truncation error.

    Assumptions/limitations: point-mass two-body dynamics only; near-
    singular close-approach regimes (where RK4's smoothness assumption
    breaks down) are avoided by construction via the near-circular
    speed_fraction range and bound-orbit dt scaling, not by an explicit
    exclusion check, so this property does not claim 4th-order convergence
    for strongly eccentric or hyperbolic cases.
    """
    r_hat = np.array(direction) / np.linalg.norm(direction)
    r_vec = r_hat * radius_m
    v_circular = math.sqrt(mu / radius_m)
    v_dir = np.cross(r_hat, np.array([1.0, 0.0, 0.0]))
    if np.linalg.norm(v_dir) < 1e-6:
        v_dir = np.cross(r_hat, np.array([0.0, 1.0, 0.0]))
    v_dir = v_dir / np.linalg.norm(v_dir)
    v_vec = v_dir * v_circular * speed_fraction
    state0 = np.hstack([r_vec, v_vec])

    energy = specific_orbital_energy(state0, mu)
    assume(energy < 0.0)
    semi_major_axis = -mu / (2.0 * energy)
    period = 2.0 * math.pi * math.sqrt(semi_major_axis**3 / mu)
    dt = period_fraction * period

    reference_final_state = _solve_ivp_two_body_oracle(state0, mu, dt)

    steps_h = 60
    state_h = propagate_cartesian_state(state0, mu, dt, steps=steps_h)
    state_h2 = propagate_cartesian_state(state0, mu, dt, steps=steps_h * 2)

    error_h = float(np.linalg.norm(state_h[:3] - reference_final_state[:3]))
    error_h2 = float(np.linalg.norm(state_h2[:3] - reference_final_state[:3]))
    assume(error_h > 1e-5 and error_h2 > 1e-5)

    observed_order = math.log2(error_h / error_h2)
    assert 3.0 <= observed_order <= 5.0
