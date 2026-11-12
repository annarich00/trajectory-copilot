# `artifacts/visualization/` — persistent 3D relative-position scene output

This is the **default, persistent, discoverable** output directory for
`src/visualization.py::plot_relative_position_3d` (TJC-16.2), mirroring the
convention already established by `artifacts/cw_gmat_slice/` (TJC-2).

Calling `plot_relative_position_3d(...)` without an explicit `output_path`
writes the rendered interactive 3D scene here as a standalone HTML file:

- `relative_position_3d.html` — the Plotly figure (`fig.write_html(...)`),
  openable directly in a browser during a live demo with no running Python
  session.

## Why this directory is only partially tracked in git

This directory's contents (other than this README) are deliberately
**gitignored** (`artifacts/visualization/*` in `.gitignore`, with this
`README.md` explicitly un-ignored): real per-run HTML output is regenerated
every time the plotting function runs and would otherwise bloat repository
history with ephemeral rendered output that is not meant to be reviewed as
source. This README is the one tracked file, so the directory and its
convention are discoverable from a fresh clone without having run anything.

## Reproducing a run

```python
from src.cw import solve_cw_rendezvous
from src.visualization import plot_relative_position_3d

solution = solve_cw_rendezvous(mu, reference_radius_m, state0, t_final)
result = plot_relative_position_3d(
    solution.trajectory_states, solution.trajectory_times_s, reference_radius_m
)
print(result.output_path)
```
