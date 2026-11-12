"""Interactive 3D relative-position visualization of target and chaser (TJC-16.2).

``plot_relative_position_3d`` turns an already-computed LVLH relative-state
time history (the same ``(N, 6)`` ``[x, y, z, xdot, ydot, zdot]`` array shape
produced by ``src/cw.py::solve_cw_rendezvous``'s ``trajectory_states`` or by
repeated calls to ``src/twobody.py::propagate_cartesian_state``) into an
interactive Plotly 3D scene for a live demo: a representative, untextured
Earth sphere, the target held at one fixed, illustrative circular-orbit
location, and the chaser traced out by the EXACT relative offset from the
supplied history at each sampled time.

Illustrative vs. authoritative, by construction (never blurred):

- The only illustrative input is ``target_orbit_radius_m`` -- a radius used
  solely to pick *some* fixed point in inertial space to anchor the scene
  around Earth (the target is placed on the inertial +x axis with velocity
  along +y, matching ``src/verify.py::_chief_circular_state``'s convention).
  This function never requires, accepts, or fabricates a real TLE, ephemeris
  state, or epoch; there is no time-of-day/longitude/ground-track meaning to
  that placement, and the rendered figure says so directly (title and a
  dedicated annotation), plus every illustrative trace is named
  ``"... (illustrative anchor)"``.
- The chaser's offset from that fixed target point is always the exact
  rotated relative position from ``trajectory_states[:, :3]`` -- nothing
  about the chaser's position is illustrative or approximated. Its trace is
  named ``"chaser (authoritative relative offset)"``.

LVLH-to-inertial rotation reuses ``src/verify.py::_lvlh_basis`` (the same
basis construction already used elsewhere in this project for exactly this
conversion, see ``src/verify.py::_rel_lvlh_to_absolute``) rather than
re-deriving the rotation here: ``r_mat``'s columns are
``(r_hat, t_hat, h_hat)`` in inertial coordinates for the illustrative
circular chief, consistent with ``src/cw.py``'s documented LVLH convention
(x radial outward, y along-track, z cross-track).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from .verify import LVLHTransformationError, _lvlh_basis

ROOT = Path(__file__).resolve().parents[1]

# Mirrors the repo's persistent artifact convention: a discoverable
# directory under artifacts/ at the repo root.
DEFAULT_OUTPUT_DIR = ROOT / "artifacts/visualizations"
DEFAULT_OUTPUT_FILENAME = "relative_position_3d.html"

# WGS84-ish mean Earth radius, for a representative, intentionally
# untextured sphere -- not a claim of surface detail or real imagery.
EARTH_RADIUS_M = 6_378_137.0

TARGET_TRACE_NAME = "target (illustrative anchor)"
CHASER_TRACE_NAME = "chaser (authoritative relative offset)"
EARTH_TRACE_NAME = "Earth (illustrative, untextured)"

ILLUSTRATIVE_ANNOTATION_TEXT = (
    "ILLUSTRATIVE SCENE ANCHORING ONLY: Earth size/target orbital placement "
    "around it use no real TLE, ephemeris, or epoch data -- they only give "
    "this scene a fixed point in space to render around. The chaser marker "
    "path IS the exact relative position from the supplied state history."
)


@dataclass(frozen=True)
class RelativePositionVisualization:
    """Result of rendering one relative-position 3D scene.

    ``figure`` is the live ``plotly.graph_objects.Figure`` (inspectable
    directly, e.g. by a test pulling trace x/y/z arrays back out);
    ``output_path`` is where the standalone HTML artifact was written via
    ``fig.write_html``, openable directly in a browser with no running
    Python session.
    """

    figure: go.Figure
    output_path: Path


def _validate_trajectory(trajectory_states: np.ndarray, trajectory_times_s: np.ndarray) -> np.ndarray:
    states = np.asarray(trajectory_states, dtype=float)
    if states.ndim != 2 or states.shape[1] != 6 or states.shape[0] < 1:
        raise ValueError(
            "trajectory_states must be a non-empty (N, 6) array of "
            "[x, y, z, xdot, ydot, zdot] LVLH relative states; got shape "
            f"{np.asarray(trajectory_states).shape}."
        )
    if not np.isfinite(states).all():
        raise ValueError("trajectory_states must contain only finite values; NaN/inf relative states are rejected, never silently rendered.")
    times = np.asarray(trajectory_times_s, dtype=float).reshape(-1)
    if times.shape[0] != states.shape[0]:
        raise ValueError(f"trajectory_times_s length ({times.shape[0]}) must match trajectory_states length ({states.shape[0]}).")
    if not np.isfinite(times).all():
        raise ValueError("trajectory_times_s must contain only finite values.")
    return states


def _illustrative_chief_inertial_state(target_orbit_radius_m: float) -> tuple[np.ndarray, np.ndarray]:
    """Return a fixed, illustrative ``(chief_pos, chief_vel)`` inertial state.

    Placed on the inertial +x axis with velocity along +y, the same
    convention used by ``src/verify.py::_chief_circular_state`` for its own
    illustrative circular reference orbit. Only the direction of
    ``chief_vel`` matters here (it fixes which axis becomes along-track for
    ``_lvlh_basis``); this function never derives or needs an orbital speed,
    period, or epoch.
    """
    if not np.isfinite(target_orbit_radius_m) or target_orbit_radius_m <= 0:
        raise ValueError("target_orbit_radius_m must be a positive finite illustrative radius in m.")
    chief_pos = np.array([target_orbit_radius_m, 0.0, 0.0])
    chief_vel = np.array([0.0, 1.0, 0.0])
    return chief_pos, chief_vel


def _earth_sphere_trace() -> go.Surface:
    u = np.linspace(0.0, 2.0 * np.pi, 30)
    v = np.linspace(0.0, np.pi, 30)
    x = EARTH_RADIUS_M * np.outer(np.cos(u), np.sin(v))
    y = EARTH_RADIUS_M * np.outer(np.sin(u), np.sin(v))
    z = EARTH_RADIUS_M * np.outer(np.ones_like(u), np.cos(v))
    return go.Surface(
        x=x, y=y, z=z,
        name=EARTH_TRACE_NAME,
        colorscale=[[0.0, "rgb(30,90,170)"], [1.0, "rgb(30,90,170)"]],
        showscale=False,
        opacity=0.85,
        hoverinfo="skip",
    )


def plot_relative_position_3d(
    trajectory_states: np.ndarray,
    trajectory_times_s: np.ndarray,
    target_orbit_radius_m: float,
    *,
    output_path: Path | str | None = None,
) -> RelativePositionVisualization:
    """Render an interactive 3D target/chaser relative-position scene.

    Parameters
    ----------
    trajectory_states:
        ``(N, 6)`` array of ``[x, y, z, xdot, ydot, zdot]`` LVLH relative
        states in SI units (meters, m/s), the same shape/convention as
        ``src/cw.py::CWRendezvousSolution.trajectory_states`` or a stacked
        history of ``src/twobody.py::propagate_cartesian_state`` outputs.
        ``N`` must be at least 1 and every value must be finite; an empty
        or non-finite history is rejected with ``ValueError`` rather than
        silently rendered.
    trajectory_times_s:
        ``(N,)`` array of sample times in seconds, matching
        ``trajectory_states``'s length. Only used for hover labels, not for
        any dynamics computation here.
    target_orbit_radius_m:
        Positive, illustrative circular-orbit radius [m] used only to place
        a fixed anchor point for the scene (see module docstring); never a
        real ephemeris/epoch value.
    output_path:
        Where to write the standalone HTML artifact (``fig.write_html``).
        Defaults to ``artifacts/visualizations/relative_position_3d.html``
        at the repo root, created if missing.

    Returns
    -------
    RelativePositionVisualization
        The live ``Figure`` plus the HTML artifact path actually written.
    """
    states = _validate_trajectory(trajectory_states, trajectory_times_s)
    times = np.asarray(trajectory_times_s, dtype=float).reshape(-1)

    chief_pos, chief_vel = _illustrative_chief_inertial_state(target_orbit_radius_m)
    try:
        r_mat, _ = _lvlh_basis(chief_pos, chief_vel)
    except LVLHTransformationError as exc:  # pragma: no cover - chief_pos/vel are fixed and always well-formed above
        raise ValueError(f"could not construct an illustrative LVLH anchoring frame: {exc}") from exc

    # Rotate every sampled LVLH relative position into the illustrative
    # inertial frame and add it to the fixed target anchor point, exactly
    # as src/verify.py::_rel_lvlh_to_absolute rotates a relative position
    # (r_mat @ r_rel_lvlh), applied row-wise here for the whole (N, 3) array:
    # inertial_row = lvlh_row @ r_mat.T.
    relative_positions_lvlh = states[:, :3]
    relative_positions_inertial = relative_positions_lvlh @ r_mat.T
    chaser_positions_inertial = chief_pos + relative_positions_inertial

    fig = go.Figure()
    fig.add_trace(_earth_sphere_trace())
    fig.add_trace(
        go.Scatter3d(
            x=[float(chief_pos[0])], y=[float(chief_pos[1])], z=[float(chief_pos[2])],
            mode="markers",
            name=TARGET_TRACE_NAME,
            marker=dict(size=7, color="orange"),
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=chaser_positions_inertial[:, 0],
            y=chaser_positions_inertial[:, 1],
            z=chaser_positions_inertial[:, 2],
            mode="lines+markers",
            name=CHASER_TRACE_NAME,
            marker=dict(size=3, color="red"),
            line=dict(color="red"),
            text=[f"t={t:.1f} s" for t in times],
            hovertemplate="%{text}<br>x=%{x:.1f} y=%{y:.1f} z=%{z:.1f} m<extra></extra>",
        )
    )

    fig.update_layout(
        title=(
            f"Relative position (target/chaser) -- ILLUSTRATIVE anchoring at "
            f"radius={target_orbit_radius_m:,.0f} m; chaser offset is the exact relative state"
        ),
        scene=dict(
            xaxis_title="x [m] (inertial, illustrative anchor)",
            yaxis_title="y [m] (inertial, illustrative anchor)",
            zaxis_title="z [m] (inertial, illustrative anchor)",
            aspectmode="data",
        ),
        annotations=[
            dict(
                text=ILLUSTRATIVE_ANNOTATION_TEXT,
                xref="paper", yref="paper",
                x=0.5, y=-0.08,
                showarrow=False,
                font=dict(size=11),
            )
        ],
    )

    if output_path is None:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        resolved_output_path = DEFAULT_OUTPUT_DIR / DEFAULT_OUTPUT_FILENAME
    else:
        resolved_output_path = Path(output_path)
        resolved_output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(resolved_output_path))

    return RelativePositionVisualization(figure=fig, output_path=resolved_output_path)
