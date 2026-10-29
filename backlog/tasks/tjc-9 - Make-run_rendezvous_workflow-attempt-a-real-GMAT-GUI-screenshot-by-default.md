---
id: TJC-9
title: Make run_rendezvous_workflow attempt a real GMAT GUI screenshot by default
status: To Do
assignee:
  - '@pi'
created_date: '2026-10-22 12:31'
updated_date: '2026-10-22 17:26'
labels: []
dependencies: []
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
src/workflow.py's run_rendezvous_workflow (TJC-1.16) hardcodes skip_gui_screenshot=True in _run_cw_path and never calls attempt_gmat_gui_screenshot at all in _run_two_body_path, so every workflow run -- including every /rendezvous demo and every conversational agent session -- always falls straight to the deterministic SVG fallback and never attempts the real GMAT GUI (OrbitView/OpenFrames) screenshot, even though scripts/run_cw_gmat_slice.py's own --gmat-gui flag and src/gmat_verify.py::attempt_gmat_gui_screenshot already implement a working, self-contained-Xvfb GUI capture path (already proven in examples/cw_gmat_slice_example/ and reproduced live just now: a real 199KB PNG with screenshot_source='gmat_gui'). tests/test_workflow.py has zero coverage of the GUI screenshot path, which is why this was never caught. The operator has decided the GUI screenshot attempt should be the default behavior of run_rendezvous_workflow for both the CW and two-body paths, not an opt-in flag.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 run_rendezvous_workflow's CW path (_run_cw_path) passes skip_gui_screenshot=False by default so a real GMAT GUI screenshot is attempted on every run
- [ ] #2 run_rendezvous_workflow's two-body path (_run_two_body_path) also attempts a real GMAT GUI screenshot via attempt_gmat_gui_screenshot by default, mirroring the CW path's behavior, with its own correctly scoped preview script (not reusing the CW GUI preview script generator)
- [ ] #3 Both paths still gracefully fall back to the deterministic SVG plot and record screenshot_source='svg_fallback' when the GUI capture is unavailable/fails (missing GMAT GUI executable, no display, blank capture, etc.) -- a failed GUI attempt must never be reported as a failure of the overall verification, only as a fallback
- [ ] #4 An explicit override parameter exists on run_rendezvous_workflow (e.g. attempt_gui_screenshot: bool = True) so a caller can opt back out to SVG-only for fast/CI runs without needing to touch either solver path's internals
- [ ] #5 tests/test_workflow.py gains coverage asserting: (a) the default call path actually invokes/attempts GUI screenshot capture for both CW and two-body outcomes, using the same monkeypatch pattern already used for GMAT availability/execution stand-ins; (b) screenshot_source is correctly recorded as gmat_gui vs svg_fallback in each case; (c) explicitly passing attempt_gui_screenshot=False skips the GUI attempt and goes straight to SVG, with zero regression to the 4 already-committed benchmark/baseline-comparison VERIFIED results
- [ ] #6 A real run of evaluations/baseline_comparison/run_workflow_cases.py (or equivalent) against a real GmatConsole-R2026a + GMAT-R2026a install in this environment produces screenshot_source='gmat_gui' for at least one case, confirmed by inspecting the regenerated result JSON, not just by test mocks
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Separately confirmed (not part of this task's scope, but directly relevant context): attempting an INTERACTIVE GMAT GUI window (as opposed to this task's non-interactive screenshot capture via attempt_gmat_gui_screenshot) is a structural, non-retry-able sandbox limitation in this environment -- no GPU render-node path (/dev/dri absent despite /dev/dxg being present/openable) and WSLg/RDP never forwards a rendered buffer to the user's real desktop even when a window registers. Documented directly in src/gmat_verify.py::attempt_gmat_gui_screenshot's docstring and reflected in .pi/prompts/rendezvous.md's step 5 (give the user the exact run-it-yourself command instead of attempting a launch). This task's GUI-screenshot-by-default fix is unaffected: attempt_gmat_gui_screenshot's self-contained Xvfb capture path is a different, already-working mechanism from the interactive-window launch path that was found not to work.
<!-- SECTION:NOTES:END -->
