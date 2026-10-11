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
from typing import Literal
import numpy as np


@dataclass(frozen=True)
class CWValidity:
    valid: bool
    warnings: tuple[str, ...]


class CWSingularTransferError(RuntimeError):
    """Retained for callers that explicitly require a unique CW solution.

    ``two_burn_targeting`` now returns a structured infeasible result for a
    singular unreachable boundary condition. This exception remains the guard
    used by ``check_phi_rv_conditioning`` for callers that request a unique,
    well-conditioned inverse solve.
    """


# A condition number above this value routes targeting through the SVD path.
# It remains explicit metadata: a near-singular matrix is never represented as
# a unique inverse result.
CW_CONDITION_NUMBER_LIMIT = 1.0e6
# Singular values at or below this relative-to-largest threshold are treated as
# zero. Residual reachability is accepted only up to this scale times max(1,|b|).
CW_SVD_RANK_TOLERANCE = 1.0e-12
CW_SVD_RESIDUAL_TOLERANCE = 1.0e-9


@dataclass(frozen=True)
class CWTargetingResult:
    """Structured fixed-duration two-burn targeting outcome.

    ``status`` is ``"unique"``, ``"singular-reachable"``, or
    ``"singular-infeasible"``. Singular reachable solutions use the SVD
    pseudoinverse and are explicitly non-unique. Infeasible outcomes contain
    no fabricated burns or final state.
    """

    status: str
    feasible: bool
    singular: bool
    non_unique: bool
    reason: str
    condition_number: float
    rank: int
    reachability_residual_m: float
    svd_rank_tolerance: float
    svd_residual_tolerance: float
    dv0: np.ndarray | None
    dv1: np.ndarray | None
    final_state: np.ndarray | None


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


def _svd_targeting_diagnostics(
    phi_rv: np.ndarray,
    b: np.ndarray,
    *,
    rank_tolerance: float,
    residual_tolerance: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, float, float, np.ndarray]:
    """Return SVD diagnostics and the minimum-norm solution for ``Phi_rv x=b``.

    A singular value is retained when it exceeds ``rank_tolerance * s_max``.
    The reachability residual is the norm of the component of ``b`` outside
    the retained left-singular-vector column space. It must be no greater than
    ``residual_tolerance * max(1, ||b||)`` for the boundary condition to be
    reachable.
    """
    u, singular_values, vh = np.linalg.svd(phi_rv, full_matrices=False)
    scale = singular_values[0] if singular_values.size else 0.0
    cutoff = rank_tolerance * scale
    rank = int(np.count_nonzero(singular_values > cutoff))
    if rank:
        projected_b = u[:, :rank] @ (u[:, :rank].T @ b)
        minimum_norm_solution = (
            vh[:rank, :].T @ ((u[:, :rank].T @ b) / singular_values[:rank])
        )
    else:
        projected_b = np.zeros_like(b)
        minimum_norm_solution = np.zeros(phi_rv.shape[1])
    residual = float(np.linalg.norm(b - projected_b))
    allowed_residual = residual_tolerance * max(1.0, float(np.linalg.norm(b)))
    return singular_values, u, vh, rank, residual, allowed_residual, minimum_norm_solution


def two_burn_targeting(
    state0: np.ndarray,
    n: float,
    t_final: float,
    target_final_state: np.ndarray | None = None,
    *,
    condition_limit: float = CW_CONDITION_NUMBER_LIMIT,
    svd_rank_tolerance: float = CW_SVD_RANK_TOLERANCE,
    svd_residual_tolerance: float = CW_SVD_RESIDUAL_TOLERANCE,
) -> CWTargetingResult:
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
    CWTargetingResult
        A unique result for a well-conditioned inverse solve, a singular but
        reachable non-unique result using the SVD-pseudoinverse minimum-norm
        solution, or a singular-and-infeasible result with no burns. The
        requested ``t_final`` is never changed.
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

    b = rf_des - phi_rr @ r0
    rhs = b - phi_rv @ v0
    if not np.isfinite(phi_rv).all() or not np.isfinite(rhs).all():
        raise CWSingularTransferError("Phi_rv or targeting boundary condition is non-finite.")

    condition_number = float(np.linalg.cond(phi_rv))
    singular_values, _, _, rank, residual, allowed_residual, minimum_norm_velocity = (
        _svd_targeting_diagnostics(
            phi_rv,
            b,
            rank_tolerance=svd_rank_tolerance,
            residual_tolerance=svd_residual_tolerance,
        )
    )
    singular_or_ill_conditioned = (
        rank < phi_rv.shape[1]
        or not np.isfinite(condition_number)
        or condition_number > condition_limit
    )

    if singular_or_ill_conditioned:
        if residual > allowed_residual:
            return CWTargetingResult(
                status="singular-infeasible",
                feasible=False,
                singular=True,
                non_unique=rank < phi_rv.shape[1],
                reason=(
                    "Requested terminal position is outside the Phi_rv column space "
                    f"(SVD residual={residual:.3e} m > tolerance={allowed_residual:.3e} m)."
                ),
                condition_number=condition_number,
                rank=rank,
                reachability_residual_m=residual,
                svd_rank_tolerance=svd_rank_tolerance,
                svd_residual_tolerance=svd_residual_tolerance,
                dv0=None,
                dv1=None,
                final_state=None,
            )
        post_burn_velocity = minimum_norm_velocity
        dv0 = post_burn_velocity - v0
        status = "singular-reachable"
        singular = True
        non_unique = rank < phi_rv.shape[1]
        reason = (
            "Phi_rv is singular or ill-conditioned; terminal position is reachable. "
            "Returned initial velocity is the SVD-pseudoinverse minimum-norm solution."
        )
    else:
        dv0 = np.linalg.solve(phi_rv, rhs)
        status = "unique"
        singular = False
        non_unique = False
        reason = "Phi_rv is well-conditioned; returned the unique inverse solution."

    vf_minus = phi_vr @ r0 + phi_vv @ (v0 + dv0)
    dv1 = vf_des - vf_minus
    final_state = np.hstack([phi_rr @ r0 + phi_rv @ (v0 + dv0), vf_minus + dv1])
    return CWTargetingResult(
        status=status,
        feasible=True,
        singular=singular,
        non_unique=non_unique,
        reason=reason,
        condition_number=condition_number,
        rank=rank,
        reachability_residual_m=residual,
        svd_rank_tolerance=svd_rank_tolerance,
        svd_residual_tolerance=svd_residual_tolerance,
        dv0=dv0,
        dv1=dv1,
        final_state=final_state,
    )

# ---------------------------------------------------------------------------
# TJC-1.15: deterministic rendezvous orchestration
#
# ``solve_cw_rendezvous`` composes ``mean_motion``, ``two_burn_targeting``,
# and ``propagate_relative_state`` into one entry point for a complete,
# structured fixed-duration CW rendezvous problem. It does not add new CW
# physics: ``cw_stm``, ``two_burn_targeting``, and their singularity handling
# (audited under TJC-1.3/TJC-1.4) are used unchanged.
# ---------------------------------------------------------------------------

CW_RENDEZVOUS_FRAME = "LVLH/RIC: x radial outward, y along-track, z cross-track (reference/SOURCE.md Sec A.1)"
CW_RENDEZVOUS_STATE_ORDERING = ("x", "y", "z", "x_dot", "y_dot", "z_dot")
CW_RENDEZVOUS_DYNAMICS = "clohessy-wiltshire-linearized-fixed-duration-two-impulse"
CW_RENDEZVOUS_UNITS = (
    ("position", "m"),
    ("velocity", "m/s"),
    ("time", "s"),
    ("mean_motion", "rad/s"),
    ("delta_v", "m/s"),
    ("gravitational_parameter", "m^3/s^2"),
)
# Mirrors reference/SOURCE.md Sec B.1's assumption-based CW selection checklist.
CW_RENDEZVOUS_ASSUMPTIONS = (
    "circular, or explicitly justified near-circular, chief/reference orbit",
    "local relative separation, small relative to the reference-orbit radius, not global phasing",
    "small relative velocity and a fixed transfer duration/regime for which CW linearization remains acceptable",
    "right-handed LVLH/RIC frame and [x, y, z, x_dot, y_dot, z_dot] state ordering (reference/SOURCE.md Sec A.1)",
    "central-body gravity dominance with perturbations neglected",
    "impulsive, instantaneous two-burn maneuvers at the start and end of the fixed transfer",
)


@dataclass(frozen=True)
class CWRendezvousSolution:
    """Complete deterministic outcome of one fixed-duration CW rendezvous problem.

    ``status``, ``feasible``, ``singular``, ``non_unique``, and ``reason`` are
    taken directly from ``two_burn_targeting``'s structured result: a singular
    or ill-conditioned transfer time surfaces as ``"singular-reachable"`` or
    ``"singular-infeasible"`` here, never as a least-squares substitute or a
    silently changed ``transfer_time_s``. Burn, trajectory, and final-state
    fields are ``None`` only when ``feasible`` is ``False``.
    """

    status: str
    feasible: bool
    singular: bool
    non_unique: bool
    reason: str
    mean_motion_radps: float
    transfer_time_s: float
    dv0_mps: np.ndarray | None
    dv1_mps: np.ndarray | None
    total_delta_v_mps: float | None
    trajectory_times_s: np.ndarray | None
    trajectory_states: np.ndarray | None
    final_state: np.ndarray | None
    condition_number: float
    rank: int
    reachability_residual_m: float
    units: tuple[tuple[str, str], ...]
    frame: str
    state_ordering: tuple[str, ...]
    dynamics: str
    assumptions: tuple[str, ...]


def _validate_cw_rendezvous_inputs(
    mu: float, reference_radius_m: float, t_final: float, trajectory_samples: int
) -> None:
    if not math.isfinite(mu) or mu <= 0:
        raise ValueError("mu must be a positive finite gravitational parameter in m^3/s^2.")
    if not math.isfinite(reference_radius_m) or reference_radius_m <= 0:
        raise ValueError("reference_radius_m must be a positive finite reference orbit radius in m.")
    if not math.isfinite(t_final) or t_final <= 0:
        raise ValueError("t_final must be a positive finite transfer duration in s.")
    if not isinstance(trajectory_samples, (int, np.integer)) or isinstance(trajectory_samples, bool) or trajectory_samples < 2:
        raise ValueError("trajectory_samples must be an integer >= 2.")


def solve_cw_rendezvous(
    mu: float,
    reference_radius_m: float,
    state0: np.ndarray,
    t_final: float,
    target_final_state: np.ndarray | None = None,
    *,
    trajectory_samples: int = 50,
    condition_limit: float = CW_CONDITION_NUMBER_LIMIT,
    svd_rank_tolerance: float = CW_SVD_RANK_TOLERANCE,
    svd_residual_tolerance: float = CW_SVD_RESIDUAL_TOLERANCE,
) -> CWRendezvousSolution:
    """Solve one complete, structured fixed-duration CW rendezvous problem.

    This is the single deterministic orchestration entry point for the
    supported CW rendezvous workflow: it computes mean motion, calls
    ``two_burn_targeting`` for the two impulsive burns, and samples
    ``propagate_relative_state`` over the post-burn-1 coast arc to return a
    relative trajectory. Every outcome exposes ``units``, ``frame``,
    ``state_ordering``, ``dynamics``, ``assumptions``, and solver ``status``
    alongside the numerical result.

    Parameters
    ----------
    mu:
        Positive gravitational parameter [m^3/s^2].
    reference_radius_m:
        Positive circular reference-orbit radius [m].
    state0:
        Initial relative state ``[x, y, z, x_dot, y_dot, z_dot]`` in the
        LVLH/RIC frame, SI units.
    t_final:
        Fixed, positive transfer duration [s]. This value is never changed:
        a singular or ill-conditioned transfer time is reported through
        ``status``/``reason``, not silently retimed.
    target_final_state:
        Desired final relative state; defaults to rendezvous at the origin
        with zero relative velocity.
    trajectory_samples:
        Number of sample points (>= 2) used to report the relative
        trajectory over ``[0, t_final]``.

    Returns
    -------
    CWRendezvousSolution
        A structured result exposing burn components, total delta-v, the
        sampled relative trajectory, final relative state, time of flight,
        units/frame/assumption metadata, and solver status. For a
        ``"singular-infeasible"`` outcome, burn/trajectory/final-state fields
        are ``None`` and no delta-v or trajectory is fabricated.

    This function does not select a transfer time, trade delta-v against
    time, or model dynamics other than circular-chief CW; those requests are
    outside this contract (see ``unsupported_cw_rendezvous_request``).
    """
    _validate_cw_rendezvous_inputs(mu, reference_radius_m, t_final, trajectory_samples)
    state0 = np.asarray(state0, dtype=float).reshape(6)

    n = mean_motion(mu, reference_radius_m)
    targeting = two_burn_targeting(
        state0,
        n,
        t_final,
        target_final_state,
        condition_limit=condition_limit,
        svd_rank_tolerance=svd_rank_tolerance,
        svd_residual_tolerance=svd_residual_tolerance,
    )

    if not targeting.feasible:
        return CWRendezvousSolution(
            status=targeting.status,
            feasible=False,
            singular=targeting.singular,
            non_unique=targeting.non_unique,
            reason=targeting.reason,
            mean_motion_radps=n,
            transfer_time_s=t_final,
            dv0_mps=None,
            dv1_mps=None,
            total_delta_v_mps=None,
            trajectory_times_s=None,
            trajectory_states=None,
            final_state=None,
            condition_number=targeting.condition_number,
            rank=targeting.rank,
            reachability_residual_m=targeting.reachability_residual_m,
            units=CW_RENDEZVOUS_UNITS,
            frame=CW_RENDEZVOUS_FRAME,
            state_ordering=CW_RENDEZVOUS_STATE_ORDERING,
            dynamics=CW_RENDEZVOUS_DYNAMICS,
            assumptions=CW_RENDEZVOUS_ASSUMPTIONS,
        )

    post_burn1_state = np.hstack([state0[:3], state0[3:] + targeting.dv0])
    trajectory_times = np.linspace(0.0, t_final, trajectory_samples)
    trajectory_states = np.array(
        [propagate_relative_state(post_burn1_state, n, float(t)) for t in trajectory_times]
    )

    return CWRendezvousSolution(
        status=targeting.status,
        feasible=True,
        singular=targeting.singular,
        non_unique=targeting.non_unique,
        reason=targeting.reason,
        mean_motion_radps=n,
        transfer_time_s=t_final,
        dv0_mps=targeting.dv0,
        dv1_mps=targeting.dv1,
        total_delta_v_mps=float(np.linalg.norm(targeting.dv0) + np.linalg.norm(targeting.dv1)),
        trajectory_times_s=trajectory_times,
        trajectory_states=trajectory_states,
        final_state=targeting.final_state,
        condition_number=targeting.condition_number,
        rank=targeting.rank,
        reachability_residual_m=targeting.reachability_residual_m,
        units=CW_RENDEZVOUS_UNITS,
        frame=CW_RENDEZVOUS_FRAME,
        state_ordering=CW_RENDEZVOUS_STATE_ORDERING,
        dynamics=CW_RENDEZVOUS_DYNAMICS,
        assumptions=CW_RENDEZVOUS_ASSUMPTIONS,
    )


@dataclass(frozen=True)
class UnsupportedCWRequest:
    """Explicit response for a request outside ``solve_cw_rendezvous``'s contract."""

    status: Literal["UNSUPPORTED"]
    request: str
    limitation: str
    recommended_next_step: str


def unsupported_cw_rendezvous_request(request: str) -> UnsupportedCWRequest:
    """Return an explicit limitation instead of widening the CW rendezvous scope.

    ``solve_cw_rendezvous`` solves only a fixed-duration, two-impulse CW
    rendezvous under the circular-chief, local-separation assumptions in
    ``reference/SOURCE.md`` Sec B.1. Transfer-time selection/optimization,
    delta-v-versus-time trade studies, Pareto fronts, continuous thrust,
    perturbation modeling, and non-CW dynamics (e.g. eccentric chief, CR3BP,
    n-body) are unsupported semester capabilities; this records that
    explicitly rather than improvising an answer.
    """
    return UnsupportedCWRequest(
        status="UNSUPPORTED",
        request=request,
        limitation=(
            "solve_cw_rendezvous supports only a fixed-duration, two-impulse "
            "Clohessy-Wiltshire rendezvous under the circular-chief, local-separation "
            "assumptions in reference/SOURCE.md Sec B.1. It does not choose or optimize "
            "transfer time, trade delta-v against time, generate Pareto fronts, model "
            "continuous thrust or perturbations, or solve non-CW dynamics (e.g. eccentric "
            "chief, CR3BP, n-body)."
        ),
        recommended_next_step=(
            "Use the orbital-problem-formalizer and orbital-model-selector skills to restate "
            "the request as a fixed-duration local CW case or route it to the bounded two-body "
            "coast fallback (src/twobody.py); otherwise return it for human review as unsupported."
        ),
    )
