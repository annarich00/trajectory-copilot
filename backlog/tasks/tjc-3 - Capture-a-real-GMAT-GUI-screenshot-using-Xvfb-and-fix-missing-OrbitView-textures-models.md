---
id: TJC-3
title: >-
  Capture a real GMAT GUI screenshot using Xvfb and fix missing OrbitView
  textures/models
status: Done
assignee: []
created_date: '2026-10-12 15:14'
updated_date: '2026-10-12 22:00'
labels: []
dependencies:
  - TJC-2
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TJC-2 documented that GMAT-R2026a (GUI binary) genuinely launches and maps real windows under this environment's default WSLg-backed DISPLAY=:0, but every external screen-capture attempt against that display returns a byte-identical blank image, because WSLg's compositor does not expose its rendered buffer to standard X11 capture tools. The operator has now installed xvfb (plus x11-apps and imagemagick) system-wide via apt. A manual investigation (outside the normal implementation workflow) confirmed Xvfb resolves the core blocker: launching GMAT-R2026a against a manually started 'Xvfb :99 -screen 0 1920x1080x24 -nolisten unix -listen tcp' display (TCP listener used because /tmp/.X11-unix is mounted read-only in this environment, blocking Xvfb's default Unix-domain socket) and capturing via mss produced a real, non-blank screenshot: 68834 bytes with 256 unique pixel values (vs. ~3708 bytes with 1-2 unique values for every prior WSLg attempt), stable across repeated captures at 3s-20s waits. An Xlib window-tree walk located the real GMAT main window (0x20011e, 1024x768 at offset 32,32, titled 'General Mission Analysis Tool (GMAT)') and confirmed capturing that exact window region also works. However, the OrbitView 3D trajectory panel itself (a child widget at a sub-region of that window) rendered mostly black (only 14 unique pixel values) rather than showing the actual trajectory, and GmatLog.txt shows 'OpenFrames cannot find or cannot load the model ../data/vehicle/models/aura.3ds' and the same for the ModifiedBlueMarble Earth texture files -- so the capture mechanism itself now works, but the rendered content is currently missing its Earth texture and spacecraft model assets. This task productizes that manual investigation into src/gmat_verify.py's real implementation (replacing or supplementing the existing WSLg-only attempt_gmat_gui_screenshot path), and investigates/fixes the missing-asset rendering gap so the captured screenshot shows an actual visible orbit/trajectory, not just window chrome.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 attempt_gmat_gui_screenshot (or a clearly superseding function) launches and manages its own Xvfb virtual display (not relying on inheriting a pre-existing DISPLAY) so the real-screenshot attempt is self-contained and does not depend on manual setup
- [x] #2 The Xvfb launch correctly handles this environment's read-only /tmp/.X11-unix (e.g. via -nolisten unix -listen tcp or an equivalent documented workaround) and is verified to actually start, not just assumed to start
- [x] #3 The captured screenshot targets the real GMAT application window region (located via a window-tree walk, as manually verified) rather than the full virtual screen, and is validated to be non-blank using a real pixel-variance check, not merely non-empty-file
- [x] #4 The missing OrbitView texture/spacecraft-model asset-loading issue (ModifiedBlueMarble.jpg, aura.3ds, and any other reported missing assets) is investigated and fixed or worked around so the captured screenshot's OrbitView panel shows actual visible orbit/trajectory content, with before/after evidence (pixel-variance or visual description) demonstrating the improvement; if a specific asset genuinely cannot be resolved, that exact blocker is documented as reproducible evidence rather than asserted
- [x] #5 screenshot_source correctly reports 'gmat_gui' (not 'svg_fallback') for a real successful capture under this fixed pipeline, and tests cover the Xvfb-launch success path, the read-only-socket-directory workaround, and the asset-loading fix, in addition to the existing fallback/failure-mode tests
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend attempt_gmat_gui_screenshot (src/gmat_verify.py) with a new keyword-only use_own_xvfb: bool = True param; display= keeps its exact original meaning (explicit override always wins, including display="").
2. Add _launch_managed_xvfb() helper: launches Xvfb :N -screen 0 1920x1080x24 -nolisten unix -listen tcp (TCP listener required by this environment's read-only /tmp/.X11-unix), verifies it actually started by polling the TCP port (not assumed), picking a free display number.
3. Add _find_window_by_title/_locate_gmat_window_region using python-xlib to walk the window tree for the real "General Mission Analysis Tool (GMAT)" window and compute its absolute mss capture region via root.translate_coords, replacing the full-virtual-screen grab.
4. Investigate the OpenFrames "cannot find or cannot load" aura.3ds/ModifiedBlueMarble.jpg errors via ldd on GMAT's osgPlugins-3.6.5/osgdb_3ds.so and osgdb_jpeg.so: confirmed they fail to resolve libosg.so.161/libosgDB.so.161 without GMAT's own lib/ dir on LD_LIBRARY_PATH. Fix by adding gmat_lib_dir (auto-derived from the GUI executable path) to the subprocess env's LD_LIBRARY_PATH.
5. Add python-xlib==0.33 to requirements-dev.txt.
6. Add tests: Xvfb-launch-success (real TCP poll), explicit-display-override-skips-own-Xvfb, and an environment-conditional end-to-end test capturing the real window with/without the asset-loading fix (size/variance comparison). Keep all pre-existing fallback/failure-mode tests passing unchanged.
7. Sync site mirrors, update site/data/project-progress.js, run full check suite, finalize Backlog, single atomic commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
VERIFICATION EVIDENCE (exact commands/output):

AC1/AC2 (self-contained Xvfb, verified start, read-only /tmp/.X11-unix workaround):
- `Xvfb :N -screen 0 1920x1080x24 -nolisten unix -listen tcp &` then polling `socket.create_connection(("127.0.0.1", 6000+N))` succeeds -- confirmed directly and via new test test_launch_managed_xvfb_starts_and_verifies_a_real_tcp_listening_display (PASSED).
- _launch_managed_xvfb() in src/gmat_verify.py implements exactly this and is used by attempt_gmat_gui_screenshot by default (use_own_xvfb=True) only when no explicit display= override is given; test_attempt_gmat_gui_screenshot_explicit_display_override_skips_own_xvfb confirms an explicit display always wins and _launch_managed_xvfb is never called (PASSED), and the pre-existing test_attempt_gmat_gui_screenshot_reports_missing_display_without_launching (display="") still passes unchanged.

AC3 (real window region via Xlib walk, real pixel-variance validation):
- Manual run: launched GMAT-R2026a under a managed Xvfb display with the gui preview script; python-xlib window-tree walk located window title "...General Mission Analysis Tool (GMAT)" at local offset (32,32) 1024x768 -- matches translate_coords absolute region {'left': 32, 'top': 32, 'width': 1024, 'height': 768}. mss.grab(region) of exactly that window: 2359296 bytes, 256 unique pixel values (non-blank).
- Covered end-to-end by test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window (PASSED when Xvfb+GMAT-R2026a available; environment-conditional skip otherwise), asserting "real GMAT application window" appears in the result reason (not the full-screen fallback phrase) and validate_gui_screenshot(...).ok is True.

AC4 (asset-loading investigation/fix, before/after evidence):
- Root cause confirmed, not assumed: `ldd /home/anna_ford/opt/GMAT/R2026a/lib/osgPlugins-3.6.5/osgdb_3ds.so` (and osgdb_jpeg.so) report `libosgDB.so.161 => not found` / `libosg.so.161 => not found` without GMAT's lib/ dir on LD_LIBRARY_PATH; with `LD_LIBRARY_PATH=/home/anna_ford/opt/GMAT/R2026a/lib` both resolve cleanly (ldd shows no "not found" lines).
- BEFORE (no LD_LIBRARY_PATH): GmatLog.txt / stdout contains exactly: "OpenFrames cannot find or cannot load the model ../data/vehicle/models/aura.3ds.", "OpenFrames cannot find or cannot load the texture ../data/graphics/texture/ModifiedBlueMarble.jpg.", "...the night texture .../ModifiedBlueMarble_night.jpg." -- plus underlying "Could not find plugin to read objects from file ...". Captured OrbitView-region PNG: 46,028 bytes (flat/textureless Earth sphere).
- AFTER (LD_LIBRARY_PATH includes GMAT's lib/ dir, auto-derived by attempt_gmat_gui_screenshot's new gmat_lib_dir default): zero asset-loading errors in the same log; captured OrbitView-region PNG: 140,331 bytes (real texture/model content, visibly different pixel data).
- Fix is implemented unconditionally in attempt_gmat_gui_screenshot (adds <gui_executable's bin/..>/lib to LD_LIBRARY_PATH whenever that directory exists) and documented in the function's docstring with this exact reproduction evidence. Covered by test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window's fixed-vs-broken (gmat_lib_dir=/nonexistent) size comparison.

AC5 (screenshot_source == 'gmat_gui' for a real capture):
- End-to-end: `timeout 60 .venv/bin/python scripts/run_cw_gmat_slice.py --output-dir /tmp/slice_run_test --gmat GmatConsole-R2026a` (GUI screenshot path enabled, i.e. no --skip-gui-screenshot) -> verification_result.json: "screenshot_source": "gmat_gui", "trajectory_artifact": ".../trajectory_gmat_gui.png", gui_screenshot_attempt.captured == true, PNG 199,445 bytes. Comparison status PASS (position_error_m=0.00794, velocity_error_mps=1.17e-5).
- New tests cover the Xvfb-launch success path, the read-only-socket-directory TCP workaround, and the asset-loading fix outcome, per AC5's explicit requirement; existing fallback/failure-mode tests (screenshot_source == 'svg_fallback' on missing GMAT, etc.) pass unchanged.

FULL CHECK SUITE:
- `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt` -- succeeded (python-xlib==0.33 added to requirements-dev.txt).
- `.venv/bin/python -m pytest -q` -> "119 passed in 26.96s" (baseline before this task's edits, confirmed via git stash, was 116 passed; net +3 after the real-capture test's prior environment-blocked assertion branch now exercises the captured==True branch instead of a skip, plus 2 new always-run tests and 1 new environment-conditional test).
- `python3 tools/compare_upstream.py --check` -> exit 0, "content-different unaccounted: none", requirements-dev.txt/src/gmat_verify.py/tests/test_cw_gmat_slice.py correctly classified as protected/accepted local edits.
- `python3 tools/sync_site_data.py --check` -> after running `sync_site_data.py` (no --check) once to update site/data/src/gmat_verify.py and site/data/tests/test_cw_gmat_slice.py mirrors, --check reports "site data mirrors match (49 mappings)" (exit 0).
- `./run_site.sh 4555` + curl smoke: GET /data/project-progress.js -> 200 (contains "TJC-3"), GET /data/src/gmat_verify.py -> 200, GET /#/cw-gmat-slice -> 200, GET / -> 200; server stopped cleanly afterward.
- No stray Xvfb/GMAT-R2026a processes left running after any test run or manual investigation (verified via pgrep after every GUI-launching command).

SAFETY: every GMAT-R2026a GUI invocation (manual investigation and the new test) used an explicit timeout and/or managed subprocess.Popen + terminate()/wait()/kill() in a finally block, matching the existing attempt_gmat_gui_screenshot pattern; `GMAT-R2026a --version` was observed to itself open a real blocking GUI window (confirmed once, then avoided for the rest of the session) rather than ever being used in a test skipif.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced the previous WSLg-only, environment-blocked attempt_gmat_gui_screenshot with a self-contained real GMAT GUI screenshot pipeline. By default (use_own_xvfb=True, no explicit display override), it launches and verifies its own Xvfb virtual display (`-nolisten unix -listen tcp`, TCP-port-polled to confirm startup -- required because this sandbox mounts /tmp/.X11-unix read-only), locates the real GMAT main window via a python-xlib window-tree walk (absolute region via root.translate_coords) instead of grabbing the full virtual screen, and validates the capture with the existing non-blank unique-pixel-value check. Confirmed (via ldd and before/after GmatLog.txt/PNG-size comparison, not assumed) that the previously-reported OrbitView aura.3ds/ModifiedBlueMarble.jpg "cannot find or cannot load" errors were a missing-LD_LIBRARY_PATH dynamic-linking problem (GMAT's own osgPlugins-3.6.5 plugins could not resolve libosg.so.161/libosgDB.so.161); fixed by adding GMAT's lib/ dir to the subprocess LD_LIBRARY_PATH, confirmed to eliminate every asset error and grow the OrbitView-region capture from 46,028 to 140,331 real-content bytes. End-to-end, scripts/run_cw_gmat_slice.py now reports screenshot_source == "gmat_gui" with a genuine 199,445-byte captured PNG and a PASS numerical comparison, not svg_fallback. An explicit display= override (including display="") still always wins unchanged, preserving every pre-existing test's behavior. Added python-xlib==0.33 to requirements-dev.txt and three new tests (Xvfb-launch-success via real TCP poll, explicit-display-override-skips-own-Xvfb, and an environment-conditional end-to-end real-window-capture-with/without-the-asset-fix test); all 119 repo tests pass (116 pre-existing + 3 new). compare_upstream.py --check and sync_site_data.py --check both pass (site mirrors re-synced); site served and curl-smoked clean on port 4555. Updated site/data/project-progress.js with a TJC-3 entry.
<!-- SECTION:FINAL_SUMMARY:END -->
