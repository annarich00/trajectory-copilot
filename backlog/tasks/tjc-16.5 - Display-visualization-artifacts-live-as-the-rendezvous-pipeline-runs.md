---
id: TJC-16.5
title: Display visualization artifacts live as the rendezvous pipeline runs
status: Done
assignee:
  - '@worker'
created_date: '2026-10-30 16:39'
updated_date: '2026-11-04 20:51'
labels: []
dependencies:
  - TJC-16.2
  - TJC-16.3
  - TJC-16.4
parent_task_id: TJC-16
priority: medium
type: feature
ordinal: 66000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The operator wants to demo this live to their advisor and see each visualization pull up progressively as the agent works through the rendezvous pipeline (formalize -> model-select -> solve -> GMAT verify), not just receive a bundle of artifact paths at the very end. This wires the already-produced plots (TJC-16.2 3D relative-position scene, TJC-16.3 trajectory/burns plot, TJC-16.4 verification comparison plot) into the existing .pi/prompts/rendezvous.md pipeline and src/workflow.py::run_rendezvous_workflow so each artifact is generated and surfaced as soon as its underlying stage completes, ending with the already-existing GMAT GUI screenshot/execution step.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 src/workflow.py::run_rendezvous_workflow (or a thin wrapper used by .pi/prompts/rendezvous.md) generates the TJC-16.2 3D relative-position scene immediately after problem formalization/model selection, before the CW/two-body solve runs, using the formalized initial/target relative state
- [x] #2 The TJC-16.3 trajectory/burns plot is generated immediately after the deterministic CW or two-body solve completes and before GMAT execution begins, not deferred to the end of the run
- [x] #3 The TJC-16.4 verification comparison plot is generated immediately after GMAT execution and parsing complete, using the same run's GMAT report output
- [x] #4 .pi/prompts/rendezvous.md is updated so each stage's newly generated artifact path is reported to the operator as soon as it is produced, in pipeline order, rather than only in the final step-4 summary, while preserving every existing required step/order/wording constraint already in that prompt
- [x] #5 The final stage of the displayed sequence remains the existing GMAT execution and GUI screenshot/preview-script handoff already defined in run_rendezvous_workflow and rendezvous.md step 5, unchanged by this task
- [x] #6 A test or recorded manual run demonstrates all four artifacts (3D scene, trajectory/burns plot, verification comparison plot, GMAT screenshot) are produced and reported in pipeline order for one real end-to-end case
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-16.5:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add src/workflow_visualization.py (thin glue over the TJC-16.2/16.3/16.4 plots; records {stage,status,paths,reason}). 2. Wire into run_rendezvous_workflow via an on_artifact callback + artifacts['visualization_artifacts']: CW path = scene before solve, trajectory/burns plot via a new on_solution hook in run_cw_rendezvous_gmat_verification (after solve, before GMAT), comparison after GMAT parse; two-body path = explicit not_generated entries with reasons (approved by supervisor; no approximate plots). 3. scripts/rendezvous_visualization_stage.py CLI so .pi/prompts/rendezvous.md can report each artifact live around the run_gmat_verification pi tool. 4. Update .pi/prompts/rendezvous.md preserving existing wording. 5. Tests (red then green) incl. a real-GMAT end-to-end test; full suite.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
SCOPE DECISION (supervisor-approved): TJC-16.2/16.3/16.4 plots are LVLH-relative and two-burn specific. CW path is fully wired. The bounded two-body path has no relative state, burns, or solver state history (RendezvousCase carries only an inertial Cartesian state + coast duration), so its three stages are recorded as explicit status='not_generated' entries with concrete reasons rather than approximate plots (that would be new physics). Impact on AC wording: AC1-AC3 are fully satisfied for the CW path; for the two-body path the stage is reported (not_generated + reason), not plotted. TIME-BASE NOTE for AC3: plot_cw_vs_gmat_comparison forbids interpolation and requires identical time bases; GMAT's d_trajectory.txt samples at its own 17 propagator steps while solve_cw_rendezvous uses a 50-point grid, so comparison_stage evaluates the same solver's analytic CW STM (src/cw.py::propagate_relative_state from the post-burn-1 state) at exactly GMAT's reported times. Nothing is interpolated or resampled; independently recomputed max position error vs GMAT = 0.00794 m, velocity 1.17e-05 m/s (consistent with the PASS final-state comparison). Also added a small on_solution hook to scripts/run_cw_gmat_slice.py::run_cw_rendezvous_gmat_verification (invoked right after the solve, before any GMAT script/exec); GMAT execution and screenshot handoff code is unchanged. The comparison plot path is also written into unified_verification_report['comparison_plot_path'] (TJC-16.4 field). tests/test_workflow.py singular-infeasible test updated: the scene is now (correctly) generated pre-solve, so the dir contains exactly relative_position_3d.html and nothing from GMAT. Worktree .venv created at the worktree (python3.14, requirements-dev.txt) and is gitignored.

TDD EVIDENCE. RED (written before implementation): '.venv/bin/python -m pytest tests/test_workflow_visualization.py -q' -> 6 failed, all 'TypeError: run_rendezvous_workflow() got an unexpected keyword argument on_artifact' (tests exercise the not-yet-existing on_artifact/visualization_artifacts behavior). GREEN after implementing src/workflow_visualization.py + workflow.py wiring: 6 passed. tests/test_rendezvous_visualization_stage_cli.py: RED 'ModuleNotFoundError: No module named scripts.rendezvous_visualization_stage' (collection error), GREEN 5 passed after adding the CLI; its prompt-order test (added later) was RED against the unmodified .pi/prompts/rendezvous.md (ValueError: substring not found 'rendezvous_visualization_stage.py scene'), GREEN 6/6 after updating the prompt. Full suite (GMAT on PATH, real GmatConsole-R2026a): '.venv/bin/python -m pytest -q' -> 206 passed in 154.7s (190 baseline-ish + 16 new; one earlier run failed only the stale 'tmp_path empty' assertion in test_singular_infeasible_..., fixed as described above).

END-TO-END RECORDED RUN (real GMAT, no fakes; CW case _cw_ready_case, GmatConsole-R2026a + real GMAT GUI screenshot attempt, run_rendezvous_workflow with on_artifact printing as produced): [0.2s] ARTIFACT relative_position_3d_scene: generated [/tmp/tjc165_run/relative_position_3d.html]; [0.3s] ARTIFACT trajectory_burns_plot: generated [/tmp/tjc165_run/trajectory_burns_plot.png]; (GMAT GUI screenshot attempt + console GMAT run, d_*.txt ReportFile written 15:41:48.6) [8.6s] ARTIFACT verification_comparison_plot: generated [.../tjc16_5_e2e_cw_vs_gmat_trajectory.png, .../tjc16_5_e2e_cw_vs_gmat_error_history.png]; final: outcome=VERIFIED verified=True, screenshot trajectory_gmat_gui.png source=gmat_gui captured a non-blank 1024x768 GMAT GUI render. File mtimes: html 15:41:40.96 < trajectory png 15:41:41.14 < GUI screenshot 15:41:47.89 < d_trajectory.txt 15:41:48.63 < comparison trajectory png 15:41:48.97 < error-history png 15:41:49.40, i.e. pipeline order. Same case is also an automated test: tests/test_workflow_visualization.py::test_real_gmat_end_to_end_cw_case_produces_all_artifacts_in_pipeline_order (skipped when GmatConsole-R2026a is unavailable; passed here). Note: GMAT GUI screenshot is produced inside the unchanged run_cw_rendezvous_gmat_verification step before the console run, as before; it remains the existing handoff (final displayed item per prompt step order). Not run: the pi TS tool / full interactive /rendezvous prompt session (cannot be driven from this subagent); the prompt's CLI commands are covered by tests/test_rendezvous_visualization_stage_cli.py.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Wired the TJC-16.2/16.3/16.4 plots into src/workflow.py::run_rendezvous_workflow at their stage boundaries (new src/workflow_visualization.py glue, on_artifact callback, artifacts['visualization_artifacts']): 3D scene after model selection and before the solve; trajectory/burns plot right after the solve (new on_solution hook in the slice runner) and before GMAT; comparison plot after GMAT execution/parsing (CW STM evaluated at GMAT's own report times, no interpolation). The bounded two-body path records explicit not_generated entries with reasons (supervisor-approved; no approximate plots). Added scripts/rendezvous_visualization_stage.py and updated .pi/prompts/rendezvous.md so each artifact path is reported as produced, keeping all prior wording; GMAT execution/screenshot handoff unchanged. Verified by a real-GMAT end-to-end test and recorded run showing all artifacts in pipeline order, red-then-green evidence in notes, and the full suite: 206 passed.
<!-- SECTION:FINAL_SUMMARY:END -->
