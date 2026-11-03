"""Smoke test for the shared CW/two-body state-history test helper (TJC-16.1).

This is pure test-infrastructure coverage: it does not test ``src/cw.py`` or
``src/twobody.py`` themselves (those already have dedicated coverage in
``tests/test_cw.py``, ``tests/test_twobody.py``, and
``tests/test_physics_properties.py``). It only confirms that
``tests/helpers/cw_state_histories.py`` -- the shared helper the TJC-16.2/
16.3/16.4 visualization subtasks' own Hypothesis tests are meant to import
instead of each duplicating CW/two-body setup -- actually produces a valid,
non-degenerate state history for both the CW and two-body paths, rather than
degenerate/empty output.
"""

from __future__ import annotations

import numpy as np
from hypothesis import given, settings

from src.cw import CWRendezvousSolution
from tests.helpers.cw_state_histories import (
    cw_rendezvous_cases,
    propagated_two_body_state_history,
    solved_cw_rendezvous,
    two_body_cases,
)


@given(cw_rendezvous_cases())
@settings(max_examples=25, deadline=2000)
def test_solved_cw_rendezvous_produces_non_degenerate_feasible_solution_or_explicit_infeasibility(case) -> None:
    """The shared CW helper either returns a feasible solution with a
    non-empty, finite trajectory (ready for a plotting function to
    consume) or an explicit infeasible result with no fabricated
    trajectory -- never a degenerate/empty feasible result.

    This mirrors ``src/cw.py::CWRendezvousSolution``'s own documented
    contract (trajectory/final-state fields are ``None`` only when
    ``feasible`` is ``False``); this test exists to confirm the shared
    helper preserves that contract rather than silently masking it.
    """
    mu, reference_radius_m, state0, t_final, target = case
    solution = solved_cw_rendezvous(mu, reference_radius_m, state0, t_final, target)

    assert isinstance(solution, CWRendezvousSolution)
    if solution.feasible:
        assert solution.trajectory_states is not None
        assert solution.trajectory_times_s is not None
        assert solution.trajectory_states.shape[0] >= 2
        assert np.isfinite(solution.trajectory_states).all()
        assert np.isfinite(solution.final_state).all()
    else:
        assert solution.trajectory_states is None
        assert solution.final_state is None


@given(two_body_cases())
@settings(max_examples=25, deadline=2000)
def test_propagated_two_body_state_history_is_non_degenerate_and_finite(case) -> None:
    """The shared two-body helper returns a non-empty, finite state history
    sampled over elapsed time from the same generated initial state, never
    a degenerate/empty array.
    """
    mu, radius_m, state0, dt = case
    times, states = propagated_two_body_state_history(mu, radius_m, state0, dt)

    assert times.shape[0] >= 2
    assert states.shape == (times.shape[0], 6)
    assert np.isfinite(times).all()
    assert np.isfinite(states).all()
    # Non-degenerate: the propagated history is not a single repeated point.
    assert float(np.linalg.norm(states[-1, :3] - states[0, :3])) > 0.0
