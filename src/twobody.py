"""Bounded deterministic point-mass two-body propagation in SI Cartesian coordinates.

This module supports coast propagation only: an initial six-element inertial Cartesian
state is propagated under a fixed central point mass with fixed-step classical RK4.
It deliberately does not solve rendezvous targeting, select maneuvers, optimize a
trajectory, or model perturbations.  Those requests must use ``unsupported_request``
rather than treating a coast result as an improvised solution.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal, Tuple

import numpy as np

STATE_FRAME = "inertial-cartesian"
CENTRAL_BODY = "Earth"
FALLBACK_LIMITATIONS = (
    "Point-mass central gravity only; no J2, drag, third bodies, solar radiation pressure, or thrust.",
    "Coast propagation only; rendezvous targeting, maneuvers, and trajectory optimization are unsupported.",
    "Inputs and outputs are SI inertial Cartesian states, not LVLH-relative states or unspecified frames.",
)


@dataclass(frozen=True)
class TwoBodyCase:
    """Like-for-like SI Cartesian coast case for a future external verifier."""

    case_id: str
    state0_m_mps: tuple[float, float, float, float, float, float]
    mu_m3_s2: float
    duration_s: float
    steps: int
    frame: str = STATE_FRAME
    central_body: str = CENTRAL_BODY
    epoch: str | None = None
    dynamics: str = "point-mass-two-body"
    integrator: str = "fixed-step-rk4"


@dataclass(frozen=True)
class UnsupportedTwoBodyRequest:
    """Explicit response for requests outside the bounded coast contract."""

    status: Literal["UNSUPPORTED"]
    request: str
    limitation: str
    recommended_next_step: str


def unsupported_request(request: str) -> UnsupportedTwoBodyRequest:
    """Return an explicit limitation instead of manufacturing an unsupported result."""
    return UnsupportedTwoBodyRequest(
        status="UNSUPPORTED",
        request=request,
        limitation=(
            "The deterministic two-body fallback supports only inertial Cartesian "
            "point-mass coast propagation; it does not target rendezvous, plan maneuvers, "
            "optimize trajectories, or include perturbations."
        ),
        recommended_next_step="Use the scoped deterministic component that explicitly supports the request or return it for human review.",
    )


def orbital_period(mu: float, semi_major_axis_m: float) -> float:
    if mu <= 0 or semi_major_axis_m <= 0:
        raise ValueError("mu and semi_major_axis_m must be positive.")
    return 2.0 * math.pi * math.sqrt(semi_major_axis_m**3 / mu)


def vis_viva_speed(mu: float, radius_m: float, semi_major_axis_m: float) -> float:
    if mu <= 0 or radius_m <= 0 or semi_major_axis_m <= 0:
        raise ValueError("mu, radius_m, and semi_major_axis_m must be positive.")
    radicand = mu * (2.0 / radius_m - 1.0 / semi_major_axis_m)
    if radicand < 0:
        raise ValueError("vis-viva inputs do not describe a physical speed.")
    return math.sqrt(radicand)


def _validated_vector(values: np.ndarray, name: str) -> np.ndarray:
    vector = np.asarray(values, dtype=float).reshape(-1)
    if vector.shape != (3,) or not np.isfinite(vector).all():
        raise ValueError(f"{name} must be a finite three-element Cartesian vector.")
    return vector.copy()


def _validate_propagation_inputs(r0: np.ndarray, v0: np.ndarray, mu: float, dt: float, steps: int) -> tuple[np.ndarray, np.ndarray]:
    r = _validated_vector(r0, "r0")
    v = _validated_vector(v0, "v0")
    if not math.isfinite(mu) or mu <= 0:
        raise ValueError("mu must be a positive finite gravitational parameter in m^3/s^2.")
    if not math.isfinite(dt):
        raise ValueError("dt must be finite seconds.")
    if not isinstance(steps, (int, np.integer)) or isinstance(steps, bool) or steps <= 0:
        raise ValueError("steps must be a positive integer.")
    if np.linalg.norm(r) == 0.0:
        raise ValueError("r0 must be nonzero; point-mass acceleration is singular at the central body.")
    return r, v


def kepler_propagate_state(r0: np.ndarray, v0: np.ndarray, mu: float, dt: float, steps: int = 2000) -> Tuple[np.ndarray, np.ndarray]:
    """Propagate an SI inertial Cartesian coast state by fixed-step classical RK4."""
    r, v = _validate_propagation_inputs(r0, v0, mu, dt, steps)
    if dt == 0.0:
        return r, v
    h = dt / steps

    def accel(x: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(x)
        if norm == 0.0:
            raise ValueError("RK4 stage reached the point-mass singularity at the central body.")
        return -mu * x / norm**3

    for _ in range(steps):
        k1_r = v
        k1_v = accel(r)

        k2_r = v + 0.5 * h * k1_v
        k2_v = accel(r + 0.5 * h * k1_r)

        k3_r = v + 0.5 * h * k2_v
        k3_v = accel(r + 0.5 * h * k2_r)

        k4_r = v + h * k3_v
        k4_v = accel(r + h * k3_r)

        r = r + (h / 6.0) * (k1_r + 2 * k2_r + 2 * k3_r + k4_r)
        v = v + (h / 6.0) * (k1_v + 2 * k2_v + 2 * k3_v + k4_v)

    return r, v


def propagate_cartesian_state(state0: np.ndarray, mu: float, dt: float, steps: int = 2000) -> np.ndarray:
    """Return the final six-element SI inertial Cartesian coast state."""
    state = np.asarray(state0, dtype=float).reshape(-1)
    if state.shape != (6,) or not np.isfinite(state).all():
        raise ValueError("state0 must be a finite six-element SI Cartesian state.")
    r, v = kepler_propagate_state(state[:3], state[3:], mu, dt, steps=steps)
    return np.hstack([r, v])


def specific_orbital_energy(state: np.ndarray, mu: float) -> float:
    """Return specific orbital energy [m^2/s^2] for an SI Cartesian state."""
    state = np.asarray(state, dtype=float).reshape(-1)
    if state.shape != (6,) or not np.isfinite(state).all() or not math.isfinite(mu) or mu <= 0:
        raise ValueError("state must be finite length six and mu must be positive finite.")
    radius = np.linalg.norm(state[:3])
    if radius == 0.0:
        raise ValueError("specific energy is undefined at the central body.")
    return 0.5 * float(np.dot(state[3:], state[3:])) - mu / radius


def specific_angular_momentum(state: np.ndarray) -> np.ndarray:
    """Return specific angular momentum [m^2/s] for an SI Cartesian state."""
    state = np.asarray(state, dtype=float).reshape(-1)
    if state.shape != (6,) or not np.isfinite(state).all():
        raise ValueError("state must be a finite six-element SI Cartesian state.")
    return np.cross(state[:3], state[3:])
