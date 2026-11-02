---
id: TJC-17
title: >-
  Fix attempt_gmat_gui_screenshot's silent Xvfb-launch-failure fallback to a
  broken real DISPLAY
status: Done
assignee:
  - '@pi'
created_date: '2026-10-30 22:12'
updated_date: '2026-11-02 01:28'
labels: []
dependencies: []
priority: high
ordinal: 68000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TJC-9 made run_rendezvous_workflow attempt a real GMAT GUI screenshot by default, using src/gmat_verify.py::attempt_gmat_gui_screenshot's self-managed Xvfb virtual display (_launch_managed_xvfb) so the capture never depends on an inherited, possibly-broken DISPLAY. However, a real manual run (artifacts/manual_runs/circular_leo_one_period_rendezvous/, 2026-10-30) recorded gui_screenshot_attempt.reason='GMAT GUI process launched under the configured DISPLAY (:0) ... captured screen image was uniformly blank', i.e. the self-managed Xvfb silently failed to start for that run and the code fell back to the real inherited DISPLAY=:0 (the same WSLg-forwarded display that independently crashes with libEGL/pixman errors when GMAT-R2026a is launched directly against it, per src/gmat_verify.py's own documented sandbox-limitation diagnosis). That fallback (src/gmat_verify.py, around the 'elif use_own_xvfb' branch: 'display = managed_xvfb.display if managed_xvfb is not None else os.environ.get("DISPLAY")') is silent: nothing in GMATGUIScreenshotResult.reason or the caller's logs distinguishes 'Xvfb launched fine, display :N' from 'Xvfb failed to start, fell back to your real DISPLAY=:0 instead' -- an operator reading the recorded reason has no way to tell these two very different situations apart, and the real-DISPLAY fallback reliably produces a blank capture (SVG fallback) instead of ever retrying the self-managed path. A follow-on manual standalone call to _launch_managed_xvfb() / attempt_gmat_gui_screenshot() in the same environment, moments later, succeeded cleanly and captured a real non-blank 1024x768 PNG, confirming the Xvfb path itself works and the failure was transient/racy, not structural.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 attempt_gmat_gui_screenshot's GMATGUIScreenshotResult.reason (or a new field) explicitly distinguishes a successful self-managed Xvfb launch (and its display number) from a fallback to the real inherited DISPLAY, so a caller/operator can tell these apart from the recorded result alone
- [x] #2 _launch_managed_xvfb failures are retried at least once (e.g. a brief backoff and a second attempt at a fresh display number) before falling back to the real inherited DISPLAY, since the observed failure was transient rather than a structural absence of Xvfb
- [x] #3 when use_own_xvfb is True (the default) and _launch_managed_xvfb ultimately fails after retry, attempt_gmat_gui_screenshot either (a) returns a result that never attempts capture against the real inherited DISPLAY at all (treating it the same as 'no display' when use_own_xvfb was explicitly requested), or (b) attempts it but the recorded reason makes unmistakably clear this was a managed-Xvfb-launch-failure fallback, not a normal successful managed-display attempt -- pick one explicit, documented behavior and make it observable in tests
- [x] #4 a regression test in tests/test_cw_gmat_slice.py or tests/test_gmat_verify.py (whichever already covers attempt_gmat_gui_screenshot/_launch_managed_xvfb) monkeypatches _launch_managed_xvfb to fail and asserts the chosen AC3 behavior, plus a retry-succeeds case asserting the retry path is actually exercised
- [x] #5 re-running the exact manual case that surfaced this (a circular-LEO one-period CW rendezvous case through run_rendezvous_workflow with attempt_gui_screenshot defaulted True) in this environment now reliably produces screenshot_source='gmat_gui' with a real non-blank PNG, not a silent fallback to a blank capture, confirmed by inspecting the regenerated result JSON
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. src/gmat_verify.py: add retry to _launch_managed_xvfb's caller (or inside _launch_managed_xvfb itself) -- on a failed launch, wait briefly and retry at least once at a fresh display number before giving up, since the observed failure was transient/racy, not structural (AC2).
2. src/gmat_verify.py::attempt_gmat_gui_screenshot: when use_own_xvfb=True (default) and the managed Xvfb launch (including retry) still fails, do NOT silently fall back to the real inherited os.environ.get('DISPLAY') -- treat this the same as 'no display at all' and return a GMATGUIScreenshotResult(False, False, None, <reason explicitly stating the managed Xvfb launch failed, not merely 'no DISPLAY configured'>) (AC3 option a, the safer default since the real DISPLAY is confirmed broken/unusable in this sandbox).
3. Thread the resolved display's provenance into the result: when the managed Xvfb succeeds, the eventual reason string (whether capture succeeds or fails) must explicitly say which display number was used and that it was the self-managed Xvfb, not an inherited DISPLAY, so a caller/operator can always tell the two apart from the recorded result alone (AC1).
4. tests/test_cw_gmat_slice.py (or wherever attempt_gmat_gui_screenshot/_launch_managed_xvfb already has coverage): add a regression test monkeypatching _launch_managed_xvfb to always fail, asserting the AC3 behavior (no fallback to real DISPLAY, explicit reason), and a second test where _launch_managed_xvfb fails once then succeeds on retry, asserting the retry path is actually exercised and capture proceeds normally after it (AC4).
5. Run the full test suite; fix regressions.
6. Re-run the exact circular-LEO one-period CW case through run_rendezvous_workflow with attempt_gui_screenshot defaulted True, several times if needed, and confirm screenshot_source='gmat_gui' with a real non-blank PNG is now reliably produced, inspecting the regenerated result JSON (AC5).
7. Delegate implementation (steps 1-5) to a subagent working in the dedicated tjc-17 git worktree/branch; orchestrator runs the final live re-confirmation (step 6), backlog finalization, and the single atomic commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented via subagent (worker) in isolated git worktree/branch tjc-17:
- src/gmat_verify.py: added _launch_managed_xvfb_with_retry (retries _launch_managed_xvfb once, 1s delay, before giving up). attempt_gmat_gui_screenshot's use_own_xvfb=True branch now calls this retry helper; if it still returns None, the function returns GMATGUIScreenshotResult(False, False, None, <explicit managed-Xvfb-launch-failure reason>) immediately and NEVER falls back to os.environ.get('DISPLAY') (the confirmed-broken real display in this sandbox). Both the blank-capture and success reason strings now include a display_description that explicitly distinguishes 'self-managed Xvfb display (:N)' from 'configured DISPLAY (...)', so an operator can always tell which was used from the recorded result alone. The explicit_display and use_own_xvfb=False paths are behaviorally unchanged (only a clarifying wording tweak to the generic no-DISPLAY message).
- tests/test_cw_gmat_slice.py: two new regression tests -- (1) monkeypatches _launch_managed_xvfb to always fail with a real-looking DISPLAY=:0 set, asserts attempted=False/captured=False, an explicit managed-Xvfb-failure reason, and that ':0' never leaks into the reason as if it had been used; (2) monkeypatches _launch_managed_xvfb to fail once then succeed, asserts the retry helper is actually called twice and proceeds with the eventually-successful display.
Verification (independently re-run by me, not just trusting the subagent's report):
- .venv/bin/python -m pytest tests/ -q -> 152 passed (full suite, zero regressions).
- Re-ran the exact circular-LEO one-period CW case through run_rendezvous_workflow 3 times in a row (attempt_gui_screenshot defaulted True, real GmatConsole-R2026a/GMAT-R2026a): all 3 runs produced screenshot_source='gmat_gui' with a real, well-formed ~201KB 1024x768 PNG and the new reason text 'captured a non-blank 1024x768 GMAT GUI render ... under the self-managed Xvfb display (:90)' -- no silent fallback to a blank DISPLAY=:0 capture observed across all 3 attempts, directly confirming AC5 with live evidence (not test mocks).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
attempt_gmat_gui_screenshot's self-managed Xvfb launch (_launch_managed_xvfb) now retries once (1s delay) before giving up (_launch_managed_xvfb_with_retry), and when use_own_xvfb=True (the default) and the retry still fails, the function returns an explicit failure result instead of silently falling back to the real, confirmed-broken inherited DISPLAY -- the exact silent-fallback-to-a-blank-capture bug observed in a real manual run. Both the blank-capture and success reason strings now explicitly name which display provenance was used ('self-managed Xvfb display (:N)' vs. 'configured DISPLAY (...)'), so this is always observable from the recorded result alone. Two new regression tests cover the no-fallback and retry-succeeds paths; full suite 152/152 passing. Re-ran the exact circular-LEO one-period CW case live 3 times with a real GMAT install: all 3 runs now reliably produce screenshot_source='gmat_gui' with a real ~201KB non-blank PNG, confirming the fix with live evidence, not just test mocks.
<!-- SECTION:FINAL_SUMMARY:END -->
