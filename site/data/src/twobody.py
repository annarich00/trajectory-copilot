"""Two-body orbital dynamics utilities.

All quantities use SI units.
"""

from __future__ import annotations

import math
from typing import Tuple

import numpy as np


def orbital_period(mu: float, semi_major_axis_m: float) -> float:
    return 2.0 * math.pi * math.sqrt(semi_major_axis_m**3 / mu)


def vis_viva_speed(mu: float, radius_m: float, semi_major_axis_m: float) -> float:
    return math.sqrt(mu * (2.0 / radius_m - 1.0 / semi_major_axis_m))


def kepler_propagate_state(r0: np.ndarray, v0: np.ndarray, mu: float, dt: float, steps: int = 2000) -> Tuple[np.ndarray, np.ndarray]:
    """Propagate a Cartesian state by simple two-body RK4 integration."""
    r = np.asarray(r0, dtype=float).reshape(3).copy()
    v = np.asarray(v0, dtype=float).reshape(3).copy()
    h = dt / steps

    def accel(x: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(x)
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
    state0 = np.asarray(state0, dtype=float).reshape(6)
    r, v = kepler_propagate_state(state0[:3], state0[3:], mu, dt, steps=steps)
    return np.hstack([r, v])
