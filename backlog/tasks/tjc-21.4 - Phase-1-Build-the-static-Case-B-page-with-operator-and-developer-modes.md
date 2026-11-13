---
id: TJC-21.4
title: 'Phase 1: Build the static demo page with operator and developer modes'
status: In Progress
assignee:
  - '@worker'
created_date: '2026-11-10 13:37'
updated_date: '2026-11-13 19:41'
labels:
  - web-demo
dependencies:
  - TJC-21.1
  - TJC-21.3
documentation:
  - docs/web-interface-decisions.md
parent_task_id: TJC-21
priority: high
type: feature
ordinal: 76000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
This is the page the advisor will see on GitHub Pages and the front end that Phase 2 reuses. It replays a stored run step by step with a mode toggle: operator mode shows the fixed templates, developer mode shows the raw agent output and tool calls. It also needs to settle whether it extends the existing site/ lab or lives in a new directory, which the decisions document leaves open.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A toggle switches between operator mode (templates) and developer mode (raw agent output and tool calls)
- [ ] #2 The page is labelled as a recorded run, and works from static files with no server and no API key
- [ ] #3 A not_generated stage and a failed verification display their status and reason
- [ ] #4 The page was opened in a browser and each step checked against the stored run
- [ ] #5 If an artifact file (for example the 3D scene) is missing, the page shows a clear message for that step instead of failing silently
- [ ] #6 Demo A is shown as NOT VERIFIED with its NUMERICAL_DISAGREEMENT status, and Demo C shows its not_generated plot stages with reasons
- [ ] #7 A decision on extending site/ versus a new directory is recorded and applied
- [ ] #8 Picking a demo shows the original request text as the user message in a chat log, before any step appears
- [ ] #9 The pipeline steps then appear one at a time as agent messages, in pipeline order, auto-playing with a delay between steps (default 1.5 s, adjustable through a delay URL parameter)
- [ ] #10 Each step message shows its status and any reason without a click, and can be clicked to show details (artifact, and in developer mode the result and raw events)
- [ ] #11 Playback controls work: pause/resume, next step, show all, restart; changing the demo restarts playback
- [ ] #12 Switching operator/developer mode while playing keeps the steps already shown and changes how they read
- [ ] #13 The page says plainly that the data is sample data until Demo A, B and C are re-captured from real pipeline runs (TJC-21.1)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
- [ ] #3 Project owner has opened the result in a browser, checked it against the acceptance criteria, and approved it before the task is marked Done
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Define a stable artifact manifest and run summary schema under artifacts/runs/<demo_id>/<run_id>/.
2. Update the workflow and GMAT bridge to write canonical artifact names plus explicit step records, including not_generated reasons.
3. Update the static demo page to consume the new run metadata instead of hand-written demo objects, while preserving the existing chat playback behavior.
4. Add or adjust tests to cover artifact naming, step ordering, and site ingestion of the new schema.

5. Extend the saved-run output so completed project-specific steps preserve useful structured results (formalization readiness/content, full model-selection result, and any actually executed solver/verification result), while retaining the current expandable chat rendering.
6. Correct Demo C to be a GEO OUT_OF_SCOPE example: preserve the original natural-language request, show formalization OUT_OF_SCOPE, record downstream steps as not_called/not_generated with truthful reasons, and do not claim CW, two-body fallback, or GMAT verification.
7. Ensure the original request text, not the case ID or filename, is stored in the manifest and rendered as the first operator message.
8. Regenerate the embedded site data and verify direct file:// operation without fetch().
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented static replay page for Demo A/B/C under site/ with operator/developer mode toggle, demo picker, and honest not_generated handling for Demo C. Validation: route wiring and rendering structure added in-repo; browser tooling unavailable in this environment, so only in-repo checks were performed.

Root cause of 'demos do not load / Developer button dead' (reproduced in headless Chrome, console error captured): site/demo-visualization-pipeline.html had a CSP with script-src 'self' AND an inline <script> body, so the browser blocked the only script. Fix: moved the code to site/js/demo-visualization-pipeline.js. Also fixed: duplicated step numbers ('1. 1.'), missing-artifact message (images are referenced; if the file is absent a visible message replaces it), and site/index.html not loading data/demo-runs.js before js/pages/demo-runs.js (old #/demo-runs route now renders). Browser evidence (Chrome headless via DevTools-free harness, http and file://): Demo A/B/C each render 7 steps; operator and developer toggle changes step text and shows/hides raw events; Demo B apostrophe text renders; Demo C shows 3 not_generated steps with reasons and the OUT_OF_SCOPE stop state; Demo A shows 'NOT VERIFIED: NUMERICAL_DISAGREEMENT (WARNING)'. TDD: tests/test_static_demo_page.py RED against the old inline-script page (1 failed), GREEN now; with saved-run and template tests 31 passed. OPEN PROBLEM (not fixed, needs owner decision): the page data does not come from real runs of the Demo A/B/C inputs. None of the referenced artifact PNGs exist (9 of 9 missing). Demo B is shown as VERIFIED/PASS, but the only real 10 km quarter-orbit run on disk (/tmp/tjc_case_quarter_orbit) recomputes to FAIL (~19.6 m, ~0.030 m/s vs 1 m / 0.001 m/s). Demo C (GEO) has transfer_time_s unknown in examples/geo_failure_case.yaml, so a real run would likely stop at NEEDS CLARIFICATION, not VERIFIED; no GEO run exists. Demo A was derived from 1000 m runs, not the 10 km request. Acceptance criteria and DoD left unchecked on purpose.

Decision (AC: extend site/ vs new directory): the demo lives in site/ as a separate standalone page, site/demo-visualization-pipeline.html (script in site/js/demo-visualization-pipeline.js), linked from the sidebar, instead of a route inside the single-page app. Reason: the routed version was fragile, and the standalone page mirrors the walkthrough style. Scope change requested by owner: chat-style playback (request first, steps appear one by one, click to expand, auto-play with delay).

CHAT PLAYBACK BUILT AND BROWSER-VERIFIED. Tests: tests/test_static_demo_page.py gained 4 tests for the chat controls, 1500 ms default delay with ?delay= override, user-message-before-agent-message order and the sample-data label; RED first (4 failed against the non-chat page), GREEN after (8 passed; 35 total with saved-run and template tests). Real-browser run (headless Chrome, delay=200 ms, throwaway harness, removed): request shows first with 0 steps; steps appear one at a time (counts 0..6 then 7); result message shows NOT VERIFIED: NUMERICAL_DISAGREEMENT for Demo A; click expands a step; developer mode keeps the 7 shown steps, changes the text, keeps expanded steps open and shows raw events; restart clears; pause holds the count; next adds exactly one; show-all reveals 7 + result; switching demo restarts; Demo B apostrophe text renders; Demo C shows 3 not_generated messages with reasons visible without a click plus the OUT_OF_SCOPE stop; 4 artifact images each fall back to a visible not-available note (the PNG files do not exist); no window errors. NOT YET DONE: the data is still the hand-written sample (page says so); AC #4 (each step checked against the stored run) and the owner browser check are open.

Reviewed the demo page and artifact layout. Recommendation: add a per-run manifest.json plus run_summary.json, canonical artifact names, and explicit step records so the page can load runs directly without hand-written demo wiring. Also ensure not_generated steps are stored explicitly with reasons, and keep a stable run directory convention under artifacts/runs/<demo_id>/<run_id>/ for seamless future site ingestion.

Scope clarification for the next implementation session: this is an extension of TJC-21.4, not a new task. The immediate goal is not a universal event schema. Preserve data that already exists and keep the implementation small.

Demo A is the real captured one-period Earth 400 km LVLH run at artifacts/runs/earth-400km-one-period-lvlh-rendezvous/bridge/. Demo B is the real captured quarter-period Earth 400 km LVLH run at artifacts/runs/earth-400km-quarter-period-rendezvous/bridge/. Demo C is intentionally a GEO OUT_OF_SCOPE example, not a bounded two-body fallback example. Demo C must stop after formalize_rendezvous_problem returns OUT_OF_SCOPE: no CW solver, no two-body propagation, and no GMAT verification should be represented as completed.

The current site renders empty expandable blocks because the saved manifest reduces completed tool steps to name/status and drops their structured results. At minimum, preserve the formalizer result/readiness, the complete select_rendezvous_model result (selection, qualified, reasons, six assumption statuses, concerns, deterministic_tool, missing_items), and truthful downstream not_called/not_generated reasons. Add solver/GMAT results only when those tools actually ran.

Every saved run must carry the original natural-language request in a request/source_request_text-compatible field. Do not use case_id or a filename as the operator message. The embedded site data must be regenerated so site/data/demo-runs.js contains Demo A/B real captured data, Demo C corrected OUT_OF_SCOPE data, and direct file opening continues to work without fetch().

Do not delete untracked artifact directories without inspecting them; preserve the captured Demo A and Demo B runs. Do not redesign the full manifest architecture, add live streaming, or modify Pi tool contracts unless required for this narrow scope.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @worker
created: 2026-11-13 19:41
---
Owner clarified that Demo C must be GEO OUT_OF_SCOPE (not bounded two-body fallback), and the operator message must be the original request text rather than a case ID. Treat this as approved TJC-21.4 scope for the next session.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Built the static demo replay page with operator and developer modes, demo selection for A/B/C, and honest not_generated/failure-mode display using the saved-run data and operator templates. Verified the new route wiring and static rendering structure in-repo.
<!-- SECTION:FINAL_SUMMARY:END -->
