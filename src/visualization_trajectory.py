"""Relative-trajectory plot: target, chaser path, burns, and rendezvous (TJC-16.3).

This module renders a direct visualization of an already-computed numeric
result -- it performs no new orbital-mechanics calculation itself. The
shared core, ``plot_relative_trajectory``, accepts plain numpy arrays/
vectors (trajectory positions, burn positions/delta-v vectors, final
position) rather than a solver-specific dataclass, so it can serve both the
CW path (``src/cw.py::solve_cw_rendezvous``'s ``CWRendezvousSolution``) and
the bounded two-body fallback path (``src/twobody.py::propagate_cartesian_state``-
derived state histories), per this task's AC2. Two thin wrappers,
``plot_cw_rendezvous_trajectory`` and ``plot_two_body_trajectory_with_burns``,
extract each path's own fields and call the shared core unchanged.

The plot is a 2D LVLH/RIC in-plane (x, y) view: target at the origin,
chaser path, markers at the two burn-application points with annotated
delta-v arrows (magnitude labeled in text, since a real delta-v vector in
m/s and a relative-position trajectory in m are not on a comparable visual
scale -- arrow *direction* is physically meaningful, arrow *length* is
schematic, rescaled to a fixed fraction of the trajectory's own spatial
extent), and the final rendezvous/terminal point.

A singular-infeasible ``CWRendezvousSolution`` (``feasible=False``, all
burn/trajectory/final-state fields ``None`` per ``src/cw.py``'s documented
contract) is rejected by ``plot_cw_rendezvous_trajectory`` with an explicit
``ValueError`` -- this module never plots a fabricated or partial
trajectory.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.cw import CWRendezvousSolution

# Delta-v annotation arrows are drawn at this fraction of the trajectory's
# own spatial extent (not to physical scale -- see module docstring); the
# actual delta-v magnitude is always given as a text label alongside the
# arrow, so no information is lost to this rescaling.
_DV_ARROW_LENGTH_FRACTION = 0.15


def _schematic_arrow_vector(dv_mps: np.ndarray, reference_length_m: float) -> np.ndarray:
    """Return a 2D arrow vector in the same direction as ``dv_mps``'s
    in-plane (x, y) component, rescaled to a fixed, visually legible
    fraction of ``reference_length_m`` (the trajectory's own spatial
    extent). A zero delta-v or zero reference length yields a zero-length
    arrow (nothing to annotate).
    """
    dv_xy = np.asarray(dv_mps, dtype=float).reshape(-1)[:2]
    norm = float(np.linalg.norm(dv_xy))
    if norm == 0.0 or reference_length_m == 0.0:
        return np.zeros(2)
    return dv_xy / norm * (_DV_ARROW_LENGTH_FRACTION * reference_length_m)


def _annotate_burn(ax: plt.Axes, position_xy: np.ndarray, dv_mps: np.ndarray, reference_length_m: float, label: str, color: str) -> np.ndarray:
    """Draw a burn marker, a schematic delta-v quiver arrow, and a text
    label giving the delta-v's actual magnitude in m/s. Returns the arrow's
    tip point (``position_xy + arrow_xy``) so callers can include it when
    computing explicit axis limits -- ``ax.quiver``/``ax.text`` artists do
    not themselves extend Matplotlib's autoscale ``dataLim``, so without
    this the drawn arrow/label can fall far outside the view established by
    the plotted line/marker data alone (see ``plot_relative_trajectory``'s
    explicit-limits computation).
    """
    arrow_xy = _schematic_arrow_vector(dv_mps, reference_length_m)
    dv_magnitude = float(np.linalg.norm(np.asarray(dv_mps, dtype=float).reshape(-1)))
    ax.quiver(
        position_xy[0], position_xy[1], arrow_xy[0], arrow_xy[1],
        angles="xy", scale_units="xy", scale=1.0, color=color, width=0.005,
    )
    tip_xy = position_xy + arrow_xy
    ax.text(
        tip_xy[0], tip_xy[1],
        f"{label}: {dv_magnitude:.4g} m/s", color=color, fontsize=8,
    )
    return tip_xy


def plot_relative_trajectory(
    trajectory_positions_m: np.ndarray,
    burn1_position_m: np.ndarray,
    burn1_dv_mps: np.ndarray,
    burn2_position_m: np.ndarray,
    burn2_dv_mps: np.ndarray,
    final_position_m: np.ndarray,
    *,
    output_path: Path,
    title: str,
    return_figure: bool = False,
) -> Path | tuple[Path, plt.Figure]:
    """Render a 2D LVLH (x, y) relative-trajectory plot and save it to
    ``output_path`` as a PNG.

    Parameters
    ----------
    trajectory_positions_m:
        ``(N, >=2)`` array of chaser position samples; only the first two
        (x, y) columns are plotted (in-plane LVLH view).
    burn1_position_m, burn2_position_m:
        3-vectors (or any length->=2 vector) giving the two burn-application
        positions.
    burn1_dv_mps, burn2_dv_mps:
        3-vectors giving the delta-v applied at each burn, used for the
        annotated schematic arrow and its magnitude label (see module
        docstring).
    final_position_m:
        The final rendezvous/terminal point position.
    output_path:
        Destination PNG path; parent directories are not created (the
        caller is expected to pass an existing directory, matching this
        project's existing artifact-writing conventions, e.g.
        ``src/workflow.py``).
    title:
        Plot title.
    return_figure:
        If ``True``, also return the created ``matplotlib.figure.Figure``
        (left open, not closed) for callers -- typically tests -- that need
        to inspect the actual rendered ``Axes`` data. If ``False`` (the
        default), the figure is closed after saving.

    Returns
    -------
    pathlib.Path
        ``output_path``, as a ``Path`` (for callers' convenience).
    tuple[pathlib.Path, matplotlib.figure.Figure]
        If ``return_figure`` is ``True``.
    """
    output_path = Path(output_path)
    trajectory = np.asarray(trajectory_positions_m, dtype=float)
    burn1_xy = np.asarray(burn1_position_m, dtype=float).reshape(-1)[:2]
    burn2_xy = np.asarray(burn2_position_m, dtype=float).reshape(-1)[:2]
    final_xy = np.asarray(final_position_m, dtype=float).reshape(-1)[:2]

    xs, ys = trajectory[:, 0], trajectory[:, 1]
    span = float(max(np.ptp(xs), np.ptp(ys), 1.0))

    # Keep the key below the axes.  Tall/narrow equal-scale LVLH paths can
    # place burn annotations near either side, so a side legend can obscure
    # those labels even when it is outside the data rectangle.
    fig, ax = plt.subplots(figsize=(8, 7))
    fig.subplots_adjust(bottom=0.22)
    ax.plot(xs, ys, "-", color="tab:blue", linewidth=1.5, label="Chaser path")
    ax.plot(0.0, 0.0, marker="^", linestyle="None", markersize=10, color="black", label="Target")
    ax.plot(burn1_xy[0], burn1_xy[1], marker="o", linestyle="None", markersize=9, color="tab:orange", label="Burn 1")
    ax.plot(burn2_xy[0], burn2_xy[1], marker="s", linestyle="None", markersize=9, color="tab:red", label="Burn 2")
    ax.plot(final_xy[0], final_xy[1], marker="*", linestyle="None", markersize=14, color="tab:green", label="Rendezvous")

    dv0_tip_xy = _annotate_burn(ax, burn1_xy, burn1_dv_mps, span, "dv0", "tab:orange")
    dv1_tip_xy = _annotate_burn(ax, burn2_xy, burn2_dv_mps, span, "dv1", "tab:red")

    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title(title)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, borderaxespad=0, fontsize=8)

    # Matplotlib's autoscale (dataLim) only tracks plotted line/marker data,
    # not quiver arrows or text; the dv annotations can otherwise fall
    # outside an autoscaled view (observed to cause a Matplotlib/FreeType
    # text-rendering crash for a near-degenerate trajectory whose own
    # extent is far smaller than the schematic arrow length). Limits are
    # computed explicitly from every drawn point, including both arrow
    # tips, with a fixed 10% margin.
    all_x = np.concatenate([xs, [0.0, burn1_xy[0], burn2_xy[0], final_xy[0], dv0_tip_xy[0], dv1_tip_xy[0]]])
    all_y = np.concatenate([ys, [0.0, burn1_xy[1], burn2_xy[1], final_xy[1], dv0_tip_xy[1], dv1_tip_xy[1]]])
    x_min, x_max = float(all_x.min()), float(all_x.max())
    y_min, y_max = float(all_y.min()), float(all_y.max())
    x_pad = 0.1 * max(x_max - x_min, 1e-12)
    y_pad = 0.1 * max(y_max - y_min, 1e-12)
    ax.set_xlim(x_min - x_pad, x_max + x_pad)
    ax.set_ylim(y_min - y_pad, y_max + y_pad)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle=":", linewidth=0.5)

    fig.savefig(output_path, format="png", bbox_inches="tight", pad_inches=0.15)
    if return_figure:
        return output_path, fig
    plt.close(fig)
    return output_path


def plot_cw_rendezvous_trajectory(
    solution: CWRendezvousSolution, output_path: Path, *, return_figure: bool = False
) -> Path | tuple[Path, plt.Figure]:
    """Plot a solved CW rendezvous via the shared ``plot_relative_trajectory``
    core.

    Extracts ``solution.trajectory_states[:, :3]`` as the chaser path,
    ``trajectory_states[0, :3]``/``dv0_mps`` as burn 1,
    ``trajectory_states[-1, :3]``/``dv1_mps`` as burn 2 (CW's terminal
    delta-v corrects velocity only, not position, so burn 2's position is
    the pre-burn-2 trajectory sample -- see
    ``src/cw.py::solve_cw_rendezvous``), and ``final_state[:3]`` as the
    rendezvous point.

    Raises
    ------
    ValueError
        If ``solution.feasible`` is ``False`` (AC3) -- a singular-infeasible
        result has no burn/trajectory/final-state data to plot
        (``src/cw.py``'s documented contract: those fields are ``None``
        only in that case), so this is rejected explicitly rather than
        plotting a fabricated or partial trajectory.
    """
    if not solution.feasible:
        raise ValueError(
            "Cannot plot an infeasible CWRendezvousSolution "
            f"(status={solution.status!r}, reason={solution.reason!r}): "
            "no burns or trajectory were computed for this result."
        )

    trajectory_positions_m = solution.trajectory_states[:, :3]
    burn1_position_m = solution.trajectory_states[0, :3]
    burn2_position_m = solution.trajectory_states[-1, :3]
    final_position_m = solution.final_state[:3]

    return plot_relative_trajectory(
        trajectory_positions_m,
        burn1_position_m,
        solution.dv0_mps,
        burn2_position_m,
        solution.dv1_mps,
        final_position_m,
        output_path=output_path,
        title="CW relative-trajectory rendezvous",
        return_figure=return_figure,
    )


def plot_two_body_trajectory_with_burns(
    trajectory_states: np.ndarray,
    burn1_dv_mps: np.ndarray,
    burn2_dv_mps: np.ndarray,
    output_path: Path,
    *,
    return_figure: bool = False,
) -> Path | tuple[Path, plt.Figure]:
    """Plot a bounded two-body state history via the shared
    ``plot_relative_trajectory`` core (AC2: one shared implementation
    serving both the CW and two-body paths).

    Parameters
    ----------
    trajectory_states:
        ``(N, 6)`` array of inertial Cartesian states (position in columns
        0:3, velocity in 3:6), e.g. from
        ``tests/helpers/cw_state_histories.py::propagated_two_body_state_history``.
    burn1_dv_mps, burn2_dv_mps:
        Delta-v 3-vectors applied at the start and end of the plotted
        history, analogous to the CW wrapper's ``dv0_mps``/``dv1_mps``.
    output_path:
        Destination PNG path.

    Notes
    -----
    The two-body path has no two-burn targeting solver of its own in this
    project (unlike ``src/cw.py::solve_cw_rendezvous``), so there is no
    separate "final rendezvous state" distinct from the trajectory's own
    terminal sample; burn 2's position and the plotted rendezvous point are
    both ``trajectory_states[-1, :3]``.
    """
    trajectory_states = np.asarray(trajectory_states, dtype=float)
    trajectory_positions_m = trajectory_states[:, :3]
    burn1_position_m = trajectory_states[0, :3]
    burn2_position_m = trajectory_states[-1, :3]
    final_position_m = trajectory_states[-1, :3]

    return plot_relative_trajectory(
        trajectory_positions_m,
        burn1_position_m,
        burn1_dv_mps,
        burn2_position_m,
        burn2_dv_mps,
        final_position_m,
        output_path=output_path,
        title="Two-body relative-trajectory with burns",
        return_figure=return_figure,
    )
