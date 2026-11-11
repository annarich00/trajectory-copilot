---
id: TJC-23.6
title: Re-express /rendezvous prompt as a skill
status: Done
assignee:
  - '@worker'
created_date: '2026-11-11 14:45'
updated_date: '2026-11-11 20:37'
labels: []
dependencies:
  - TJC-23.2
  - TJC-23.3
  - TJC-23.4
  - TJC-23.5
parent_task_id: TJC-23
priority: high
type: feature
ordinal: 91000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The user wants the orchestration currently in .pi/prompts/rendezvous.md turned into a skill: step ordering, stop conditions, visualization stage timing, and the GMAT-example review hookup, re-expressed as a .pi/skills/*/SKILL.md the agent applies the same way the other rendezvous skills were applied before their own tool conversions. Scope is limited to the prompt-to-skill re-expression only -- this task does not convert that new skill into a registered pi tool call; it depends on TJC-23.2 through TJC-23.5 only because the new skill must instruct the agent to call those already-converted tools (and the existing run_gmat_verification tool) in the documented order, not because this task itself produces another tool.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The orchestration logic in .pi/prompts/rendezvous.md (step ordering, stop conditions, visualization stage timing, GMAT-example review hookup) is captured in an intermediate skill definition
- [x] #2 The stop conditions (NEEDS CLARIFICATION / OUT OF SCOPE halt, single-spacecraft coast exception) and the gmat-example-reviewer subagent handoff are preserved
- [x] #3 The new skill reproduces the prompt's documented behavior (confirmed by an end-to-end test or manual run covering at least one CW and one bounded-two-body case) and .pi/prompts/rendezvous.md is then removed, so the orchestration lives only in the skill, not duplicated in both places
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.6: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create .pi/skills/rendezvous-pipeline-orchestrator/SKILL.md (portable Agent Skills frontmatter: name/description only; no argument-hint/slash-prompt fields) that re-expresses .pi/prompts/rendezvous.md's 6 numbered steps verbatim-equivalent: step1 formalizer tool call + single-spacecraft-coast OUT-OF-SCOPE exception + NEEDS CLARIFICATION/OUT OF SCOPE halt; step2 model-selector tool call + visualization-stage-timing instructions; step3 CW-path (solve via run_gmat_verification, scene/trajectory/comparison stage CLI calls in order) vs bounded-two-body-path (run_rendezvous_workflow, not_generated stage reporting) branching; step4 gmat-example-reviewer subagent handoff (advisory/stylistic, NO CORPUS ENTRY handling, non-blocking on subagent failure, never self-authored verdicts); step5 final report step; step6 optional interactive GUI launch step. Replace the old prompt's '$ARGUMENTS' substitution with an instruction to apply the skill to the operator's rendezvous request text already in context.
2. Update tests/test_rendezvous_prompt_reviewer_step.py and the one affected test in tests/test_rendezvous_visualization_stage_cli.py (test_rendezvous_prompt_reports_artifacts_in_pipeline_order_and_keeps_existing_constraints) to read the new skill file's path instead of .pi/prompts/rendezvous.md, preserving every existing assertion/invariant (rename PROMPT constant's source path only; keep assertions and _step() helper working against the skill's numbered steps).
3. Update prose path-references in src/gmat_verify.py, src/workflow_visualization.py, scripts/rendezvous_visualization_stage.py from '.pi/prompts/rendezvous.md' to the new skill file path.
4. Minimal AGENTS.md fix: update the two '.pi/prompts/rendezvous.md' references in the rendezvous-routing-rule section to point at the new skill file path, without rewriting the rest of that section (full sync is TJC-23.7).
5. Update docs/web-interface-decisions.md's 'Pending: TJC-23' table row for the '/rendezvous prompt' element: mark it done, naming the new skill and noting the prompt file was removed; leave the rest of that table/file alone (other rows belong to other TJC-23 subtasks/TJC-21).
6. Delete .pi/prompts/rendezvous.md.
7. Check docs/baseline-checksums.md (no entry for this file -- confirm no edit needed), tools/sync_site_data.py and tools/compare_upstream.py for references to .pi/prompts/rendezvous.md or the new skill path; apply the same minimal reference-cleanup pattern TJC-23.4/23.5 used (scoped strictly to the deleted/added file, not a wider sync).
8. Run the two updated test files, then the full suite (.venv/bin/python -m pytest -q), comparing against the known baseline (255/261 passed + 1 pre-existing unrelated failure per TJC-23.4/23.5 notes) to confirm no new failures introduced.
9. Execute AC3 evidence: manually walk through the new skill as the acting agent for one CW case (reusing examples/cw_gmat_vertical_slice.yaml's parameters) and one bounded-two-body case (reusing evaluations/benchmark/case_c_two_body.json's parameters), calling the real registered pi tools (formalize_rendezvous_problem, select_rendezvous_model, solve_cw_rendezvous/propagate_two_body_coast, run_gmat_verification) and the subagent tool for the gmat-example-reviewer handoff, recording tool calls/outcomes/stop-conditions/artifacts at each step honestly (including any step infeasible in this sandbox).
10. Record the AC3 transcript/evidence via --append-notes, finalize ACs/DoD with evidence, write final summary, mark Done, then make exactly one atomic git commit 'TJC-23.6: ...' (implementation first, then amend in the Backlog finalization metadata) containing only this task's changes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## AC3 evidence: CW case (restored from prior worker, confirmed genuine)

A prior worker session ran a complete end-to-end CW-case walkthrough following
the restored `.pi/skills/rendezvous-pipeline-orchestrator/SKILL.md` by
launching a nested `pi` CLI session that actually invoked the real registered
pi tools. Transcript/results captured at `/tmp/tjc23_6_cw_run.jsonl` (4446
lines) and `/tmp/tjc23_6_cw_toolresults.txt`; artifacts at
`/tmp/tjc23_6_ac3_cw/`. Inspected directly by this worker and confirmed
genuine (not fabricated):

- Request (`/tmp/tjc23_6_cw_request.txt`): `/skill:rendezvous-pipeline-orchestrator`
  invocation for Earth mu=398600441800000.0 m^3/s^2, chief at 350 km altitude
  (ref radius 6728000.0 m), chaser relative state [15,-200,0] m /
  [-0.14,0,0] m/s, two impulsive burns over a quarter orbital period,
  output_dir `/tmp/tjc23_6_ac3_cw`.
- Step 1: `formalize_rendezvous_problem` called 5 times (first attempts
  rejected by the tool's own `formalizationSummary` two-sentence limit --
  real input-validation errors, not fabricated), then succeeded with
  `Readiness: READY TO SOLVE`.
- Step 2: `select_rendezvous_model` returned `CW rendezvous`, all six
  assumption items `supported`, `deterministic_tool: src.cw.two_burn_targeting`.
- Step 3: `run_gmat_verification` called explicitly (case_id
  `tjc23_6_ac3_cw`, `gmat_executable="GmatConsole-R2026a"`). Real GMAT
  console execution occurred (stdout shows genuine GMAT R2026a console
  banner/engine init/script interpretation/command sequence, exit_status 0).
  Result: `verified=true`, dv0=[-0.0200727,0.0457153,0] m/s,
  dv1=[-0.1429122,-0.0800364,0] m/s, total ΔV=0.213726 m/s, GMAT comparison
  PASS (position error 7.94e-3 m, velocity error 1.17e-5 m/s, both within
  tolerance). Scene/trajectory/comparison visualization artifacts produced
  at `/tmp/tjc23_6_ac3_cw/` (`relative_position_3d.html`,
  `trajectory_burns_plot.png`, `trajectory.svg`,
  `tjc23_6_ac3_cw_cw_vs_gmat_trajectory.png`,
  `tjc23_6_ac3_cw_cw_vs_gmat_error_history.png`), plus
  `generated_cw_rendezvous.script` (real GMAT script, inspected directly).
- Step 4: the `subagent` tool really was called for the `gmat-example-reviewer`
  handoff (visible `subagent` tool-use block in the transcript, real run ID,
  real completed mission). It returned `NO CORPUS ENTRY` (the corpus's
  controlled mission-type vocabulary has no rendezvous/LVLH entry, as
  `docs/gmat-example-reviewer-example-run.md` already documents) plus
  advisory, non-blocking stylistic notes. The numerical VERIFIED result was
  reported independently of, and unaffected by, this advisory verdict.
- Step 5: final report stated `VERIFIED` plainly, listed all artifact paths,
  and reported the step-4 review as a separate advisory item, matching the
  skill's required shape exactly.

This case fully exercises the skill's step 1-5 CW path, including a real
GMAT console run and a real gmat-example-reviewer subagent handoff.

## AC3 evidence: bounded two-body case (run directly by this worker)

Per an explicit supervisor decision (this worker's own tool allowlist has no
direct function-call access to the registered pi tools or to the `subagent`
tool, and was directed not to spawn a second nested `pi` CLI subprocess to
avoid repeating the prior timeout), this case was walked through by calling
the exact same deterministic Python each registered tool is documented as a
thin wrapper/relay around, directly via `.venv/bin/python`, reusing
`evaluations/benchmark/case_c_two_body.json`'s real parameters (Earth
mu=398600441800000.0 m^3/s^2, initial inertial Cartesian state
[7778000,0,0,0,7158.7124559338245,0] m/m/s, 900 s point-mass coast, no
burns/targeting -- the case the skill's step 1 single-spacecraft-coast
exception and step 2 locality/other_physics-violated assessment route to the
bounded two-body fallback, not the formalizer).

- Step 1 (skill's single-spacecraft-coast exception): this request has no
  second spacecraft/relative frame/targeting objective, so per the skill it
  correctly skips `formalize_rendezvous_problem` (OUT OF SCOPE for the
  formalizer by design) and proceeds straight to step 2, exactly matching
  `evaluations/benchmark/case_c_two_body.json`'s own committed precedent.
- Step 2: ran `scripts/model_selector_tool_bridge.py` directly (the exact
  script `.pi/extensions/orbital-model-selector-tool`'s `select_rendezvous_model`
  tool shells out to via `pi.exec`, relayed verbatim) with
  circularity/duration_regime/frame/maneuver_assumptions=supported,
  locality/other_physics=violated (the 1,000+ km-scale inertial coast is not
  local LVLH relative motion). Result: `selection: "bounded two-body
  fallback"`, `deterministic_tool: "src.twobody.propagate_cartesian_state"`,
  reasons `"Violated CW assumption(s): locality, other_physics."` --
  matching the benchmark case's `expected_model` exactly.
- Step 3 (bounded-two-body path): called
  `src/workflow.py::run_rendezvous_workflow` directly (as the skill's step 3
  instructs for this path) with a `RendezvousCase`/`ModelSelectionCase`
  built from the exact values above, `output_dir=/tmp/tjc23_6_ac3_twobody`,
  `gmat_executable="GmatConsole-R2026a"`. This is the real, unmodified
  production code path (not a mock): it ran `select_model` internally,
  propagated via `src.twobody.propagate_cartesian_state`, generated a real
  GMAT script (`/tmp/tjc23_6_ac3_twobody/generated_two_body_coast.script`,
  inspected directly), and executed real GMAT console verification.
  Result: final state [5258694.860896885, 5730917.235484777, 0,
  -5274.619259140002, 4839.995423329594, 0] m/m/s (byte-for-byte identical to
  `evaluations/benchmark/case_c_two_body.json`'s
  `reference_numerical_result.summary.final_state_m_mps`), GMAT comparison
  `status: PASS` (position error 2.178e-3 m, velocity error 5.254e-6 m/s,
  also identical to the benchmark's recorded `gmat_position_error_m`/
  `gmat_velocity_error_mps`), `verified: true`,
  `verification_status: "VERIFIED"`. A real GMAT GUI screenshot was also
  captured (`trajectory_gmat_gui.png`, 144895 bytes, self-managed Xvfb).
  All three visualization stages (scene/trajectory-burns/comparison) were
  correctly reported `not_generated` with a concrete `reason` each (no LVLH
  relative state to render, no CW burns/state-history to plot) -- exactly
  the behavior the skill's step 3 bounded-two-body branch and the "never
  substitute a fabricated plot" rule require.
- Step 4 (gmat-example-reviewer handoff): **not performed**. This worker's
  tool allowlist has no `subagent` tool access, so per the skill's own
  documented fallback for this exact situation: "GMAT-example review
  skipped/unavailable: subagent tool not available to this worker." No
  verdict was faked or paraphrased.
- Step 5: final result is `VERIFIED` (solver succeeded AND GMAT
  independently confirmed it), stated plainly above, independent of the
  skipped step-4 review.

This case fully exercises the skill's step 1 single-spacecraft-coast
exception, step 2 model selection, and step 3 bounded-two-body path
(including a real GMAT console run), via the exact underlying deterministic
code the registered pi tools wrap -- not a literal pi-tool function call,
and honestly reported as such -- with step 4 honestly reported as
unavailable rather than faked.

## Test/suite results

Both updated test files pass after the restore
(`tests/test_rendezvous_prompt_reviewer_step.py`: all passing;
`tests/test_rendezvous_visualization_stage_cli.py`: 1 pre-existing failure,
confirmed below, 13 passing). Full suite:
`.venv/bin/python -m pytest -q` -> 2 failed, 272 passed. Both failures
confirmed pre-existing and unrelated to this change (verified via
`git stash`/clean-tree comparison against commit 820657d before this
task's changes were applied):
- `tests/test_cw_gmat_slice.py::test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window`
  -- flaky PNG-size comparison between two Xvfb-rendered screenshots,
  unrelated to this task, fails identically on the pre-change tree.
- `tests/test_rendezvous_visualization_stage_cli.py::test_rendezvous_prompt_reports_artifacts_in_pipeline_order_and_keeps_existing_constraints`
  -- asserts a string ("exactly this: state plainly that an interactive GMAT
  window cannot be") that is no longer present in the *source*
  `.pi/prompts/rendezvous.md` prose either (confirmed failing identically
  against the pre-change tree at commit 820657d, before this task's rename);
  a pre-existing prompt/test drift unrelated to this task's skill
  re-expression, not introduced by it.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Re-expressed .pi/prompts/rendezvous.md's 6-step orchestration (formalizer call + single-spacecraft-coast exception + stop conditions; model-selector call + visualization-stage timing; CW-path vs bounded-two-body-path branching; gmat-example-reviewer subagent handoff; final report; optional GUI launch) as .pi/skills/rendezvous-pipeline-orchestrator/SKILL.md, preserving every stop condition and the reviewer handoff verbatim-equivalent, then deleted the retired prompt file. Updated the two tests that read the prompt file to read the skill file instead (same invariants, same assertions), and updated prose path references in AGENTS.md, docs/web-interface-decisions.md, src/gmat_verify.py, src/workflow_visualization.py, scripts/rendezvous_visualization_stage.py. AC3 evidence: one real CW case (prior worker's genuine nested-pi-CLI run, restored from /tmp and verified honest: real formalize_rendezvous_problem/select_rendezvous_model/run_gmat_verification/subagent tool calls, real GMAT console execution, VERIFIED, NO CORPUS ENTRY reviewer verdict) plus one real bounded-two-body case (run directly by this worker via the exact underlying bridge scripts/run_rendezvous_workflow the registered tools wrap, per supervisor direction, since this worker has no direct pi-tool/subagent access: model selection -> bounded two-body fallback, real GMAT console verification, final state and GMAT error identical to evaluations/benchmark/case_c_two_body.json's reference, VERIFIED, gmat-example-reviewer step honestly reported skipped/unavailable). Full suite: 272 passed, 2 pre-existing failures (test_cw_gmat_slice.py flaky screenshot-size test; test_rendezvous_visualization_stage_cli.py's GUI-limitation string assertion, which already fails against the unmodified prompt file before this change) confirmed via git-stash comparison, neither introduced by this task.
<!-- SECTION:FINAL_SUMMARY:END -->
