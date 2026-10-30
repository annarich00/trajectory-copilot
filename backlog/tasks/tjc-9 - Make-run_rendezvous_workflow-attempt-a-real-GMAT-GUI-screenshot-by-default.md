---
id: TJC-9
title: Make run_rendezvous_workflow attempt a real GMAT GUI screenshot by default
status: Done
assignee:
  - '@pi'
created_date: '2026-10-22 12:31'
updated_date: '2026-10-30 20:11'
labels: []
dependencies: []
priority: high
ordinal: 100
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
src/workflow.py's run_rendezvous_workflow (TJC-1.16) hardcodes skip_gui_screenshot=True in _run_cw_path and never calls attempt_gmat_gui_screenshot at all in _run_two_body_path, so every workflow run -- including every /rendezvous demo and every conversational agent session -- always falls straight to the deterministic SVG fallback and never attempts the real GMAT GUI (OrbitView/OpenFrames) screenshot, even though scripts/run_cw_gmat_slice.py's own --gmat-gui flag and src/gmat_verify.py::attempt_gmat_gui_screenshot already implement a working, self-contained-Xvfb GUI capture path (already proven in examples/cw_gmat_slice_example/ and reproduced live just now: a real 199KB PNG with screenshot_source='gmat_gui'). tests/test_workflow.py has zero coverage of the GUI screenshot path, which is why this was never caught. The operator has decided the GUI screenshot attempt should be the default behavior of run_rendezvous_workflow for both the CW and two-body paths, not an opt-in flag.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 run_rendezvous_workflow's CW path (_run_cw_path) passes skip_gui_screenshot=False by default so a real GMAT GUI screenshot is attempted on every run
- [x] #2 run_rendezvous_workflow's two-body path (_run_two_body_path) also attempts a real GMAT GUI screenshot via attempt_gmat_gui_screenshot by default, mirroring the CW path's behavior, with its own correctly scoped preview script (not reusing the CW GUI preview script generator)
- [x] #3 Both paths still gracefully fall back to the deterministic SVG plot and record screenshot_source='svg_fallback' when the GUI capture is unavailable/fails (missing GMAT GUI executable, no display, blank capture, etc.) -- a failed GUI attempt must never be reported as a failure of the overall verification, only as a fallback
- [x] #4 An explicit override parameter exists on run_rendezvous_workflow (e.g. attempt_gui_screenshot: bool = True) so a caller can opt back out to SVG-only for fast/CI runs without needing to touch either solver path's internals
- [x] #5 tests/test_workflow.py gains coverage asserting: (a) the default call path actually invokes/attempts GUI screenshot capture for both CW and two-body outcomes, using the same monkeypatch pattern already used for GMAT availability/execution stand-ins; (b) screenshot_source is correctly recorded as gmat_gui vs svg_fallback in each case; (c) explicitly passing attempt_gui_screenshot=False skips the GUI attempt and goes straight to SVG, with zero regression to the 4 already-committed benchmark/baseline-comparison VERIFIED results
- [x] #6 A real run of evaluations/baseline_comparison/run_workflow_cases.py (or equivalent) against a real GmatConsole-R2026a + GMAT-R2026a install in this environment produces screenshot_source='gmat_gui' for at least one case, confirmed by inspecting the regenerated result JSON, not just by test mocks
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. src/gmat_verify.py: add generate_two_body_gui_preview_script(state0_si, mu_m3_s2, duration_s) producing an OrbitView preview script for the single-spacecraft inertial coast (mirrors generate_two_body_coast_script's Spacecraft/ForceModel/Propagator setup, substitutes OrbitView for ReportFile, no burns), scoped separately from generate_gmat_gui_preview_script (AC2).
2. src/workflow.py: add attempt_gui_screenshot: bool = True to run_rendezvous_workflow and thread it into _run_cw_path/_run_two_body_path (AC4).
3. _run_cw_path: pass skip_gui_screenshot=not attempt_gui_screenshot into run_cw_rendezvous_gmat_verification (flips the current hardcoded True), and record result['screenshot_source']/['gui_screenshot_attempt'] into WorkflowResult.artifacts (AC1).
4. _run_two_body_path: when attempt_gui_screenshot, write the new GUI preview script, call gmat_verify.attempt_gmat_gui_screenshot, validate with validate_gui_screenshot, and only use it (screenshot_source='gmat_gui', media_type image/png) when captured+valid; otherwise fall back to the existing _write_two_body_svg path (screenshot_source='svg_fallback'); record screenshot_source/gui_screenshot_attempt in artifacts exactly like the CW path (AC2, AC3).
5. tests/test_workflow.py: add coverage that (a) the default call monkeypatches slice_runner.attempt_gmat_gui_screenshot / workflow.attempt_gmat_gui_screenshot (same stand-in pattern as tests/test_cw_gmat_slice.py) to assert a real attempt is made for both CW and two-body outcomes, with screenshot_source flipping between gmat_gui (captured) and svg_fallback (not captured/unavailable) without ever failing the overall verification; (b) attempt_gui_screenshot=False skips the GUI attempt entirely (monkeypatched to raise if called) and goes straight to SVG for both paths, with the existing fake-GMAT-run happy-path tests still reaching VERIFIED (AC5).
6. Run the full tests/test_workflow.py and tests/test_cw_gmat_slice.py suites; fix regressions.
7. Re-run evaluations/baseline_comparison/run_workflow_cases.py for real against the installed GmatConsole-R2026a/GMAT-R2026a, inspect the regenerated case_*_workflow_result.json for at least one screenshot_source=='gmat_gui', and commit the refreshed result JSON/example artifacts if they change (AC6).
8. Delegate the code+test implementation (steps 1-6) to a subagent working in the dedicated tjc-9 git worktree/branch; orchestrator runs the real GMAT GUI verification run (step 7), backlog finalization, and the single atomic commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Separately confirmed (not part of this task's scope, but directly relevant context): attempting an INTERACTIVE GMAT GUI window (as opposed to this task's non-interactive screenshot capture via attempt_gmat_gui_screenshot) is a structural, non-retry-able sandbox limitation in this environment -- no GPU render-node path (/dev/dri absent despite /dev/dxg being present/openable) and WSLg/RDP never forwards a rendered buffer to the user's real desktop even when a window registers. Documented directly in src/gmat_verify.py::attempt_gmat_gui_screenshot's docstring and reflected in .pi/prompts/rendezvous.md's step 5 (give the user the exact run-it-yourself command instead of attempting a launch). This task's GUI-screenshot-by-default fix is unaffected: attempt_gmat_gui_screenshot's self-contained Xvfb capture path is a different, already-working mechanism from the interactive-window launch path that was found not to work.

Implemented via subagent (worker) in isolated git worktree/branch tjc-9:
- src/gmat_verify.py: added generate_two_body_gui_preview_script(state0_si, mu_m3_s2, duration_s) -- a correctly-scoped single-spacecraft OrbitView GUI preview script generator for the two-body coast case (distinct from the CW/Deputy-specific generate_gmat_gui_preview_script).
- src/workflow.py: run_rendezvous_workflow gained gmat_gui_executable='GMAT-R2026a' and attempt_gui_screenshot=True (default) params, threaded into both _run_cw_path (skip_gui_screenshot=not attempt_gui_screenshot passed into the existing slice_runner pipeline) and _run_two_body_path (new attempt_gmat_gui_screenshot + validate_gui_screenshot call before the existing _write_two_body_svg fallback). Both paths surface screenshot_source/gui_screenshot_attempt into WorkflowResult.artifacts. A failed/unavailable GUI attempt never flips verified/failure_mode -- only screenshot_source.
- tests/test_workflow.py: 4 new tests (default-True invokes real capture for both paths; graceful SVG fallback on blank-capture/no-display for both paths with zero change to VERIFIED outcome; attempt_gui_screenshot=False skips the GUI stand-in entirely for both paths via an assert-if-called stub) plus 2 pre-existing SVG-path-specific tests updated to pass attempt_gui_screenshot=False explicitly (this sandbox has a real reachable GMAT-R2026a + mss + Xlib, so the new default-True path genuinely captures a real GUI render here rather than only falling back -- those two tests are about SVG-path/CW behavior specifically, not GUI capture).
Verification:
- .venv/bin/python -m pytest tests/test_workflow.py tests/test_cw_gmat_slice.py -q -> 40 passed.
- .venv/bin/python -m pytest tests/ -q (full suite) -> 150 passed, zero regressions (independently re-run by me after the subagent handoff).
- Real end-to-end run (no mocks) of evaluations/baseline_comparison/run_workflow_cases.py --gmat GmatConsole-R2026a against the installed GmatConsole-R2026a/GMAT-R2026a: all 3 previously-VERIFIED cases (a: straightforward CW, b: boundary CW, c: two-body) now show screenshot_source='gmat_gui' with a real ~195KB-199KB captured PNG and verified=True/outcome='VERIFIED' unchanged; case d (NEEDS_CLARIFICATION) is byte-for-byte unchanged (no screenshot attempted, as expected -- it short-circuits before any physics/GMAT step). Regenerated case_a/b/c_workflow_result.json committed; workflow_artifacts/ working directories are gitignored and not committed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
run_rendezvous_workflow now attempts a real GMAT GUI (OrbitView/OpenFrames) screenshot by default for both the CW and bounded two-body paths, via attempt_gmat_gui_screenshot (self-contained Xvfb capture), falling back to the deterministic SVG plot (screenshot_source='svg_fallback') whenever the GUI capture is unavailable or fails -- never as an overall verification failure. A new attempt_gui_screenshot: bool = True parameter (plus gmat_gui_executable) lets callers opt back out to SVG-only. The two-body path gained its own correctly-scoped generate_two_body_gui_preview_script (not a reuse of the CW/Deputy-specific generator). tests/test_workflow.py covers the default-on capture attempt, graceful fallback, and explicit opt-out for both paths (150/150 full suite passing). A real run against the installed GmatConsole-R2026a/GMAT-R2026a produced screenshot_source='gmat_gui' for all 3 previously-VERIFIED baseline-comparison cases (a, b, c), confirmed by inspecting the regenerated result JSON; case d (NEEDS_CLARIFICATION) is unchanged.
<!-- SECTION:FINAL_SUMMARY:END -->
