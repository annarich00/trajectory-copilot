"""Shared test-only helpers for generating valid CW/two-body state histories.

Pure test infrastructure for TJC-16 (visualization pipeline): TJC-16.2
(interactive 3D relative-position scene), TJC-16.3 (LVLH trajectory plot
with burn markers), and TJC-16.4 (CW-vs-two-body-vs-GMAT error-history
comparison plot) each need a non-degenerate, physically valid CW or
two-body state history to exercise their own plotting functions' Hypothesis
property tests. This module is the single place that setup lives, so each
sibling subtask imports from here rather than re-deriving its own generated
circular-chief CW cases or two-body initial-state construction.

This module contains no production code and is not imported by anything
under ``src/``. It follows the same Hypothesis strategy/docstring
conventions established by ``tests/test_physics_properties.py`` (TJC-6):
generated inputs are restricted to each governing module's own documented
physical validity domain, and known singular/near-singular regions are
explicitly excluded via ``assume`` rather than swept over blindly.

Two Hypothesis strategies are exposed:

- ``cw_rendezvous_cases()``: generates ``(mu, reference_radius_m, state0,
  t_final, target)`` tuples, excluding the documented CW targeting
  singularities (``reference/SOURCE.md`` "Known singularities";
  ``docs/cw-stm-audit.md``), consistent with
  ``tests/test_physics_properties.py``'s own singularity-guard convention.
- ``two_body_cases()``: generates ``(mu, radius_m, state0, dt)`` tuples
  restricted to bound, non-degenerate two-body initial states, following
  the same construction as
  ``tests/test_physics_properties.py::_random_bound_two_body_state``.

Two plain helper functions turn a generated case into an actual solved/
propagated state history, ready for a plotting function to consume:

- ``solved_cw_rendezvous(...)`` wraps ``src/cw.py::solve_cw_rendezvous``.
- ``propagated_two_body_state_history(...)`` wraps repeated calls to
  ``src/twobody.py::propagate_cartesian_state`` to build a sampled
  trajectory (that function itself only returns the final state, not a
  history).
"""

from __future__ import annotations

import math

import numpy as np
from hypothesis import assume
from hypothesis import strategies as st

from src.cw import CWRendezvousSolution, mean_motion, solve_cw_rendezvous
from src.twobody import propagate_cartesian_state

# Same generated domain as tests/test_physics_properties.py's circular-chief
# CW cases: sub-GEO through sub-LEO mean motion, local proximity-operations
# relative-state scale (reference/SOURCE.md Sec B.1's CW linearization
# assumption).
MU_EARTH = 398_600_441_800_000.0
_CW_REFERENCE_RADIUS_M = st.floats(min_value=6.6e6, max_value=4.3e7, allow_nan=False, allow_infinity=False)
_CW_T_FINAL_S = st.floats(min_value=60.0, max_value=20_000.0, allow_nan=False, allow_infinity=False)
_CW_RELATIVE_POSITION_M = st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
_CW_RELATIVE_VELOCITY_MPS = st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False)

# Same generated domain as
# tests/test_physics_properties.py::test_two_body_propagation_conserves_energy_and_angular_momentum.
_TWO_BODY_MU = st.floats(min_value=1e13, max_value=1e15, allow_nan=False, allow_infinity=False)
_TWO_BODY_RADIUS_M = st.floats(min_value=5e6, max_value=5e7, allow_nan=False, allow_infinity=False)
_TWO_BODY_SPEED_FRACTION = st.floats(min_value=0.5, max_value=1.3, allow_nan=False, allow_infinity=False)
_TWO_BODY_DIRECTION = st.tuples(
    st.floats(min_value=-1.0, max_value=1.0),
    st.floats(min_value=-1.0, max_value=1.0),
    st.floats(min_value=-1.0, max_value=1.0),
).filter(lambda d: np.linalg.norm(d) > 0.2)
_TWO_BODY_DT_S = st.floats(min_value=10.0, max_value=3000.0, allow_nan=False, allow_infinity=False)

# n*t values within this distance (radians) of an integer multiple of pi are
# the documented CW targeting (Phi_rv) singularities (reference/SOURCE.md
# "Known singularities"; docs/cw-stm-audit.md); excluded here so every
# generated case this module hands to a plotting function's own property
# test is a well-conditioned, non-singular transfer, matching
# tests/test_physics_properties.py's own singularity-guard convention.
_SINGULARITY_GUARD_RAD = 0.3


@st.composite
def cw_rendezvous_cases(draw) -> tuple[float, float, np.ndarray, float, np.ndarray]:
    """Generate a non-singular ``(mu, reference_radius_m, state0, t_final,
    target)`` CW rendezvous case, ready for ``solved_cw_rendezvous``.

    ``mu`` is fixed at ``MU_EARTH`` (matching this project's existing
    circular-LEO/GEO CW fixtures in ``tests/test_cw.py`` and
    ``tests/test_physics_properties.py``, which also hold ``mu`` fixed and
    vary ``reference_radius_m`` to vary mean motion); ``reference_radius_m``
    and ``t_final`` are generated over the same ranges as
    ``tests/test_physics_properties.py``'s CW targeting property, with
    ``n*t_final`` kept at least ``_SINGULARITY_GUARD_RAD`` away from an
    integer multiple of pi.
    """
    reference_radius_m = draw(_CW_REFERENCE_RADIUS_M)
    t_final = draw(_CW_T_FINAL_S)
    n = mean_motion(MU_EARTH, reference_radius_m)
    theta = n * t_final
    rem = theta % math.pi
    assume(rem > _SINGULARITY_GUARD_RAD and rem < math.pi - _SINGULARITY_GUARD_RAD)

    state0 = np.array([draw(_CW_RELATIVE_POSITION_M) for _ in range(3)] + [draw(_CW_RELATIVE_VELOCITY_MPS) for _ in range(3)])
    target = np.array([draw(_CW_RELATIVE_POSITION_M) for _ in range(3)] + [draw(_CW_RELATIVE_VELOCITY_MPS) for _ in range(3)])
    return MU_EARTH, reference_radius_m, state0, t_final, target


def solved_cw_rendezvous(
    mu: float, reference_radius_m: float, state0: np.ndarray, t_final: float, target: np.ndarray
) -> CWRendezvousSolution:
    """Return the actual ``src/cw.py::solve_cw_rendezvous`` solution for a
    generated ``cw_rendezvous_cases()`` tuple, ready for a plotting
    function to consume (``trajectory_states``/``trajectory_times_s``,
    ``dv0_mps``/``dv1_mps``, ``final_state``).
    """
    return solve_cw_rendezvous(mu, reference_radius_m, state0, t_final, target)


def _random_bound_two_body_state(mu: float, radius_m: float, speed_fraction: float, direction: np.ndarray) -> np.ndarray:
    """Construct a non-degenerate bound two-body initial state.

    Identical construction to
    ``tests/test_physics_properties.py::_random_bound_two_body_state``:
    the position is placed at ``radius_m`` along the generated direction,
    and the velocity direction is derived to be non-collinear with the
    position (not because a collinear/rectilinear orbit is physically
    invalid, but to keep the generated history visually representative for
    a plotting function rather than a degenerate straight-line case).
    """
    r_hat = direction / np.linalg.norm(direction)
    r_vec = r_hat * radius_m
    v_circular = math.sqrt(mu / radius_m)
    v_dir = np.cross(direction, np.array([1.0, 0.0, 0.0]))
    if np.linalg.norm(v_dir) < 1e-6:
        v_dir = np.cross(direction, np.array([0.0, 1.0, 0.0]))
    v_dir = v_dir / np.linalg.norm(v_dir)
    v_vec = v_dir * v_circular * speed_fraction
    return np.hstack([r_vec, v_vec])


@st.composite
def two_body_cases(draw) -> tuple[float, float, np.ndarray, float]:
    """Generate a non-degenerate bound ``(mu, radius_m, state0, dt)``
    two-body case, ready for ``propagated_two_body_state_history``.

    Generated over the same domain as
    ``tests/test_physics_properties.py::test_two_body_propagation_conserves_energy_and_angular_momentum``.
    """
    mu = draw(_TWO_BODY_MU)
    radius_m = draw(_TWO_BODY_RADIUS_M)
    speed_fraction = draw(_TWO_BODY_SPEED_FRACTION)
    direction = np.array(draw(_TWO_BODY_DIRECTION))
    dt = draw(_TWO_BODY_DT_S)
    state0 = _random_bound_two_body_state(mu, radius_m, speed_fraction, direction)
    return mu, radius_m, state0, dt


def propagated_two_body_state_history(
    mu: float, radius_m: float, state0: np.ndarray, dt: float, samples: int = 20, steps_per_sample: int = 200
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(times_s, states)`` sampled over ``[0, dt]`` for a generated
    ``two_body_cases()`` tuple, ready for a plotting function to consume.

    ``src/twobody.py::propagate_cartesian_state`` only returns the final
    state for one elapsed duration, not a sampled history; this helper
    calls it once per sample time (each call independently propagating from
    ``state0``, matching that function's own documented contract) to build
    an actual state-history array, analogous to
    ``src/cw.py::solve_cw_rendezvous``'s own ``trajectory_states`` sampling.
    ``radius_m`` is accepted for symmetry with ``two_body_cases()`` but is
    not otherwise required by propagation itself (the full six-element
    ``state0`` already carries position and velocity).

    ``steps_per_sample`` (default 200, well below ``propagate_cartesian_state``'s
    own default of 2000) keeps this test-only history-building helper fast
    across many generated Hypothesis cases and sample points; RK4 global
    accuracy at this reduced step count is still far tighter than the
    coarse visual tolerance a plotting function's own property test needs
    (see ``tests/test_physics_properties.py``'s AC8 RK4 convergence-order
    property for this project's own characterization of RK4 accuracy vs.
    step count), not a precision this module otherwise depends on.
    """
    del radius_m
    times = np.linspace(0.0, dt, samples)
    states = np.array([propagate_cartesian_state(state0, mu, float(t), steps=steps_per_sample) for t in times])
    return times, states
