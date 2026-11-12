# `artifacts/cw_gmat_slice/` — persistent GMAT verification output

This is the **default, persistent, discoverable** output directory for
`scripts/run_cw_gmat_slice.py` (TJC-2). Running the script without
`--output-dir` writes every real run's evidence here:

- `generated_cw_rendezvous.script` — the generated GMAT console-mode script;
- `d_init.txt`, `d_postburn1.txt`, `d_final.txt`, `d_trajectory.txt` — parsed
  GMAT `ReportFile` output;
- `trajectory.svg` — the deterministic SVG trajectory plot (fallback
  artifact), **or** `trajectory_gmat_gui.png` — a real captured GMAT GUI
  (OrbitView/OpenFrames) screenshot, whichever was actually produced (see
  `verification_result.json`'s `"screenshot_source"` field: `"gmat_gui"` or
  `"svg_fallback"`);
- `verification_result.json` — the full structured result, including an
  explicit `trajectory_artifact` path to whichever of the above was
  produced.

## Why this directory is only partially tracked in git

This directory's contents (other than this README) are deliberately
**gitignored** (`artifacts/cw_gmat_slice/*` in `.gitignore`, with this
`README.md` explicitly un-ignored): real per-run outputs are regenerated
every time the script runs and would otherwise bloat repository history
with ephemeral binary/log artifacts that are not meant to be reviewed as
source. This README is the one tracked file, so the directory and its
convention are discoverable from a fresh clone without having run anything.

A single small, **persistent, committed example run** (demonstrating the
real shape of these artifacts, including an example `verification_result.json`
and `trajectory.svg`) lives instead under `examples/cw_gmat_slice_example/`
— that directory is fully tracked in git and is what the educational site
(`#/cw-gmat-slice`) links to as a concrete, always-available example.

## Reproducing a real run

```
.venv/bin/python scripts/run_cw_gmat_slice.py --gmat GmatConsole-R2026a
```

(omit `--output-dir` to use this default, persistent location). See
`site/js/pages/cw-gmat-slice.js` and `src/gmat_verify.py` for the full
verification contract and failure modes.
