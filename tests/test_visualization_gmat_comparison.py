"""Tests for src/visualization_comparison.py (TJC-16.4).

The CW-vs-two-body-vs-GMAT comparison plot renders two artifacts for one
already-solved/already-parsed case: (1) overlaid position trajectories from
the CW/two-body solver and the independently-parsed GMAT report, and (2) a
position-error/velocity-error-magnitude-vs-time plot with the already-
declared ``src/gmat_verify.py::compare_gmat_final_state`` tolerances drawn as
a horizontal reference line. This module computes no new physics: every
plotted error value is the pointwise ``||cw[i] - gmat[i]||`` of two already-
parsed/solved state histories, matching ``compare_gmat_final_state``'s own
single-point position/velocity error definition extended across the whole
time history.

Hypothesis strategy conventions follow ``tests/helpers/cw_state_histories.py``
(TJC-16.1) and ``tests/test_physics_properties.py`` (TJC-6): generated inputs
stay within each governing module's documented validity domain, with a
distinct strategy here (``matching_cw_gmat_histories``) because this task's
generated-input shape is a pair of time-aligned state histories (one
"CW/two-body", one synthetic "GMAT"), not a single physics case -- the
*physical* history is built from the shared ``two_body_cases()``/
``propagated_two_body_state_history`` helper (any non-degenerate finite
state-history source is equally valid input to this purely-geometric
plotting function; the two-body helper is reused here rather than
duplicated), and the synthetic "GMAT" history is the same times_s array
paired with a small generated additive perturbation, simulating a real but
small discrepancy between an independent GMAT run and the CW/two-body
prediction.

INCOMPLETE/UNAVAILABLE terminology note: AC3 is worded as "INCOMPLETE/
UNAVAILABLE". Reading ``src/verification_report.py::assemble_verification_report``
confirms the only such status string this codebase actually produces is the
literal ``"INCOMPLETE"`` (``comparison_status = comparison.status if
comparison is not None else "INCOMPLETE"``); there is no separate
``"UNAVAILABLE"`` status literal anywhere in this codebase. The tests below
therefore exercise rejection of ``comparison_status == "INCOMPLETE"``
directly, which is the actual status string AC3 describes in this codebase
today.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gmat_verify import GMATReportParseResult  # noqa: E402
from src.visualization_comparison import plot_cw_vs_gmat_comparison  # noqa: E402
from tests.helpers.cw_state_histories import (  # noqa: E402
    propagated_two_body_state_history,
    two_body_cases,
)

# Small additive position/velocity perturbation, simulating a real (but
# small, within-tolerance-or-just-over) discrepancy between an independently
# parsed GMAT report and the CW/two-body prediction being verified -- never
# zero (a zero perturbation would not exercise the error-history computation
# meaningfully) and kept well below the generated two-body state's own scale.
_POSITION_PERTURBATION_M = st.floats(min_value=-50.0, max_value=50.0, allow_nan=False, allow_infinity=False)
_VELOCITY_PERTURBATION_MPS = st.floats(min_value=-0.05, max_value=0.05, allow_nan=False, allow_infinity=False)

_FAST = settings(max_examples=25, deadline=2000)
# Each example here actually renders and saves two real matplotlib figures
# (~1.3s/call observed), unlike _FAST's pure-numeric checks elsewhere in this
# project's Hypothesis suite; mirrors tests/test_physics_properties.py's own
# _SLOW_ORACLE convention for property tests whose per-example cost is
# dominated by genuine work rather than input generation.
_SLOW_PLOTTING = settings(max_examples=10, deadline=8000)


@st.composite
def matching_cw_gmat_histories(draw):
    """Generate a ``(cw_times_s, cw_states_si, gmat_report)`` triple sharing
    one time base, where ``gmat_report`` is a synthetic, already-"parsed"
    ``GMATReportParseResult`` built by perturbing the CW/two-body history by
    a small generated per-sample delta (simulating genuine GMAT-vs-CW
    discrepancy), ready for ``plot_cw_vs_gmat_comparison``.
    """
    mu, radius_m, state0, dt = draw(two_body_cases())
    cw_times_s, cw_states_si = propagated_two_body_state_history(mu, radius_m, state0, dt)
    n_samples = cw_states_si.shape[0]
    position_delta = np.array(
        [[draw(_POSITION_PERTURBATION_M) for _ in range(3)] for _ in range(n_samples)]
    )
    velocity_delta = np.array(
        [[draw(_VELOCITY_PERTURBATION_MPS) for _ in range(3)] for _ in range(n_samples)]
    )
    gmat_states_si = cw_states_si + np.hstack([position_delta, velocity_delta])
    gmat_report = GMATReportParseResult(
        True, "parsed synthetic GMAT report for test", cw_times_s.copy(), gmat_states_si
    )
    return cw_times_s, cw_states_si, gmat_report


def _good_gmat_report(times_s: np.ndarray, states_si: np.ndarray) -> GMATReportParseResult:
    return GMATReportParseResult(True, "parsed synthetic GMAT report for test", times_s, states_si)


# --- AC4: error-history values match an independently recomputed diff -----


@given(matching_cw_gmat_histories())
@_SLOW_PLOTTING
def test_error_histories_equal_independently_recomputed_pointwise_difference(case) -> None:
    """The position/velocity error-magnitude histories the function actually
    plots equal ``||cw[i][:3] - gmat[i][:3]||``/``||cw[i][3:] - gmat[i][3:]||``
    computed fresh here (not by calling into the function's own internals),
    to float64 numerical tolerance.

    Physical rationale: this mirrors ``src/gmat_verify.py
    ::compare_gmat_final_state``'s own single-final-point error definition
    (``np.linalg.norm`` of the position/velocity difference), extended
    pointwise across the whole time history; the function under test must
    not independently "recompute" physics, only report this same pointwise
    comparison at every sample.

    Uses a plain ``tempfile.TemporaryDirectory`` (not the ``tmp_path``
    pytest fixture) as the output directory: ``tmp_path`` is function-scoped
    and Hypothesis's own health check correctly flags it as not reset
    between generated examples within one ``@given`` test, whereas a fresh
    ``TemporaryDirectory`` per call is isolated per generated example.
    """
    cw_times_s, cw_states_si, gmat_report = case
    with tempfile.TemporaryDirectory() as output_dir:
        result = plot_cw_vs_gmat_comparison(
            cw_times_s, cw_states_si, gmat_report,
            comparison_status="PASS", pos_tol_m=1.0, vel_tol_mps=0.001,
            output_dir=Path(output_dir), case_id="hypothesis-case",
        )

        expected_position_error_m = np.linalg.norm(cw_states_si[:, :3] - gmat_report.states_si[:, :3], axis=1)
        expected_velocity_error_mps = np.linalg.norm(cw_states_si[:, 3:] - gmat_report.states_si[:, 3:], axis=1)

        np.testing.assert_allclose(result.position_error_m, expected_position_error_m, rtol=1e-12, atol=1e-9)
        np.testing.assert_allclose(result.velocity_error_mps, expected_velocity_error_mps, rtol=1e-12, atol=1e-12)


# --- AC4: mismatched time bases are rejected, never interpolated ----------


@given(matching_cw_gmat_histories())
@_SLOW_PLOTTING
def test_mismatched_time_bases_are_rejected_not_interpolated(case) -> None:
    """A GMAT report whose ``times_s`` differs from the CW/two-body
    history's own ``times_s`` must raise ``ValueError`` -- the function must
    never silently interpolate or otherwise misalign two different time
    bases onto each other.
    """
    cw_times_s, cw_states_si, gmat_report = case
    mismatched_times_s = gmat_report.times_s + 1.0  # Shifts every sample time; same shape, different base.
    mismatched_report = _good_gmat_report(mismatched_times_s, gmat_report.states_si)

    with tempfile.TemporaryDirectory() as output_dir:
        with pytest.raises(ValueError, match="time base"):
            plot_cw_vs_gmat_comparison(
                cw_times_s, cw_states_si, mismatched_report,
                comparison_status="PASS", pos_tol_m=1.0, vel_tol_mps=0.001,
                output_dir=Path(output_dir), case_id="hypothesis-case",
            )


# --- AC3: INCOMPLETE comparison status raises, never draws a fabricated plot


def test_incomplete_comparison_status_raises_and_writes_no_artifact(tmp_path) -> None:
    """``comparison_status == 'INCOMPLETE'`` (the actual status string
    ``src/verification_report.py::assemble_verification_report`` uses when
    no GMAT comparison was performed -- see this module's docstring for why
    there is no separate 'UNAVAILABLE' literal in this codebase) must raise
    an explicit error and must not write any plot file: a fabricated GMAT
    trace is never drawn when GMAT verification did not actually happen.
    """
    times_s = np.linspace(0.0, 100.0, 5)
    states_si = np.zeros((5, 6))
    gmat_report = _good_gmat_report(times_s, states_si.copy())

    with pytest.raises(ValueError, match="INCOMPLETE"):
        plot_cw_vs_gmat_comparison(
            times_s, states_si, gmat_report,
            comparison_status="INCOMPLETE", pos_tol_m=1.0, vel_tol_mps=0.001,
            output_dir=tmp_path, case_id="incomplete-case",
        )

    assert list(tmp_path.iterdir()) == []


def test_unparsed_gmat_report_raises_and_writes_no_artifact(tmp_path) -> None:
    """A GMAT report with ``ok=False`` (GMAT ran but produced unparsable
    output -- the ``MALFORMED_OUTPUT`` failure mode) must also raise,
    independent of whatever ``comparison_status`` string is passed: there is
    no real GMAT state history to plot.
    """
    times_s = np.linspace(0.0, 100.0, 5)
    states_si = np.zeros((5, 6))
    bad_gmat_report = GMATReportParseResult(False, "GMAT report file is empty: /tmp/x.txt", None, None)

    with pytest.raises(ValueError, match="ok=False|not ok|could not be parsed"):
        plot_cw_vs_gmat_comparison(
            times_s, states_si, bad_gmat_report,
            comparison_status="PASS", pos_tol_m=1.0, vel_tol_mps=0.001,
            output_dir=tmp_path, case_id="malformed-case",
        )

    assert list(tmp_path.iterdir()) == []


# --- AC1/AC2/AC6: happy path writes real artifacts -------------------------


def test_happy_path_writes_trajectory_and_error_history_artifacts(tmp_path) -> None:
    """A genuine, well-formed matching CW/GMAT pair produces two real,
    non-empty PNG files (overlaid trajectory comparison, and position/
    velocity error-history-with-tolerance-line), and the returned paths
    point at exactly those files.
    """
    times_s = np.linspace(0.0, 600.0, 30)
    cw_states_si = np.column_stack(
        [
            7_000_000.0 * np.cos(times_s / 900.0),
            7_000_000.0 * np.sin(times_s / 900.0),
            np.zeros_like(times_s),
            -7_000_000.0 / 900.0 * np.sin(times_s / 900.0),
            7_000_000.0 / 900.0 * np.cos(times_s / 900.0),
            np.zeros_like(times_s),
        ]
    )
    gmat_states_si = cw_states_si + 0.5  # Small uniform offset simulating real discrepancy.
    gmat_report = _good_gmat_report(times_s, gmat_states_si)

    result = plot_cw_vs_gmat_comparison(
        times_s, cw_states_si, gmat_report,
        comparison_status="PASS", pos_tol_m=1.0, vel_tol_mps=0.001,
        output_dir=tmp_path, case_id="happy-case",
    )

    trajectory_path = Path(result.trajectory_plot_path)
    error_history_path = Path(result.error_history_plot_path)
    assert trajectory_path.is_file() and trajectory_path.stat().st_size > 0
    assert error_history_path.is_file() and error_history_path.stat().st_size > 0
    assert trajectory_path.suffix == ".png"
    assert error_history_path.suffix == ".png"
    assert result.position_error_m.shape == (30,)
    assert result.velocity_error_mps.shape == (30,)
