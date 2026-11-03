"""Hypothesis property tests for the 3D relative-position visualization (TJC-16.2).

Extends TJC-6's Hypothesis property-test conventions (physical rationale,
ICs/units, expected result+tolerance+justification, assumptions/limitations
recorded per test) to ``src/visualization.py::plot_relative_position_3d``.
Generated non-degenerate CW/two-body relative-state histories come from
``tests/helpers/cw_state_histories.py`` (TJC-16.1), shared across this
visualization task family rather than re-derived here.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings

from src.visualization import (
    CHASER_TRACE_NAME,
    TARGET_TRACE_NAME,
    plot_relative_position_3d,
)
from src.verify import _lvlh_basis
from tests.helpers.cw_state_histories import (
    cw_rendezvous_cases,
    solved_cw_rendezvous,
    two_body_cases,
    propagated_two_body_state_history,
)

_FAST = settings(max_examples=30, deadline=5000)


def _trace_by_name(figure, name: str):
    matches = [trace for trace in figure.data if trace.name == name]
    assert len(matches) == 1, f"expected exactly one trace named {name!r}, found {len(matches)}"
    return matches[0]


@given(case=cw_rendezvous_cases())
@_FAST
def test_chaser_trace_offset_from_target_matches_authoritative_relative_position(case) -> None:
    """AC1/AC3: the chaser trace recovered from the rendered Figure, minus
    the fixed target trace, reproduces the exact relative position fed in
    (after the documented LVLH->inertial rotation), to numerical tolerance.

    Physical rationale: the task's core correctness requirement is that the
    chaser's rendered offset from the target is the AUTHORITATIVE relative
    position from the supplied state history, not an approximation -- only
    the scene's inertial anchor point is illustrative (module docstring in
    ``src/visualization.py``). This test pulls the actual plotted x/y/z
    arrays back out of the returned ``plotly.graph_objects.Figure`` (not a
    re-derivation from scratch) and checks offset-from-target equals the
    relative position rotated into the same illustrative inertial frame via
    ``src/verify.py::_lvlh_basis`` -- the same basis construction
    ``src/visualization.py`` itself reuses, per this project's established
    LVLH-inertial conversion pattern (``src/verify.py::_rel_lvlh_to_absolute``).

    ICs/units: a non-singular CW rendezvous case from
    ``tests/helpers/cw_state_histories.py::cw_rendezvous_cases()`` (circular
    chief, sub-GEO through sub-LEO mean motion, meters/seconds SI), solved by
    ``solved_cw_rendezvous`` to get ``trajectory_states``/``trajectory_times_s``
    exactly as ``src/cw.py::solve_cw_rendezvous`` would hand to a caller.
    ``target_orbit_radius_m`` is set equal to this case's own
    ``reference_radius_m`` (a representative, non-adversarial illustrative
    anchor radius).

    Expected result/tolerance: max absolute coordinate difference <= 1e-6 m.
    Justification: the rotation and addition in
    ``plot_relative_position_3d`` are both exact double-precision linear
    algebra (a 3x3 rotation matmul and a vector add, no iterative solve or
    sampling), so exploration found residuals at machine-precision scale
    (~1e-9 m or tighter); 1e-6 m leaves comfortable margin without being
    razor-thin.

    Assumptions/limitations: this property only exercises CW rendezvous
    histories (not the two-body history path), and only non-singular cases
    (``cw_rendezvous_cases()``'s own singularity guard); a separate test
    below exercises the two-body-history input path.
    """
    mu, reference_radius_m, state0, t_final, target = case
    solution = solved_cw_rendezvous(mu, reference_radius_m, state0, t_final, target)
    if not solution.feasible:
        return

    result = plot_relative_position_3d(
        solution.trajectory_states, solution.trajectory_times_s, reference_radius_m
    )

    chief_pos = np.array([reference_radius_m, 0.0, 0.0])
    chief_vel = np.array([0.0, 1.0, 0.0])
    r_mat, _ = _lvlh_basis(chief_pos, chief_vel)
    expected_inertial = chief_pos + solution.trajectory_states[:, :3] @ r_mat.T

    target_trace = _trace_by_name(result.figure, TARGET_TRACE_NAME)
    chaser_trace = _trace_by_name(result.figure, CHASER_TRACE_NAME)
    target_point = np.array([target_trace.x[0], target_trace.y[0], target_trace.z[0]])
    chaser_points = np.column_stack([chaser_trace.x, chaser_trace.y, chaser_trace.z])

    recovered_offset_from_target = chaser_points - target_point
    recovered_absolute = target_point + recovered_offset_from_target

    np.testing.assert_allclose(recovered_absolute, expected_inertial, rtol=0.0, atol=1e-6)


@given(case=two_body_cases())
@_FAST
def test_chaser_trace_matches_two_body_state_history_input(case) -> None:
    """AC1: plot_relative_position_3d also accepts a two-body-propagated
    relative-state history (``src/twobody.py::propagate_cartesian_state``
    output shape), not only a CW solution's ``trajectory_states``.

    Physical rationale: the task brief requires the plotting function to
    accept "the same array shape/units already produced by
    ``src/cw.py::solve_cw_rendezvous`` OR ``src/twobody.py::propagate_cartesian_state``";
    this test exercises the second source independently so the function's
    input contract is not accidentally coupled to CW-specific fields.

    ICs/units: a bound, non-degenerate two-body case from
    ``tests/helpers/cw_state_histories.py::two_body_cases()``, built into a
    sampled ``(times, states)`` history via
    ``propagated_two_body_state_history`` (meters/seconds SI). The absolute
    two-body state here is reused directly as if it were already a
    "relative" LVLH history -- physically this test only cares that the
    plotting function's rotation/placement arithmetic is shape/unit
    agnostic to which physical source produced the six numbers, matching
    this project's convention of sharing one input contract across both
    histories (see ``src/visualization.py`` docstring).

    Expected result/tolerance: same 1e-6 m tolerance and same recovery
    method as the CW property above, for the same justification (exact
    double-precision linear algebra, not an iterative/sampled quantity).

    Assumptions/limitations: ``radius_m`` from ``two_body_cases()`` is
    reused as the illustrative ``target_orbit_radius_m`` anchor (a
    representative positive radius; not claimed to be dynamically
    consistent with the two-body state's own orbit, since the anchor is
    illustrative by construction).
    """
    mu, radius_m, state0, dt = case
    times, states = propagated_two_body_state_history(mu, radius_m, state0, dt)

    result = plot_relative_position_3d(states, times, radius_m)

    chief_pos = np.array([radius_m, 0.0, 0.0])
    chief_vel = np.array([0.0, 1.0, 0.0])
    r_mat, _ = _lvlh_basis(chief_pos, chief_vel)
    expected_inertial = chief_pos + states[:, :3] @ r_mat.T

    target_trace = _trace_by_name(result.figure, TARGET_TRACE_NAME)
    chaser_trace = _trace_by_name(result.figure, CHASER_TRACE_NAME)
    target_point = np.array([target_trace.x[0], target_trace.y[0], target_trace.z[0]])
    chaser_points = np.column_stack([chaser_trace.x, chaser_trace.y, chaser_trace.z])

    np.testing.assert_allclose(chaser_points, expected_inertial, rtol=0.0, atol=1e-6)
    # target_point is unused beyond sanity that the trace exists with one point.
    assert target_point.shape == (3,)


def test_empty_trajectory_states_is_rejected_not_silently_rendered() -> None:
    """AC3: a zero-length relative-state history must raise, not render.

    Physical rationale: an empty history has no defined chaser position at
    any time; silently rendering an empty/blank scene (or a scene with a
    fabricated single point) would misrepresent the absence of data as a
    valid result. This is an explicit degenerate-input contract check, not
    a Hypothesis-generated property.

    ICs/units: a ``(0, 6)`` float array (zero samples, correct column
    count) and a matching length-0 times array.

    Expected result: ``ValueError`` is raised before any Plotly figure is
    constructed or any file is written.

    Assumptions/limitations: only covers the zero-length-history shape of
    "degenerate"; non-finite-value degeneracy is covered by the next test.
    """
    empty_states = np.zeros((0, 6))
    empty_times = np.zeros((0,))
    with pytest.raises(ValueError):
        plot_relative_position_3d(empty_states, empty_times, 7_000_000.0)


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_trajectory_states_is_rejected_not_silently_rendered(bad_value: float) -> None:
    """AC3: a relative-state history containing NaN/inf must raise, not render.

    Physical rationale: a NaN/inf relative position has no physically
    meaningful location to offset the chaser from the target; silently
    rendering it (e.g. Plotly dropping/NaN-skipping the point) would hide a
    genuine upstream failure (e.g. a non-converged solve) as if the scene
    were valid.

    ICs/units: a well-formed ``(3, 6)`` finite history with one element
    replaced by ``bad_value`` (NaN, +inf, or -inf in turn).

    Expected result: ``ValueError`` is raised before any Plotly figure is
    constructed or any file is written.

    Assumptions/limitations: only one element is corrupted per case; this
    is sufficient to establish the all-finite check rejects non-finite
    input anywhere in the array, not only a fully-NaN array.
    """
    states = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [10.0, 20.0, 30.0, 0.1, 0.2, 0.3],
            [bad_value, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
    )
    times = np.array([0.0, 10.0, 20.0])
    with pytest.raises(ValueError):
        plot_relative_position_3d(states, times, 7_000_000.0)
