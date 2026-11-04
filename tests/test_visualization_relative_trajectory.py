"""Hypothesis and example-based tests for the relative-trajectory plot
(TJC-16.3).

This module tests ``src/visualization_trajectory.py``'s shared plotting
core and its two thin wrappers, following ``tests/test_physics_properties.py``
(TJC-6) and ``tests/test_cw_state_histories_helpers.py``/
``tests/helpers/cw_state_histories.py`` (TJC-16.1)'s established Hypothesis
strategy/docstring conventions: generated inputs come from the shared
``cw_rendezvous_cases()`` strategy (restricted to CW's own documented
physical validity domain, singular transfer times already excluded), and
each property test's docstring records physical rationale, ICs/units,
expected result with tolerance and justification, and assumptions/
limitations.

This module does not re-derive or duplicate any CW/two-body physics: it
only asserts that the plotting functions faithfully render the already-
computed, already-tested numeric results from ``src/cw.py::solve_cw_rendezvous``
and ``tests/helpers/cw_state_histories.py::propagated_two_body_state_history``.
"""

from __future__ import annotations

import numpy as np
from hypothesis import given, settings

from src.cw import CWRendezvousSolution, CW_RENDEZVOUS_ASSUMPTIONS, CW_RENDEZVOUS_DYNAMICS
from src.cw import CW_RENDEZVOUS_FRAME, CW_RENDEZVOUS_STATE_ORDERING, CW_RENDEZVOUS_UNITS
from src.visualization_trajectory import (
    plot_cw_rendezvous_trajectory,
    plot_two_body_trajectory_with_burns,
)
from tests.helpers.cw_state_histories import (
    cw_rendezvous_cases,
    propagated_two_body_state_history,
    solved_cw_rendezvous,
    two_body_cases,
)

_FAST = settings(max_examples=25, deadline=5000)


def _infeasible_cw_solution() -> CWRendezvousSolution:
    """Build an explicit singular-infeasible ``CWRendezvousSolution`` with no
    fabricated burns/trajectory, matching ``src/cw.py::solve_cw_rendezvous``'s
    own documented contract (burn/trajectory/final-state fields are ``None``
    only when ``feasible`` is ``False``).
    """
    return CWRendezvousSolution(
        status="singular-infeasible",
        feasible=False,
        singular=True,
        non_unique=False,
        reason="Requested terminal position is outside the Phi_rv column space (explicitly constructed for this test).",
        mean_motion_radps=0.0011,
        transfer_time_s=1000.0,
        dv0_mps=None,
        dv1_mps=None,
        total_delta_v_mps=None,
        trajectory_times_s=None,
        trajectory_states=None,
        final_state=None,
        condition_number=float("inf"),
        rank=1,
        reachability_residual_m=1.0,
        units=CW_RENDEZVOUS_UNITS,
        frame=CW_RENDEZVOUS_FRAME,
        state_ordering=CW_RENDEZVOUS_STATE_ORDERING,
        dynamics=CW_RENDEZVOUS_DYNAMICS,
        assumptions=CW_RENDEZVOUS_ASSUMPTIONS,
    )


def test_plot_cw_rendezvous_trajectory_rejects_infeasible_solution(tmp_path) -> None:
    """AC3: ``plot_cw_rendezvous_trajectory`` must raise ``ValueError`` for a
    singular-infeasible CW solution rather than silently plotting a
    fabricated or partial trajectory.

    Physical rationale: ``src/cw.py::solve_cw_rendezvous`` documents that
    burn/trajectory/final-state fields are ``None`` only when ``feasible``
    is ``False`` -- there is no valid burn or trajectory data to plot for
    such a result, so the plotting function must reject it explicitly
    rather than attempt to render ``None`` fields.

    ICs/units: an explicitly constructed ``CWRendezvousSolution`` with
    ``feasible=False`` and all burn/trajectory/final-state fields ``None``
    (not a generated case -- this is a single deliberate example of the
    documented infeasible contract).

    Expected result: a ``ValueError`` is raised, and no file is written to
    ``output_path``. Justification: this mirrors this project's existing
    "never fabricate a partial/empty result" convention
    (``src/cw.py::two_burn_targeting``'s own singular-infeasible handling).

    Assumptions/limitations: this test only exercises the CW-specific
    wrapper's explicit infeasibility guard; it does not test the shared
    core's behavior directly (the shared core never receives a
    ``CWRendezvousSolution`` at all, per AC2's plain-array design).
    """
    solution = _infeasible_cw_solution()
    output_path = tmp_path / "infeasible.png"

    try:
        plot_cw_rendezvous_trajectory(solution, output_path)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for an infeasible CW solution")

    assert not output_path.exists()


@given(cw_rendezvous_cases())
@_FAST
def test_plot_cw_rendezvous_trajectory_renders_actual_solution_data(tmp_path_factory, case) -> None:
    """AC4: for generated non-singular feasible CW solutions, the actual
    rendered artifact's data -- read back from the saved PNG and from the
    Matplotlib ``Axes`` the plotting function drew into -- matches the
    solution's own terminal point and burn-application points to tight
    numerical tolerance, and the saved file is a well-formed PNG.

    Physical rationale: this is a visualization-faithfulness property, not
    a physics property -- ``cw_rendezvous_cases()``/``solved_cw_rendezvous``
    already independently establish the CW solution's own correctness
    (``tests/test_cw_state_histories_helpers.py``); this test only confirms
    the plot drawn from that solution actually encodes the solution's own
    ``final_state`` position and ``trajectory_states[0]``/
    ``trajectory_states[-1]`` burn-application positions, not a stale or
    substituted value.

    ICs/units: generated via ``cw_rendezvous_cases()`` (same domain as
    ``tests/test_cw_state_histories_helpers.py``: ``mu`` fixed at Earth's,
    reference_radius_m in [6.6e6, 4.3e7] m, t_final in [60, 20000] s,
    relative position/velocity components in [-1000, 1000] m /
    [-1, 1] m/s, non-singular transfer times only). Only feasible,
    non-singular (``status == "unique"``) solutions are kept; singular-
    reachable and singular-infeasible outcomes are discarded via Hypothesis
    ``assume`` since this AC is explicitly scoped to the non-singular
    feasible case.

    Expected result/tolerance: the plotted terminal-point marker's (x, y)
    data equals ``final_state[:2]`` and the two plotted burn markers' (x, y)
    data equal ``trajectory_states[0, :2]`` and ``trajectory_states[-1, :2]``,
    each to ``atol=1e-6`` (plain floating-point pass-through with no
    recomputation involved, so the only expected residual is roundoff from
    Matplotlib's internal float64 data storage). The saved file exists and
    starts with the PNG magic bytes (``src/gmat_verify.py::validate_gui_screenshot``'s
    own PNG-well-formedness convention).

    Assumptions/limitations: this test checks only the 2D (x, y) LVLH
    in-plane data the shared core actually plots (``z`` is not rendered by
    this 2D plot, matching the Implementation Plan's 2D-LVLH design
    choice); it does not independently verify annotation text content
    (dv magnitude labels), only marker/line position data.
    """
    mu, reference_radius_m, state0, t_final, target = case
    solution = solved_cw_rendezvous(mu, reference_radius_m, state0, t_final, target)
    if not solution.feasible or solution.status != "unique":
        return

    output_dir = tmp_path_factory.mktemp("cw_plot")
    output_path = output_dir / "cw_rendezvous.png"

    saved_path, fig = plot_cw_rendezvous_trajectory(solution, output_path, return_figure=True)

    assert saved_path == output_path
    assert output_path.exists()
    with open(output_path, "rb") as handle:
        header = handle.read(8)
    assert header == b"\x89PNG\r\n\x1a\n"

    ax = fig.axes[0]
    lines_by_label = {line.get_label(): line for line in ax.lines}
    for expected_label in ("Burn 1", "Burn 2", "Rendezvous"):
        assert expected_label in lines_by_label, f"no plotted line labeled {expected_label!r}"

    def _xy(label: str) -> np.ndarray:
        x_data, y_data = lines_by_label[label].get_data()
        return np.array([float(x_data[0]), float(y_data[0])])

    np.testing.assert_allclose(_xy("Rendezvous"), solution.final_state[:2], rtol=0.0, atol=1e-6)
    np.testing.assert_allclose(_xy("Burn 1"), solution.trajectory_states[0, :2], rtol=0.0, atol=1e-6)
    np.testing.assert_allclose(_xy("Burn 2"), solution.trajectory_states[-1, :2], rtol=0.0, atol=1e-6)

    import matplotlib.pyplot as plt

    plt.close(fig)


@given(two_body_cases())
@_FAST
def test_plot_two_body_trajectory_with_burns_renders_successfully(tmp_path_factory, case) -> None:
    """AC2: the shared plotting core also renders and saves successfully
    for the bounded two-body fallback path's state-history shape, not only
    the CW path, demonstrating one shared implementation serves both.

    Physical rationale: this is a smoke test of the shared-core design
    choice itself (AC2's "one shared plotting implementation... where the
    data shape allows it"), not a physics property of two-body propagation
    (already covered by ``tests/test_physics_properties.py``'s AC4/AC8).

    ICs/units: generated via ``two_body_cases()`` (same domain as
    ``tests/test_cw_state_histories_helpers.py``: mu in [1e13, 1e15]
    m^3/s^2, radius_m in [5e6, 5e7] m, non-degenerate bound initial state),
    propagated into a 20-sample state history via
    ``propagated_two_body_state_history``. Burn delta-v vectors are a fixed
    small arbitrary 3-vector (not physically meaningful here -- this test
    only exercises the plotting path's shape handling, not a real two-body
    rendezvous targeting result, since ``src/twobody.py`` has no two-burn
    targeting solver of its own).

    Expected result: the function returns a ``pathlib.Path`` equal to the
    requested output path, and the saved file exists and starts with the
    PNG magic bytes. Justification: this smoke test only needs to confirm
    the shared core accepts this path's data shape and produces a
    well-formed artifact, not any specific rendered content (that is
    already covered to tight tolerance for the CW path by AC4's test
    above).

    Assumptions/limitations: the two-body path has no dedicated two-burn
    targeting solver in this project, so the plotted "burns" here are an
    arbitrary demonstration vector, not a solved rendezvous maneuver; this
    is explicitly a shared-core shape/rendering smoke test, not a
    two-body-rendezvous-correctness test.
    """
    mu, radius_m, state0, dt = case
    times, states = propagated_two_body_state_history(mu, radius_m, state0, dt)

    output_dir = tmp_path_factory.mktemp("two_body_plot")
    output_path = output_dir / "two_body_trajectory.png"

    burn1_dv_mps = np.array([1.0, 0.0, 0.0])
    burn2_dv_mps = np.array([0.0, 1.0, 0.0])

    saved_path = plot_two_body_trajectory_with_burns(states, burn1_dv_mps, burn2_dv_mps, output_path)

    assert saved_path == output_path
    assert output_path.exists()
    with open(output_path, "rb") as handle:
        header = handle.read(8)
    assert header == b"\x89PNG\r\n\x1a\n"
