"""Clohessy-Wiltshire relative motion utilities.

The state convention is ``[x, y, z, x_dot, y_dot, z_dot]`` in the chief's
right-handed LVLH/RIC frame: x radial outward, y along-track/in-track in the
chief's direction of motion, and z orbit-normal. ``cw_stm`` implements the
circular-chief CW solution cited term-by-term in ``docs/cw-stm-audit.md``.
It is not valid for eccentric chiefs, large/global relative geometry,
perturbations, or unqualified long-duration linearization.

All quantities use SI units:
- distance: m
- time: s
- velocity: m/s
- gravitational parameter: m^3/s^2
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass(frozen=True)
class CWValidity:
    valid: bool
    warnings: tuple[str, ...]


class CWSingularTransferError(RuntimeError):
    """Raised when CW two-impulse targeting is singular or ill-conditioned.

    This happens when Phi_rv -- the block of the CW state-transition matrix
    that maps an initial relative-velocity impulse to the resulting change
    in relative position -- loses rank or becomes numerically unreliable to
    invert. Per reference/SOURCE.md ("Known singularities"), this occurs at
    transfer times near integer multiples of half the orbital period
    (n*t = k*pi), where in-plane terms of Phi_rv vanish or nearly vanish.

    At these transfer times the two-impulse targeting problem does not have
    a physically meaningful, well-determined solution, and the computed
    delta-v must not be silently approximated (e.g. via least squares).
    """


# Condition numbers of Phi_rv above this value indicate the position-
# velocity mapping is too close to singular for the targeting solve to be
# numerically trustworthy. See the numeric characterization in this
# module's test suite for how condition number grows near n*t = k*pi.
CW_CONDITION_NUMBER_LIMIT = 1.0e6


def mean_motion(mu: float, reference_radius_m: float) -> float:
    """Return circular-orbit mean motion n [rad/s]."""
    return math.sqrt(mu / reference_radius_m**3)


def cw_stm(n: float, t: float) -> np.ndarray:
    """Return the circular-chief CW STM for ``[x, y, z, x_dot, y_dot, z_dot]``.

    ``n`` is positive mean motion in rad/s and ``t`` is elapsed seconds. The
    returned blocks map position/velocity to position/velocity and therefore
    have units ``[1]``, ``[s]``, ``[1/s]``, and ``[1]`` respectively. See
    ``docs/cw-stm-audit.md`` for the authoritative equation mapping and
    assumptions.
    """
    nt = n * t
    s = math.sin(nt)
    c = math.cos(nt)

    phi_rr = np.array([
        [4 - 3 * c, 0.0, 0.0],
        [6 * (s - nt), 1.0, 0.0],
        [0.0, 0.0, c],
    ])
    phi_rv = np.array([
        [s / n, 2 * (1 - c) / n, 0.0],
        [2 * (c - 1) / n, (4 * s - 3 * nt) / n, 0.0],
        [0.0, 0.0, s / n],
    ])
    phi_vr = np.array([
        [3 * n * s, 0.0, 0.0],
        [6 * n * (c - 1), 0.0, 0.0],
        [0.0, 0.0, -n * s],
    ])
    phi_vv = np.array([
        [c, 2 * s, 0.0],
        [-2 * s, 4 * c - 3, 0.0],
        [0.0, 0.0, c],
    ])
    top = np.hstack([phi_rr, phi_rv])
    bottom = np.hstack([phi_vr, phi_vv])
    return np.vstack([top, bottom])


def propagate_relative_state(state0: np.ndarray, n: float, t: float) -> np.ndarray:
    """Propagate a CW relative state forward in time."""
    state0 = np.asarray(state0, dtype=float).reshape(6)
    return cw_stm(n, t) @ state0


def validate_cw_use(
    reference_radius_m: float,
    relative_position_m: np.ndarray,
    transfer_time_s: float,
    n: float | None = None,
) -> CWValidity:
    """Check basic CW applicability heuristics."""
    warnings: list[str] = []
    r = float(reference_radius_m)
    rel = np.linalg.norm(np.asarray(relative_position_m, dtype=float).reshape(3))
    if r <= 0:
        warnings.append("Reference orbit radius must be positive.")
    if rel / r > 0.01:
        warnings.append("Relative separation is large compared with orbit radius.")
    if transfer_time_s <= 0:
        warnings.append("Transfer time must be positive.")
    if n is not None and transfer_time_s > 2 * math.pi / n * 2:
        warnings.append("Transfer spans more than about two orbital periods.")
    return CWValidity(valid=not warnings, warnings=tuple(warnings))


def check_phi_rv_conditioning(
    phi_rv: np.ndarray, condition_limit: float = CW_CONDITION_NUMBER_LIMIT
) -> float:
    """Return cond(Phi_rv) and raise if the two-impulse solve is singular.

    Phi_rv must be inverted to solve for the initial-impulse delta-v in
    two-impulse CW targeting. Per reference/SOURCE.md, Phi_rv loses rank at
    transfer times near integer multiples of half the orbital period
    (n*t = k*pi), where sin(n*t) -> 0 and the in-plane velocity-to-position
    mapping degenerates. Near these times the matrix remains technically
    invertible in floating point, but the solve is numerically meaningless
    and produces unbounded, physically impossible delta-v.

    This check rejects the targeting problem outright rather than silently
    returning a least-squares "solution" to an ill-posed problem.
    """
    if not np.isfinite(phi_rv).all():
        raise CWSingularTransferError(
            "Phi_rv contains non-finite entries; CW targeting is undefined "
            "for this transfer time."
        )
    det = np.linalg.det(phi_rv)
    if det == 0.0 or not np.isfinite(det):
        raise CWSingularTransferError(
            "Phi_rv is exactly singular (det=0); two-impulse CW targeting "
            "has no unique solution at this transfer time. This typically "
            "occurs at transfer times that are integer multiples of half "
            "the orbital period (n*t = k*pi)."
        )
    cond = float(np.linalg.cond(phi_rv))
    if not np.isfinite(cond) or cond > condition_limit:
        raise CWSingularTransferError(
            f"Phi_rv is ill-conditioned for CW targeting (cond={cond:.3e} > "
            f"limit={condition_limit:.1e}). This occurs near transfer times "
            "that are integer multiples of half the orbital period "
            "(n*t = k*pi), where the in-plane velocity-to-position mapping "
            "nearly degenerates and solved delta-v magnitudes become "
            "unbounded and physically meaningless. Choose a transfer time "
            "away from this singularity (e.g. a non-integer multiple of "
            "half the orbital period)."
        )
    return cond


def _solve_dv_for_target(phi_rv: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    """Solve Phi_rv @ dv0 = rhs after confirming Phi_rv is well-conditioned.

    Raises CWSingularTransferError instead of silently falling back to a
    least-squares pseudo-solution when Phi_rv is singular or ill-conditioned
    (see check_phi_rv_conditioning).
    """
    check_phi_rv_conditioning(phi_rv)
    return np.linalg.solve(phi_rv, rhs)


def two_burn_targeting(
    state0: np.ndarray,
    n: float,
    t_final: float,
    target_final_state: np.ndarray | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute two-impulse CW targeting using STM partitioning.

    The method solves for the initial velocity impulse using the STM block
    partitioning approach with Phi_rr, Phi_rv, Phi_vr, Phi_vv.

    Parameters
    ----------
    state0:
        Initial relative state [r0, v0] in LVLH/RIC coordinates.
    n:
        Mean motion [rad/s].
    t_final:
        Transfer duration [s].
    target_final_state:
        Desired final relative state. Defaults to rendezvous at the origin
        with zero relative velocity.

    Returns
    -------
    dv0, dv1, final_state

    Raises
    ------
    CWSingularTransferError
        If Phi_rv is singular or ill-conditioned at ``t_final`` (e.g.
        ``t_final`` at or near an integer multiple of half the orbital
        period). The caller must choose a different transfer time; this
        function does not silently fall back to a least-squares solution.
    """
    state0 = np.asarray(state0, dtype=float).reshape(6)
    if target_final_state is None:
        target_final_state = np.zeros(6)
    target_final_state = np.asarray(target_final_state, dtype=float).reshape(6)

    phi = cw_stm(n, t_final)
    phi_rr = phi[:3, :3]
    phi_rv = phi[:3, 3:]
    phi_vr = phi[3:, :3]
    phi_vv = phi[3:, 3:]

    r0, v0 = state0[:3], state0[3:]
    rf_des, vf_des = target_final_state[:3], target_final_state[3:]

    dv0 = _solve_dv_for_target(phi_rv, rf_des - phi_rr @ r0 - phi_rv @ v0)
    vf_minus = phi_vr @ r0 + phi_vv @ (v0 + dv0)
    dv1 = vf_des - vf_minus
    final_state = np.hstack([phi_rr @ r0 + phi_rv @ (v0 + dv0), vf_minus + dv1])
    return dv0, dv1, final_state
