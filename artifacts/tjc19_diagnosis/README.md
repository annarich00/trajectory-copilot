# TJC-19 diagnosis — captured evidence (RESOLVED)

This directory holds the raw evidence for TJC-19's investigation of the GMAT GUI
segfault and the reported 124-second mission run time attributed to TJC-18's
multi-view/XYPlot script. The investigation is complete; the narrative findings
live in TJC-19's Backlog Implementation Notes (`backlog task view TJC-19 --plain`).

**An earlier, interrupted session's handoff notes previously occupied this file and
reached two conclusions that are now known to be wrong. See "Corrections" below —
those earlier conclusions should not be cited.**

## Headline findings

- **The segfault is real, reproducible, and NOT caused by TJC-18.** It reproduces on
  the full TJC-18 script (9/10 runs) *and* on the pre-TJC-18-style single-OrbitView
  baseline (5/10 runs). It is an intermittent crash during GMAT's GUI/window
  teardown, after `Mission run completed.` has already been logged.
- **The one necessary condition is that at least one plot window actually opens**
  (`ShowPlot = true`). The full TJC-18 script with every `ShowPlot` flipped to
  `false` keeps all resources and commands (including `MarkPoint`) and never
  crashed. More simultaneous windows raises the crash rate (1 window ~5/10,
  3 windows ~9/10), consistent with a per-window teardown race.
- **The 124-second run time did not reproduce.** The full TJC-18 script's mission run
  takes 0.64–2.04s on an idle machine; the single-OrbitView baseline takes
  0.37–0.62s. TJC-18's two extra windows cost roughly +0.3 to +1.4s, not +124s.
- **`attempt_gmat_gui_screenshot` is unaffected**, because it kills GMAT externally
  and never asks it to run the teardown path where the crash occurs. Observed, not
  inferred: the GMAT child's recorded exit status was SIGTERM (`-15`) on every run,
  never SIGSEGV (`-11`).
- **The font-error spam is pre-existing and per-window**, not new to TJC-18: 105
  lines with one OrbitView, 210 with two or three windows, 0 with no windows.

## Corrections to the earlier interrupted session

Both of its central claims were measurement artifacts, not GMAT behavior:

1. **"The runs hung and never reached `Mission run completed`."** `Mission run
   completed.` and `===> Total Run Time: %.3lf seconds` are emitted by
   `libGmatBase.so` into GMAT's **log file**, never onto stdout (confirm with
   `strings ~/opt/GMAT/R2026a/bin/libGmatBase.so | grep -i 'Total Run Time'`). That
   session grepped only captured stdout, so its absence there carried no information.
2. **"`EXIT_CODE=124` proves a hang."** Those runs used a bare `-r` with no `-x`,
   which leaves GMAT's GUI event loop running indefinitely after the mission
   finishes — exactly as intended, since the operator closed the window by hand.
   Under `timeout`, such a run can never exit on its own, so `124` meant only "the
   GUI was still open". There was no hang to explain.

Its one load-independent finding does still hold: with `LD_LIBRARY_PATH` unset,
`lib/osgPlugins-3.6.5/osgdb_3ds.so` and `osgdb_freetype.so` fail to resolve
`libosg.so.161`/`libosgDB.so.161`/`libosgText.so.161`/`libOpenThreads.so.21`
(per `ldd`), which changes the *wording* of the font/texture errors but, as
measured here, affects neither the crash rate nor the run time.

## Contents

- `run_variant.sh` — the harness used for every timing and exit-status measurement.
  Runs one variant under either a self-managed Xvfb framebuffer or the inherited
  WSLg `DISPLAY`, with or without GMAT's `lib/` on `LD_LIBRARY_PATH`, always under a
  bounded `timeout`, always with `-x` so GMAT exits through its own teardown and the
  exit code is meaningful. Records a pre-run idle check (`uptime`, top-10 CPU),
  per-run GMAT log, stdout, 5-second `ps`/`free` snapshots, and a summary.
  Usage: `./run_variant.sh <label> <script> <timeout-s> <with|without> [xvfb|inherit]`.
- `ac3_screenshot_probe.py` — the AC3 probe. Calls the real
  `attempt_gmat_gui_screenshot` on every window-opening variant and records the GMAT
  child's final exit signal, distinguishing "killed by our `terminate()`" from "died
  of SIGSEGV on its own".
- `variants/` — the script variants, forming the one-element-at-a-time isolation
  ladder:
  | variant | content | SIGSEGV rate |
  |---|---|---|
  | `variant_a_single_orbitview.script` | one `OrbitView` (pre-TJC-18 baseline) | 5/10 |
  | `variant_b_two_orbitviews.script` | two `OrbitView`s, no `XYPlot` | 2/3 |
  | `variant_c_full_tjc18.script` | full TJC-18 output: two `OrbitView`s + `BurnMarkers` `XYPlot` + `MarkPoint` | 9/10 |
  | `variant_d_xyplot_no_markpoint.script` | variant C with the `MarkPoint` commands removed | 2/3 |
  | `variant_e_one_orbitview_xyplot.script` | one `OrbitView` + `XYPlot` + `MarkPoint` | 3/3 |
  | `variant_f_full_showplot_false.script` | variant C with every `ShowPlot = false` | 0/3 |

  `variant_c_full_tjc18.script` is byte-identical to the script the operator ran
  (verified by diffing against a fresh `generate_gmat_gui_preview_script` call with
  the `circular_leo_400km_one_period_rendezvous_user_request` case's inputs).
- `logs/trial_results.txt` — the aggregated per-run results table (one row per run:
  exit code, wall time, GMAT's own mission run time, font-error count, display mode,
  and the pre-run load average). This is the complete per-run record and the primary
  evidence file.
- `logs/` — raw output for the named one-off runs: `<label>.summary.txt` (idle check
  + exit code + timing), `<label>.gmatlog.txt` (GMAT's own log, where the run time
  actually appears), `<label>.stdout.log`, `<label>.ps.log` (memory/CPU snapshots),
  plus `ac3_probe.log`. The repeated `trial_*` runs' bulky stdout captures were
  pruned (~800KB of near-identical per-window font-error spam); their results live in
  `trial_results.txt`. The `tjc19_repro*.log` / `tjc19_variant_a.log` files are the
  earlier session's raw captures, kept for provenance but subject to the two
  measurement corrections above.
- `ac3_captures/` — the PNGs the AC3 probe actually captured (not committed; they are
  regenerable by re-running the probe).

## Reproducing

From the repo root, on an otherwise-idle machine (the harness records its own idle
check, so a contended run is detectable after the fact):

```bash
./artifacts/tjc19_diagnosis/run_variant.sh repro \
  artifacts/tjc19_diagnosis/variants/variant_c_full_tjc18.script 240 without
```

Expect `exit_code=139` on most runs. Because the crash is intermittent, a single
clean exit does not disprove it — run it several times.

## What remains unknown

The operator's original 124-second run time is still unexplained. No script-content
factor reproduces it: not the window count, not the `XYPlot`, not `MarkPoint`, not
`LD_LIBRARY_PATH`, and not the inherited-`DISPLAY` path the operator actually used.
Unrelated background CPU contention is the leading hypothesis, but it was not
measured during that run and cannot be confirmed retroactively.
