# `examples/cw_gmat_slice_example/` — committed demonstration artifact

This is **one small, persistent, committed example run** of
`scripts/run_cw_gmat_slice.py` against the circular-LEO quarter-orbit CW
rendezvous case (`examples/cw_gmat_vertical_slice.yaml`), kept in git
history so it is always available to link to from the educational site
(`#/cw-gmat-slice`) without requiring GMAT to actually be installed.

- `verification_result.json` — the full structured result from a real run
  against `GmatConsole-R2026a`, reaching `"verified": true` (position error
  ~0.0079 m, velocity error ~1.17e-5 m/s, both well inside the 1 m / 0.001
  m/s tolerances). `"screenshot_source": "svg_fallback"` — see TJC-2's
  documented real-GMAT-GUI-screenshot investigation in
  `src/gmat_verify.py::attempt_gmat_gui_screenshot` for why.
- `trajectory.svg` — the deterministic SVG trajectory plot artifact from
  that same run.

This directory is distinct from `artifacts/cw_gmat_slice/` (see that
directory's own `README.md`): that one is the *live, regenerated-every-run*
default output location (mostly gitignored); this one is a *fixed,
unchanging, committed snapshot* for discoverability.
