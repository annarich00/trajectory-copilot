"""Stage-boundary visualization artifacts for the rendezvous workflow (TJC-16.5).

Thin glue between ``src/workflow.py`` (and ``scripts/rendezvous_visualization_stage.py``,
used by ``.pi/prompts/rendezvous.md``) and the already-built plots:

- ``scene_stage``: TJC-16.2 interactive 3D relative-position scene
  (``src/visualization.py``), generated after formalization/model selection and
  BEFORE the deterministic solve, so it can only show the formalized initial
  relative state (a one-sample history), never a solved path;
- ``trajectory_stage``: TJC-16.3 trajectory/burns plot
  (``src/visualization_trajectory.py``), generated right after the solve and
  BEFORE GMAT execution;
- ``comparison_stage``: TJC-16.4 CW-vs-GMAT comparison plot
  (``src/visualization_comparison.py``), generated after GMAT execution and
  parsing from that same run's ``d_trajectory.txt`` ReportFile output.

No physics, optimization, or plotting logic lives here. Every stage returns one
plain record ``{"stage", "status", "paths", "reason"}`` where ``status`` is
``"generated"`` or ``"not_generated"``; a ``not_generated`` record always carries
a concrete ``reason`` and an empty ``paths`` list. Nothing is ever faked: a
plot whose inputs do not exist (infeasible solve, no GMAT comparison, the
bounded two-body path's missing relative state/burns/history) is reported as
not generated, never approximated.

Time bases for the comparison plot: ``plot_cw_vs_gmat_comparison`` requires the
CW and GMAT histories to share the exact same times and never interpolates.
GMAT's trajectory report samples at its own propagator steps, which differ from
``solve_cw_rendezvous``'s uniform 50-sample grid, so ``comparison_stage``
evaluates the SAME solver's analytic CW state-transition model
(``src/cw.py::propagate_relative_state``, from the post-burn-1 state) at exactly
GMAT's reported times. No sample from either source is interpolated or resampled.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np

from .cw import CWRendezvousSolution, propagate_relative_state
from .gmat_verify import parse_gmat_report
from .visualization import plot_relative_position_3d
from .visualization_comparison import plot_cw_vs_gmat_comparison
from .visualization_trajectory import plot_cw_rendezvous_trajectory

SCENE_STAGE = "relative_position_3d_scene"
TRAJECTORY_STAGE = "trajectory_burns_plot"
COMPARISON_STAGE = "verification_comparison_plot"

VisualizationRecord = dict


def _generated(stage: str, paths: Sequence[str]) -> VisualizationRecord:
    return {"stage": stage, "status": "generated", "paths": [str(path) for path in paths], "reason": None}


def _not_generated(stage: str, reason: str) -> VisualizationRecord:
    return {"stage": stage, "status": "not_generated", "paths": [], "reason": reason}


def scene_stage(
    initial_relative_state: Sequence[float] | None, reference_radius_m: float | None, output_dir: Path,
) -> VisualizationRecord:
    """3D scene from the formalized initial LVLH relative state (a single sample at t=0)."""
    if initial_relative_state is None or reference_radius_m is None:
        return _not_generated(
            SCENE_STAGE,
            "bounded two-body fallback case carries only an inertial Cartesian state and coast duration; it has no "
            "initial_relative_state (LVLH) or reference radius to render, and deriving a relative state would require "
            "an unspecified target state.",
        )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    state0 = np.asarray(initial_relative_state, dtype=float).reshape(1, 6)
    result = plot_relative_position_3d(
        state0, np.array([0.0]), float(reference_radius_m), output_path=output_dir / "relative_position_3d.html",
    )
    return _generated(SCENE_STAGE, [result.output_path])


def trajectory_stage(solution: CWRendezvousSolution, output_dir: Path) -> VisualizationRecord:
    """Trajectory/burns plot from a just-completed CW solve."""
    if not solution.feasible:
        return _not_generated(
            TRAJECTORY_STAGE,
            f"CW targeting infeasible (status={solution.status!r}): no burns or trajectory were computed to plot.",
        )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = plot_cw_rendezvous_trajectory(solution, output_dir / "trajectory_burns_plot.png")
    return _generated(TRAJECTORY_STAGE, [path])


def two_body_trajectory_stage() -> VisualizationRecord:
    return _not_generated(
        TRAJECTORY_STAGE,
        "bounded two-body fallback is a single coast propagation to a final state: it has no CW burns (dv0/dv1) and "
        "no sampled state history, so a trajectory/burns plot would fabricate both.",
    )


def two_body_comparison_stage() -> VisualizationRecord:
    return _not_generated(
        COMPARISON_STAGE,
        "bounded two-body fallback keeps only the propagated final state, not a solver state history, so there is no "
        "time-aligned history to compare against GMAT beyond the existing final-state comparison.",
    )


def comparison_stage(
    *,
    case_id: str,
    solution: CWRendezvousSolution | None,
    initial_relative_state: Sequence[float],
    comparison_status: str,
    pos_tol_m: float,
    vel_tol_mps: float,
    gmat_trajectory_report: Path,
    output_dir: Path,
) -> VisualizationRecord:
    """CW-vs-GMAT comparison plot from this run's parsed GMAT trajectory report."""
    if solution is None or not solution.feasible:
        return _not_generated(COMPARISON_STAGE, "CW targeting infeasible: no GMAT run or comparison was performed.")
    if comparison_status == "INCOMPLETE":
        return _not_generated(
            COMPARISON_STAGE,
            "comparison status is INCOMPLETE: GMAT never produced a verified final-state comparison for this run, "
            "so no GMAT trace is drawn.",
        )
    gmat_report = parse_gmat_report(Path(gmat_trajectory_report), expect_single_row=False)
    if not gmat_report.ok:
        return _not_generated(COMPARISON_STAGE, f"GMAT trajectory report was not parsed: {gmat_report.reason}")

    state0 = np.asarray(initial_relative_state, dtype=float).reshape(6)
    post_burn1_state = np.hstack([state0[:3], state0[3:] + solution.dv0_mps])
    cw_times_s = np.array(gmat_report.times_s, dtype=float)
    cw_states_si = np.array(
        [propagate_relative_state(post_burn1_state, solution.mean_motion_radps, float(t)) for t in cw_times_s]
    )
    try:
        plot = plot_cw_vs_gmat_comparison(
            cw_times_s, cw_states_si, gmat_report,
            comparison_status=comparison_status, pos_tol_m=pos_tol_m, vel_tol_mps=vel_tol_mps,
            output_dir=Path(output_dir), case_id=case_id,
        )
    except ValueError as exc:
        return _not_generated(COMPARISON_STAGE, f"comparison plot refused: {exc}")
    return _generated(COMPARISON_STAGE, [plot.trajectory_plot_path, plot.error_history_plot_path])
