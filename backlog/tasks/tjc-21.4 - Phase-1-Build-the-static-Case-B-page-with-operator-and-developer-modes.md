---
id: TJC-21.4
title: 'Phase 1: Build the static demo page with operator and developer modes'
status: In Progress
assignee:
  - '@worker'
created_date: '2026-11-10 13:37'
updated_date: '2026-11-20 22:03'
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

9. Point the captured-run contract test at the new demo-a/demo-b run dirs and backfill source_request_text/request plus the recorded formalization and model-selection results into both manifests/summaries (model-selection recomputed through scripts/model_selector_tool_bridge.py, the real deterministic selector, so the stored payload is tool output rather than hand-transcription).

10. Pass source_request_text/formalization/model_selection through the two build_cw_run_manifest call sites (src/workflow.py CW path, scripts/gmat_tool_bridge.py) so future runs capture them automatically.

11. Add Demo C as artifacts/runs/demo-c-400km-quarter-period-14000km-alongtrack/run_manifest.json: READY_TO_SOLVE formalization, UNSUPPORTED model selection (locality violated, two-body coast contract not satisfied), and every downstream step not_called/not_generated with a truthful reason. Drop build_embedded_demo_runs.py's artifacts/saved_runs fallback, which does not exist on disk.

12. Regenerate site/data/demo-runs.js from the three run dirs, correct the page's sample-data banner to the recorded truth, and verify file:// operation in headless Chrome against each stored run.

13. Correct docs/web-demo-cases.md: Demo B's measured 19.60 m FAIL instead of a predicted VERIFIED, and the new 14000 km locality Demo C instead of the GEO framing.

14. Simplify developer-mode artifact detail rendering so image artifacts show the image directly, retaining only the visible unavailable-artifact fallback required by AC #5.

15. Remove the operator-mode toggle and rendering branch at the owner’s request; retain the developer-oriented recorded-run replay as the sole view.

16. Render each recorded request as its natural-language text by stripping only a leading /rendezvous command token from the user-message display; retain the canonical stored request unchanged.

17. Start each replay with an empty chat log. On Play, type the displayed request character by character before scheduling pipeline-step playback; keep playback controls deterministic for pause, next, show-all, restart, and demo changes.

18. Stabilize typed-request playback by preventing the user-message entrance animation and smooth-scroll from restarting on every typed character.

19. Diagnose and make the transition from typed request to agent-step playback explicit, so the first recorded response is scheduled immediately after typing completes.

20. Bound the request-typing duration for the 550–600-character recorded prompts so the first agent response remains promptly visible while retaining a typing effect.

21. Restore the owner-preferred one-character typing cadence and reproduce the browser playback state with a DOM/timer harness before changing the agent-response transition again.

22. Replace generic agent headers with a canonical source label for every recorded pipeline step, naming the rendezvous orchestrator skill, applicable tool, or visualization stage without changing the stored run data.

23. Insert a recorded-calculation table after GMAT verification and before the verification-comparison artifact stage, using only structured saved-run values (burn delta-v components/totals and GMAT comparison metrics) with an honest unavailable state for Demo C.

24. Inspect the recorded visualization artifacts and their generated source/layout, correct clipped labels and legend/graph overlap, regenerate embedded demo data, and verify each visual artifact remains present in the static replay.

25. Re-run the recorded Demo A/B GMAT verification at 20 m position and 0.05 m/s velocity tolerances, regenerate their structured saved-run results/plots, and update the static replay from those real results.

26. Render recorded HTML visualization artifacts inline in the replay with a sandboxed responsive iframe, retaining a clear unavailable fallback instead of exposing only their filesystem-style artifact path.

27. Correct the blank inline Plotly frame by allowing the recorded same-origin HTML artifact to run with the origin context its Plotly runtime requires, while retaining its restricted frame boundary and fallback.

28. Add explicit Plotly controls to the embedded relative-position scene for an Earth overview and a focused target/chaser view that hides the illustrative Earth sphere and constrains the scene to recorded target/chaser coordinates.

29. Make the interactive Earth overview use the available scene width and make the focus control visibly frame the target/chaser path by switching the focused scene to a cube aspect while retaining the full-scale overview.

30. Remove the visible Reason caption from replay response cards while retaining stored reasons in the saved run and developer-detail payload.

31. Replace the long recorded-run banner with a concise closed-by-default disclosure that states the current A/B/C outcomes and retains optional local/custom-run guidance.

32. Slow only the default inter-agent-step playback delay to a more readable pace; preserve the independent 20 ms operator-request typing interval.

33. Separate the 3D scene title, zoom controls, legend, and scene domain into dedicated vertical bands so controls cannot overlay explanatory text.

34. Restore and exceed the prior 3D scene’s usable size by increasing the artifact/frame height while reserving non-overlapping title, control, and legend bands above the scene.

35. Remove the retired educational SPA, its display mirrors, server/runner, and synchronization tool; retain only the standalone recorded-run demo plus its embedded data and update stale repository documentation.

36. Update the root README that GitHub displays with a concise recorded-demo section, its direct-file location, and the current verified/not-verified/unsupported demo outcomes.
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

RE-CAPTURE (parent session, real pipeline tool calls, GMAT R2026a at /home/anna_ford/opt/GMAT/R2026a/bin/GmatConsole-R2026a): Demo A, B and C were re-run through the required pipeline (formalize_rendezvous_problem -> select_rendezvous_model -> solve_cw_rendezvous -> run_gmat_verification) with the visualization stages in pipeline order. New run dirs (old captures left untouched): artifacts/runs/demo-a-400km-one-period-10km-alongtrack/bridge/ and artifacts/runs/demo-b-400km-quarter-period-10km-alongtrack/bridge/, 13 artifacts each.

Owner decision this session: every demo must show its recorded status honestly. Owner also supplied a NEW Demo C prompt, superseding comment #1's GEO OUT_OF_SCOPE framing: same 400 km circular LEO scenario/frame/timing as Demo B but a 14000 km along-track offset (2.07x the 6778.137 km reference radius, ~118 deg of arc). Demo C is therefore a LOCALITY-violation / UNSUPPORTED example, not a GEO out-of-scope example.

RECORDED RESULTS (all from real tool calls, nothing hand-written):
- Formalization: all three READY TO SOLVE (Demo C included; every required field is specified, so the refusal is correctly a model-selection judgment, not a formalizer scope rejection).
- Demo A model selection: CW rendezvous (QUALIFIED), targeting_conditioning=boundary, concern: 'singular but reachable at this transfer time; the returned velocity would be a non-unique SVD minimum-norm solution.'
- Demo A solve: status=singular-reachable, rank 1, condition number 7.7e16, dv0=[0,0.6002086512384345,0], dv1=[2.94e-16,-0.6002086512384345,0], total dv 1.2004173 m/s.
- Demo A GMAT: FAIL / NUMERICAL_DISAGREEMENT, position error 281.46093 m (tol 1 m), velocity error 0.00094833 m/s (tol 0.001).
- Demo B model selection: CW rendezvous (unqualified), all six required items supported, targeting_conditioning supported, no concerns.
- Demo B solve: status=unique, rank 3, condition number 2.8614, dv0=[6.882606529398794,-3.4413032639715575,0], dv1=[6.882606529398794,3.441303263971557,0], total dv 15.389976 m/s.
- Demo B GMAT: FAIL / NUMERICAL_DISAGREEMENT, position error 19.59965 m (tol 1 m), velocity error 0.029826 m/s (tol 0.001).
- Demo C model selection: UNSUPPORTED, deterministic_tool=null, reasons: 'Violated CW assumption(s): locality.' plus the bounded-two-body-coast contract not being satisfied (it is a targeting request with burns, not a coast). Pipeline correctly stops here: no solve, no GMAT, no plots.

OPEN ITEM FOR OWNER (docs vs evidence): docs/web-demo-cases.md predicts Demo B VERIFIED. The real GMAT run does NOT pass (19.6 m vs 1 m tolerance). Both Demo A and Demo B are honest NOT VERIFIED / NUMERICAL_DISAGREEMENT. That document needs correcting; the page must show the recorded FAIL, not the predicted pass.

PARENT-SESSION ERROR WORTH RECORDING: the first run_gmat_verification call used a repo-relative output_dir and returned MALFORMED_OUTPUT ('GMAT report file does not exist'), because GMAT's working directory is its own bin/. Re-running with an ABSOLUTE output_dir produced the real comparison. Use absolute output_dir paths for this tool.

SUBAGENT FAILURES (no work lost): worker a0c14bab timed out at 30 min with zero changes; resume 8eecfd03 failed instantly ('text content blocks must be non-empty', unresumable session); workflow slice1 a7c5e612 timed out at 60 min but left sound uncommitted work in src/workflow.py (+84/-5: source_request_text/formalization/model_selection kwargs, seven canonically-ordered steps, structured per-step results, GMAT not_called handling) and tests/test_run_manifest_contract.py (+163, 4 new tests). That code is what produced the correct 7-step manifests above; 11 passed / 4 failed at handoff, the 4 failures being the old captured runs lacking request text.

FINISH (parent session). Wired the re-captured runs into the page and made all three demos honest.

Test evidence: RED 'assert None == /rendezvous Earth is the central body...' for test_workflow_cw_path_records_request_text_and_prose_step_results and test_gmat_tool_bridge_records_the_request_text_and_results_it_is_given (2 failed, request text/structured results not yet threaded through the call sites); GREEN after wiring: 59 passed in 104.78s for the targeted subset.

Full suite: 32 failed, 277 passed (192.57s). The 32 failures are PRE-EXISTING and unrelated: verified by stashing all of this task's changes and re-running on a clean HEAD 99259e5, which gives the SAME 32 failures with 260 passed. This task therefore adds 17 passing tests and zero new failures. The pre-existing failures are missing committed fixtures under evaluations/formalizer/ and evaluations/benchmark/ (FileNotFoundError), i.e. absent evaluation corpus files, not behavior regressions.

Site data verified statically (no browser needed): parsed site/data/demo-runs.js and asserted each embedded run against its run_manifest.json. Demo A outcome NUMERICAL_DISAGREEMENT/verified=false with all 7 steps and structured results on formalize/select/solve/GMAT; Demo B identical shape and also NUMERICAL_DISAGREEMENT/verified=false; Demo C outcome UNSUPPORTED/verified=false with formalize+select completed and all five downstream steps not_called/not_generated each carrying a truthful reason. Every demo's request field holds the real natural-language request text, not a case_id.

NO BROWSER AVAILABLE in this environment: both Playwright Chromium builds fail with 'libnspr4.so: cannot open shared object file' and installing system libraries needs sudo (not authorized). AC #4 (each step checked against the stored run in a browser) and DoD #3 (owner approval) are therefore left UNCHECKED and are owner-side. No browser evidence is claimed.

Cleaned up test side effects before committing: tests regenerate artifacts/visualizations/relative_position_3d.html and create artifacts/runs/bridge_test_case/; both were reverted/removed so they stay out of this commit.

REMAINING OWNER ITEMS: (1) open site/demo-visualization-pipeline.html and check each demo's steps against its stored run (AC #4, DoD #3). (2) No demo shows a PASS -- Demo A and B are both honest NOT VERIFIED. (3) Worth a separate task: Demo B's 19.6 m error over a quarter period is large enough that the verification report itself suggests a frame/unit/state-ordering mismatch in the CW-to-GMAT mapping rather than ordinary linearization error; Demo A's 281 m error is explained by its singular (rank-1, cond 7.7e16) targeting matrix at exactly one period.

Developer-image cleanup: RED: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_developer_mode_renders_visual_artifacts_without_textual_step_chrome -> FAILED because developerImageMessage did not exist. GREEN: added a developer-only image-artifact renderer that omits the step title, status, narrative, artifact path, and raw JSON; retained the visible missing-artifact fallback. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 14 passed.

Owner removed the operator-mode requirement. RED: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_page_has_no_operator_mode_or_mode_toggle -> FAILED because the Operator mode button was still present. GREEN: removed the operator/developer toggle and operator-rendering branch; the replay now uses developer-oriented content as its sole view. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 15 passed.

Request-label cleanup: RED: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_user_message_omits_the_rendezvous_command_prefix -> FAILED because no displayRequest formatter existed. GREEN: the chat user-message formatter now strips exactly one leading, case-insensitive /rendezvous command token while preserving the canonical stored request. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 16 passed.

Typed-request playback: RED: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_replay_starts_blank_and_play_types_the_request_before_steps -> FAILED because no typing state or delay existed. GREEN: the replay now starts with an empty chat log; Play types the displayed request at 20 ms per character (overridable with ?typingDelay=), then starts the existing per-step playback. Pause stops either phase; Next completes a partial request before stepping; Show all completes the request and steps; Restart and demo changes return to the blank state. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 17 passed.

Typed-request stability: RED: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_typed_user_request_does_not_restart_entrance_animation_or_scroll -> FAILED because each character update re-triggered the generic message animation. GREEN: disabled the entrance animation specifically for the user request and stopped per-character smooth scrolling; agent steps retain their entrance animation and scroll behavior. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 18 passed.

Typed-to-agent handoff: RED: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_first_agent_step_starts_when_request_typing_completes -> FAILED because completing typing only re-entered the timer scheduler, leaving no explicit first-response handoff. GREEN: on the final typed character, the page reveals the first agent step immediately and then schedules the remaining recorded steps at the configured inter-step delay. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 19 passed.

Prompt-duration fix: the recorded requests are 553–602 characters, so one character per 20 ms delayed the first response by roughly 11–12 seconds. RED: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_long_recorded_requests_are_typed_in_bounded_chunks -> FAILED because typing advanced one character per timer tick. GREEN: each 20 ms tick now adds four characters, keeping the typing effect while reducing recorded-request typing to about 3 seconds before the immediate first agent response. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 20 passed.

Playback root-cause fix: removing the mode toggle left one  guard in step rendering. As soon as the first agent step was revealed, browsers threw , so no response could render. Restored the owner-preferred one-character-per-20-ms typing pace and removed the stale guard (the sole view always renders recorded result/raw details). RED: two focused checks failed for the stale mode reference and changed typing increment. GREEN: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 20 passed. A Node DOM/timer harness also confirmed , followed by  after Play-driven typing.

Correction to the preceding shell-recorded note: the stale condition was mode === developer, and the browser error was ReferenceError: mode is not defined. The command shell removed those literals from the preceding prose; this note is the accurate record.

Source-label headers: RED: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_pipeline_steps_use_skill_or_tool_source_labels -> FAILED because every response used the generic Agent header. GREEN: mapped all seven canonical pipeline steps to explicit orchestrator-skill, tool, or artifact-stage labels; the final result is identified as the orchestrator recorded-run summary. The picture-only artifact cards remain picture-only as requested. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 21 passed.

Recorded-calculation table: RED: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_recorded_calculation_table_follows_gmat_and_precedes_comparison_plots -> FAILED because no calculation table existed. GREEN: inserted a table immediately after the GMAT step, before the verification-comparison stage. It derives targeting status, transfer time, both RIC burn vectors, total delta-v, matrix rank/conditioning, GMAT status, and GMAT position/velocity errors solely from each saved run. Demo C truthfully says the values are unavailable because no solve or GMAT verification ran. The Node DOM/timer replay confirmed table=true, after_gmat=true, before_comparison=true. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 22 passed.

Visualization-layout cleanup: RED: uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_visualization_renderers_reserve_space_for_legends_and_titles -> FAILED because the three renderers did not reserve layout space. GREEN: moved the trajectory/burn legend below the equal-scale axes; placed both comparison-plot legends outside their axes; wrapped long case identifiers into titled header space; saved static plots with tight bounding boxes; and put the interactive Plotly legend outside the 3D scene with explicit margins for the title, legend, and annotation. Re-rendered Demo A/B scene, trajectory/burn, comparison-trajectory, and error-history artifacts, then rebuilt embedded site data. Inspected the regenerated Demo A static artifacts: labels are wholly visible and legends do not cover plot data. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py tests/test_visualization_relative_trajectory.py tests/test_visualization_gmat_comparison.py tests/test_visualization_relative_position_3d.py -> 37 passed.

Tolerance re-verification: independently re-ran GMAT for the two recorded CW cases with position tolerance 20 m and velocity tolerance 0.05 m/s, writing to their existing absolute bridge directories. Demo A remains FAIL / NUMERICAL_DISAGREEMENT (281.46093 m position error). Demo B is now independently VERIFIED: 19.59965 m and 0.029826 m/s both fall within the new tolerances. Preserved each run’s original request, formalization, and model-selection data; regenerated embedded page data and updated the cases document. Tests initially exposed obsolete assertions that every GMAT-run demo must fail; updated them for the intentional reverified Demo B outcome. GREEN: PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py tests/test_run_manifest_contract.py -> 41 passed.

Inline 3D artifact: RED: PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_html_visualization_artifacts_render_inline_not_as_a_path_only -> FAILED because HTML artifacts rendered only their path. GREEN: added a sandboxed, responsive iframe for text/html artifacts; artifact-root paths resolve from the site page to the sibling repository artifacts directory when opened directly from the UNC/file URL. The iframe has the same explicit unavailable fallback as image artifacts. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 23 passed.

Inline-frame blank-box correction: inspected the recorded Demo B Plotly HTML directly in Windows Edge headless; it rendered successfully as a 1000x700 screenshot, so the artifact/path was valid. The iframe had sandboxed scripts into an opaque origin, which prevented the embedded Plotly runtime from using its expected same-origin context. RED: PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_html_visualization_artifacts_render_inline_not_as_a_path_only -> FAILED because the iframe lacked allow-same-origin. GREEN: added allow-same-origin alongside allow-scripts for this recorded local artifact frame. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 23 passed.

3D scene view controls: RED: PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_visualization_relative_position_3d.py::test_scene_includes_target_chaser_zoom_and_earth_overview_controls -> FAILED because the figure had no view controls. GREEN: added Plotly buttons for Zoom to target and chaser (hides the illustrative Earth and constrains axes around target/chaser coordinates) and Earth overview (restores the Earth and autorange). Regenerated Demo A/B interactive scene artifacts. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py tests/test_visualization_relative_position_3d.py -> 30 passed.

3D scene sizing/focus refinement: RED: the focus-view test failed because it did not switch to cube aspect, and then failed because the interactive figure had no explicit height. GREEN: the focus button now sets cube aspect (so the target/chaser path fills its focused view); the Earth overview uses the full scene width with a horizontal top legend; and the Plotly figure has a 620 px height so the Earth scene occupies substantially more of the embedded frame. Regenerated Demo A/B scene artifacts. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py tests/test_visualization_relative_position_3d.py -> 30 passed.

Reason-caption cleanup: RED: PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_response_cards_do_not_show_a_reason_caption -> FAILED because response cards rendered a visible Reason label. GREEN: removed that presentation row; the structured saved-run reason fields remain intact. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 24 passed.

Recorded-run disclosure cleanup: RED: PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_page_uses_a_concise_disclosure_for_current_recorded_run_outcomes -> FAILED because the page used a long, stale banner claiming all three demos failed at 1 m. GREEN: replaced it with a closed-by-default About these recorded demos disclosure containing the current concise outcomes (A not verified, B verified at 20 m / 0.05 m/s, C unsupported) and one short local custom-run hint. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 24 passed.

Playback pacing: RED: PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py::test_agent_playback_defaults_to_2500ms_without_changing_typing_timing -> FAILED because agent steps still defaulted to 1500 ms. GREEN: agent steps now default to 2500 ms; the independent operator-request typing interval remains 20 ms. The delay URL parameter still overrides the agent-step delay. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py -> 24 passed.

3D control/text overlap: RED: the scene-layout test failed because the scene occupied the full vertical domain and controls had no dedicated band. GREEN: created separate vertical bands: title at 0.98, zoom controls at 0.84, legend at 0.74, and the 3D scene in y=[0, 0.67]. This prevents control/text overlap. Regenerated Demo A/B scene artifacts. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py tests/test_visualization_relative_position_3d.py -> 31 passed.

3D layout correction after owner feedback: the prior 0.67 scene domain made the visualization too small. RED: focus-layout test failed after raising the required scene dimensions. GREEN: increased the Plotly artifact and iframe height to 780 px, expanded the scene domain to 0.75, and retained separated title/control/legend bands (0.98/0.88/0.79) to avoid overlap while restoring a larger usable scene. Regenerated Demo A/B scene artifacts. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py tests/test_visualization_relative_position_3d.py -> 31 passed.

Retired-site removal: removed the legacy educational SPA, its CSS, page modules, pedagogical JS, mirrored source/reference/evaluation files, Node server, root runner, and mirror-sync tool at the owner’s request. Retained only the standalone replay page, its required JavaScript, and its embedded run data. Removed the demo page’s obsolete CSS dependency and documented that the retained site surface is serverless. Updated the embedded-run builder documentation for iframe-rendered HTML artifacts. PYTHONPATH=. uv run --with-requirements requirements-dev.txt pytest -q tests/test_static_demo_page.py tests/test_run_manifest_contract.py -> 43 passed. Confirmed the retained site tree has exactly site/demo-visualization-pipeline.html, site/js/demo-visualization-pipeline.js, and site/data/demo-runs.js.

Root README update: added the GitHub-displayed Recorded rendezvous demo section, identifies the standalone replay file, states it opens locally without a server/API key, and summarizes the current recorded Demo A/B/C outcomes and tolerance contract.
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
