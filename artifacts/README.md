# Artifacts

This directory stores generated outputs and run-derived material.

## Layout

- `artifacts/runs/` — outputs from workflow runs, verification runs, and diagnosis runs
- `artifacts/evaluations/` — benchmark sets, comparison results, and formalizer evaluation material
- `artifacts/visualizations/` — shared generated charts, plots, and HTML visualizations

## Rule of thumb

- Put reusable hand-authored inputs in `examples/`
- Put generated results, logs, screenshots, and reports in `artifacts/`
- Git ignores most generated files here; keep only the curated examples and docs that should be tracked
- The repository uses a .gitignore file for bulk-generated run outputs under this tree
- Prefer adding a new subfolder under `artifacts/` instead of scattering outputs at the repository root
