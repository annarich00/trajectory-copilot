# `examples/cw_gmat_slice_example/` — committed demonstration artifact

This is **one small, persistent, committed example run** of
`scripts/run_cw_gmat_slice.py` against the circular-LEO quarter-orbit CW
rendezvous case (`examples/cw_gmat_vertical_slice.yaml`), kept in git
history so it is always available to link to from the educational site
(`#/cw-gmat-slice`) without requiring GMAT to actually be installed.

- `verification_result.json` — the full structured result from a real run
  against `GmatConsole-R2026a`, reaching `"verified": true` (position error
  ~0.0079 m, velocity error ~1.17e-5 m/s, both well inside the 1 m / 0.001
  m/s tolerances). `"screenshot_source": "gmat_gui"` — TJC-3 fixed the
  OrbitView/OpenFrames asset-loading bug (a missing `LD_LIBRARY_PATH` entry
  for GMAT's own `lib/` directory) that previously made every real-GUI
  screenshot attempt fail in this environment; see
  `src/gmat_verify.py::attempt_gmat_gui_screenshot` for the fix and its
  reproduction evidence.
- `trajectory_gmat_gui.png` — the real, non-blank, correctly-textured GMAT
  GUI (OrbitView/OpenFrames) screenshot captured by that same run
  (~199 KB).

## How this was produced (TJC-4)

Regenerated with a real, live run of `scripts/run_cw_gmat_slice.py` in an
environment with Xvfb, `GMAT-R2026a` (the GUI executable), and
`GmatConsole-R2026a` (the noninteractive executable) all installed:

```
timeout 90 .venv/bin/python scripts/run_cw_gmat_slice.py \
  --gmat GmatConsole-R2026a --gmat-gui GMAT-R2026a \
  --output-dir <some writable absolute path>
```

(an absolute `--output-dir` is required: GMAT's `ReportFile` resources are
written relative to GMAT's own `bin/` working directory, not the caller's
cwd, so a relative output directory silently produces a `MALFORMED_OUTPUT`
failure instead of real artifacts). The run was performed in a scratch
directory and the two files above were copied in, with only the top-level
`input`/`trajectory_artifact`/`verification_report_path`/
`artifact_storage_convention` path fields in `verification_result.json`
relativized back to this repository (the same convention TJC-2's original
commit used); raw GMAT stdout/log text embedded in the JSON still shows the
scratch path verbatim since that is unedited real process output, not a
path the reader is meant to follow.

**This is expected to reproduce only when all of the following hold:**
an X display is reachable (this project's `attempt_gmat_gui_screenshot`
can launch its own self-contained Xvfb when none is inherited), and both
`GMAT-R2026a` and `GmatConsole-R2026a` are installed and runnable. In an
environment missing any of those (e.g. a CI container without GMAT
installed at all, or one where `GMAT-R2026a`'s GUI genuinely cannot render
under any reachable display), `scripts/run_cw_gmat_slice.py` falls back to
the deterministic SVG trajectory plot and `screenshot_source` records
`"svg_fallback"` instead — that is a legitimate, honestly-reported outcome
for this committed example too, not a bug if it is what you observe when
regenerating this directory yourself.

This directory is distinct from `artifacts/cw_gmat_slice/` (see that
directory's own `README.md`): that one is the *live, regenerated-every-run*
default output location (mostly gitignored); this one is a *fixed,
unchanging, committed snapshot* for discoverability.
