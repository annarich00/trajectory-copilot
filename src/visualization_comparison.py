"""CW/two-body-vs-GMAT verification comparison plots (TJC-16.4).

``src/gmat_verify.py::compare_gmat_final_state`` already compares one
*final* CW/two-body state to one *final* GMAT-parsed state at declared
tolerances; ``src/verification_report.py::UnifiedVerificationReport``
already carries that single-point numeric comparison. This module adds no
new physics or comparison logic -- it only renders, for one already-solved/
already-parsed case, the same comparison extended visually across the
*whole* time history the chief/deputy or two-body case actually ran over:

- an overlaid position-trajectory plot (CW/two-body prediction vs. the
  independently parsed GMAT report, same axes), and
- a position-error-magnitude-vs-time and velocity-error-magnitude-vs-time
  plot, computed pointwise from the two already-parsed/solved state arrays
  (``||cw_state[i][:3] - gmat_state[i][:3]||`` / the velocity analogue --
  the exact same error definition ``compare_gmat_final_state`` already uses
  at its one final point), with the already-declared ``pos_tol_m``/
  ``vel_tol_mps`` drawn as a horizontal reference line so pass/fail is
  visually apparent across the whole history, not just at the end.

New module (not ``src/visualization.py``) to avoid merge conflicts with the
sibling TJC-16.2 (interactive 3D relative-position scene) and TJC-16.3
(annotated LVLH trajectory plot) subtasks, each developed in a separate
worktree and each free to add their own ``src/visualization*.py`` module
without colliding with this one.

Library choice: matplotlib (TJC-16.1's own stated reasoning for this
subtask -- richer annotated static 2D/3D plotting, native PNG save, no new
runtime JS dependency for artifacts that are mostly viewed as images during
a demo), using the non-interactive ``Agg`` backend so this module never
requires a display to run (consistent with this sandboxed environment's own
headless-test conventions elsewhere in this project).

Core invariant (AC3), mirroring ``src/verification_report.py``'s own
"never a false PASS"/VERIFIED-vs-solver-only distinction: this module never
draws a GMAT trace that was not actually, successfully parsed. It raises
``ValueError`` immediately -- never silently falling back to an empty or
placeholder plot -- when:

- ``gmat_report.ok`` is ``False`` (GMAT's ReportFile output was missing,
  empty, the wrong shape, or non-numeric -- the ``MALFORMED_OUTPUT`` failure
  mode; there is no real parsed GMAT state history to plot at all), or
- ``comparison_status == "INCOMPLETE"`` -- the literal status string
  ``assemble_verification_report`` assigns when no GMAT comparison was ever
  performed (``comparison is None``). AC3 is worded as "INCOMPLETE/
  UNAVAILABLE"; reading ``assemble_verification_report`` confirms this
  codebase has no separate ``"UNAVAILABLE"`` status literal anywhere, so
  this function's explicit-rejection check is against the one status
  string this codebase actually produces for "no comparison was made".

This module also never silently aligns two different time bases onto each
other (AC4): ``cw_times_s`` and ``gmat_report.times_s`` must be the exact
same array (same shape, matching values), or a ``ValueError`` is raised --
no interpolation or resampling is ever attempted.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Headless by construction: this module never requires a display.
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .gmat_verify import GMATReportParseResult  # noqa: E402


@dataclass(frozen=True)
class ComparisonPlotResult:
    """Artifacts and the underlying computed error histories for one case.

    ``position_error_m``/``velocity_error_mps`` are the exact pointwise
    error-magnitude arrays actually drawn on ``error_history_plot_path``,
    exposed directly so a caller (or a test) can check them without
    re-parsing the saved image.
    """

    trajectory_plot_path: str
    error_history_plot_path: str
    position_error_m: np.ndarray
    velocity_error_mps: np.ndarray


def plot_cw_vs_gmat_comparison(
    cw_times_s: np.ndarray,
    cw_states_si: np.ndarray,
    gmat_report: GMATReportParseResult,
    *,
    comparison_status: str,
    pos_tol_m: float,
    vel_tol_mps: float,
    output_dir: Path,
    case_id: str,
) -> ComparisonPlotResult:
    """Render and save the CW/two-body-vs-GMAT comparison artifacts.

    ``cw_times_s``/``cw_states_si`` are the CW or two-body solver's own
    time history (``cw_states_si`` an ``(N, 6)`` ``[x, y, z, x_dot, y_dot,
    z_dot]`` SI-unit array, matching this project's state-ordering
    convention elsewhere, e.g. ``src/cw.py::CW_RENDEZVOUS_STATE_ORDERING``).
    ``gmat_report`` is a ``src/gmat_verify.py::parse_inertial_report``/
    ``parse_gmat_report`` result for the *same* case. ``pos_tol_m``/
    ``vel_tol_mps`` must be the same declared tolerances already passed to
    ``src/gmat_verify.py::compare_gmat_final_state`` for this case (this
    function draws them as reference lines; it does not invent new ones).

    Raises ``ValueError`` (see module docstring) when ``gmat_report.ok`` is
    ``False``, when ``comparison_status == "INCOMPLETE"``, or when
    ``cw_times_s``/``gmat_report.times_s`` are not the same time base. No
    files are written in any of those cases.
    """
    if comparison_status == "INCOMPLETE":
        raise ValueError(
            "Refusing to plot a CW-vs-GMAT comparison: comparison_status is 'INCOMPLETE' "
            "(no GMAT-vs-CW numerical comparison was performed for this case). Drawing a GMAT "
            "trace here would fabricate a comparison that never actually happened."
        )
    if not gmat_report.ok:
        raise ValueError(
            f"Refusing to plot a CW-vs-GMAT comparison: the GMAT report is not ok (ok=False); "
            f"reason: {gmat_report.reason}. There is no real parsed GMAT state history to plot."
        )

    cw_times_s = np.asarray(cw_times_s, dtype=float)
    cw_states_si = np.asarray(cw_states_si, dtype=float)
    gmat_times_s = np.asarray(gmat_report.times_s, dtype=float)
    gmat_states_si = np.asarray(gmat_report.states_si, dtype=float)

    if cw_times_s.shape != gmat_times_s.shape or not np.array_equal(cw_times_s, gmat_times_s):
        raise ValueError(
            "Refusing to plot a CW-vs-GMAT comparison: cw_times_s and gmat_report.times_s are "
            "different time bases (different shape or values). This function never interpolates "
            "or otherwise re-aligns mismatched time bases onto each other; the caller must supply "
            "two state histories already sampled at the exact same times."
        )
    if cw_states_si.shape != gmat_states_si.shape:
        raise ValueError(
            f"cw_states_si shape {cw_states_si.shape} does not match gmat_report.states_si shape "
            f"{gmat_states_si.shape}; both must be the same (N, 6) shape for the same time base."
        )

    position_error_m = np.linalg.norm(cw_states_si[:, :3] - gmat_states_si[:, :3], axis=1)
    velocity_error_mps = np.linalg.norm(cw_states_si[:, 3:] - gmat_states_si[:, 3:], axis=1)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    trajectory_plot_path = output_dir / f"{case_id}_cw_vs_gmat_trajectory.png"
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(cw_states_si[:, 0], cw_states_si[:, 1], cw_states_si[:, 2], label="CW/two-body prediction", color="tab:blue")
    ax.plot(gmat_states_si[:, 0], gmat_states_si[:, 1], gmat_states_si[:, 2], label="GMAT (independent)", color="tab:orange", linestyle="--")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_zlabel("z [m]")
    ax.set_title(f"CW/two-body vs. GMAT trajectory comparison -- case '{case_id}'")
    ax.legend()
    fig.tight_layout()
    fig.savefig(trajectory_plot_path)
    plt.close(fig)

    error_history_plot_path = output_dir / f"{case_id}_cw_vs_gmat_error_history.png"
    fig, (ax_pos, ax_vel) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    ax_pos.plot(cw_times_s, position_error_m, color="tab:red", label="position error magnitude")
    ax_pos.axhline(pos_tol_m, color="black", linestyle=":", label=f"position tolerance ({pos_tol_m} m)")
    ax_pos.set_ylabel("position error [m]")
    ax_pos.set_title(f"Position/velocity error history -- case '{case_id}' (status: {comparison_status})")
    ax_pos.legend()

    ax_vel.plot(cw_times_s, velocity_error_mps, color="tab:red", label="velocity error magnitude")
    ax_vel.axhline(vel_tol_mps, color="black", linestyle=":", label=f"velocity tolerance ({vel_tol_mps} m/s)")
    ax_vel.set_xlabel("time [s]")
    ax_vel.set_ylabel("velocity error [m/s]")
    ax_vel.legend()
    fig.tight_layout()
    fig.savefig(error_history_plot_path)
    plt.close(fig)

    return ComparisonPlotResult(
        trajectory_plot_path=str(trajectory_plot_path),
        error_history_plot_path=str(error_history_plot_path),
        position_error_m=position_error_m,
        velocity_error_mps=velocity_error_mps,
    )
