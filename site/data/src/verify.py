"""Verification utilities for CW versus two-body comparisons."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .cw import propagate_relative_state
from .twobody import propagate_cartesian_state


@dataclass(frozen=True)
class VerificationResult:
    cw_state: np.ndarray
    two_body_state: np.ndarray
    position_error_m: float
    velocity_error_mps: float
    warnings: tuple[str, ...]


def compare_cw_two_body(cw_state: np.ndarray, two_body_state: np.ndarray, pos_tol_m: float = 50.0, vel_tol_mps: float = 0.05) -> VerificationResult:
    cw_state = np.asarray(cw_state, dtype=float).reshape(6)
    two_body_state = np.asarray(two_body_state, dtype=float).reshape(6)
    pos_err = float(np.linalg.norm(cw_state[:3] - two_body_state[:3]))
    vel_err = float(np.linalg.norm(cw_state[3:] - two_body_state[3:]))
    warnings = []
    if pos_err > pos_tol_m or vel_err > vel_tol_mps:
        warnings.append("MODEL VALIDITY WARNING")
    return VerificationResult(cw_state, two_body_state, pos_err, vel_err, tuple(warnings))


def _chief_circular_state(n: float, mu: float) -> tuple[np.ndarray, np.ndarray]:
    """Return an inertial (chief_pos, chief_vel) for a circular reference orbit.

    The chief is placed on the inertial X-axis with velocity along the
    inertial Y-axis, so that at t=0 the LVLH frame (x radial, y along-
    track, z cross-track; see reference/SOURCE.md) is aligned with the
    inertial frame. This is consistent with the convention already used by
    cw_stm/propagate_relative_state.
    """
    r0 = (mu / n**2) ** (1.0 / 3.0)
    v0 = n * r0
    chief_pos = np.array([r0, 0.0, 0.0])
    chief_vel = np.array([0.0, v0, 0.0])
    return chief_pos, chief_vel


def _lvlh_basis(chief_pos: np.ndarray, chief_vel: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (R, h_hat) where R's columns are the LVLH unit vectors in the
    inertial frame: r_hat (radial), t_hat (along-track), h_hat (cross-track).
    """
    r_hat = chief_pos / np.linalg.norm(chief_pos)
    h = np.cross(chief_pos, chief_vel)
    h_hat = h / np.linalg.norm(h)
    t_hat = np.cross(h_hat, r_hat)
    r_mat = np.column_stack([r_hat, t_hat, h_hat])
    return r_mat, h_hat


def _rel_lvlh_to_absolute(
    chief_pos: np.ndarray, chief_vel: np.ndarray, rel_state: np.ndarray, n: float
) -> tuple[np.ndarray, np.ndarray]:
    """Convert a CW relative state (LVLH) to an absolute inertial deputy state."""
    r_mat, h_hat = _lvlh_basis(chief_pos, chief_vel)
    r_rel_lvlh, v_rel_lvlh = rel_state[:3], rel_state[3:]
    r_rel_inertial = r_mat @ r_rel_lvlh
    omega = n * h_hat
    deputy_pos = chief_pos + r_rel_inertial
    v_rel_inertial = r_mat @ v_rel_lvlh + np.cross(omega, r_rel_inertial)
    deputy_vel = chief_vel + v_rel_inertial
    return deputy_pos, deputy_vel


def _absolute_to_rel_lvlh(
    chief_pos: np.ndarray,
    chief_vel: np.ndarray,
    deputy_pos: np.ndarray,
    deputy_vel: np.ndarray,
    n: float,
) -> np.ndarray:
    """Convert absolute inertial chief/deputy states to a CW relative state (LVLH)."""
    r_mat, h_hat = _lvlh_basis(chief_pos, chief_vel)
    r_mat_t = r_mat.T
    r_rel_inertial = deputy_pos - chief_pos
    v_rel_inertial = deputy_vel - chief_vel
    omega = n * h_hat
    r_rel_lvlh = r_mat_t @ r_rel_inertial
    v_rel_lvlh = r_mat_t @ (v_rel_inertial - np.cross(omega, r_rel_inertial))
    return np.hstack([r_rel_lvlh, v_rel_lvlh])


def validate_against_two_body(initial_state: np.ndarray, n: float, dt: float, mu: float, pos_tol_m: float = 50.0, vel_tol_mps: float = 0.05) -> VerificationResult:
    """Verify a CW relative-motion propagation against an independent
    nonlinear two-body propagation.

    This builds a circular reference (chief) orbit consistent with the
    supplied mean motion ``n`` and ``mu``, converts the CW relative state
    into absolute inertial chief/deputy states, propagates *both* bodies
    with the nonlinear two-body RK4 integrator in ``twobody.py``, and
    converts the result back into the CW relative (LVLH) frame. This is
    then compared against the CW linear propagation of the same initial
    state over the same ``dt``.

    Unlike a self-comparison, this uses a genuinely independent dynamics
    model (nonlinear point-mass two-body integration) as the reference
    truth, so divergence between CW and two-body here reflects actual
    CW linearization error rather than trivially comparing CW to itself.
    """
    initial_state = np.asarray(initial_state, dtype=float).reshape(6)

    cw_state = propagate_relative_state(initial_state, n, dt)

    chief_pos0, chief_vel0 = _chief_circular_state(n, mu)
    deputy_pos0, deputy_vel0 = _rel_lvlh_to_absolute(chief_pos0, chief_vel0, initial_state, n)

    chief_state_f = propagate_cartesian_state(np.hstack([chief_pos0, chief_vel0]), mu, dt)
    deputy_state_f = propagate_cartesian_state(np.hstack([deputy_pos0, deputy_vel0]), mu, dt)

    tb_state = _absolute_to_rel_lvlh(
        chief_state_f[:3], chief_state_f[3:], deputy_state_f[:3], deputy_state_f[3:], n
    )

    return compare_cw_two_body(cw_state, tb_state, pos_tol_m=pos_tol_m, vel_tol_mps=vel_tol_mps)
