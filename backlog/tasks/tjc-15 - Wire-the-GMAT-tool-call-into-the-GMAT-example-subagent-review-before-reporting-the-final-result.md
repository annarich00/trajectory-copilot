---
id: TJC-15
title: >-
  Wire the GMAT tool call into the GMAT-example subagent review before reporting
  the final result
status: Done
assignee:
  - '@worker'
created_date: '2026-10-28 13:34'
updated_date: '2026-11-05 22:58'
labels: []
dependencies:
  - TJC-12
  - TJC-14
priority: low
type: feature
ordinal: 59000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fourth of the four classmate-brainstormed workflow additions, and the piece that connects the other three. Once the GMAT execution tool (separate task) and the GMAT-example review subagent (separate task) both exist independently, this task sequences them: after the main workflow agent calls the GMAT execution tool and gets a numerical/screenshot verification result, it hands the generated GMAT script and mission context to the GMAT-example subagent for a formatting/convention review, then incorporates that subagent's verdict into what it reports back to the user -- before declaring the result 'VERIFIED.' This is an additive step in .pi/prompts/rendezvous.md (a new step between the existing steps 3 and 4), not a replacement for the numerical verification contract: a 'divergent formatting' verdict from the subagent must never override or be confused with a PASS/FAIL numerical result from src/gmat_verify.py.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 .pi/prompts/rendezvous.md gains an explicit step (sequenced after the GMAT tool call, before the final outcome report) that hands the generated script and mission type to the GMAT-example subagent and requires reporting its verdict alongside, not instead of, the numerical VERIFIED/FAIL outcome
- [x] #2 The subagent's formatting verdict is clearly labeled as advisory/stylistic in the final report and cannot change a FAIL to VERIFIED or a VERIFIED to FAIL on its own
- [x] #3 If the GMAT-example subagent is unavailable or errors, the workflow still completes and reports the numerical verification result, with the formatting review explicitly noted as skipped/unavailable rather than blocking the whole result
- [x] #4 A worked end-to-end example (one real or recorded run) shows the full chain: natural-language request -> formalizer -> model selector -> GMAT execution tool call -> GMAT-example subagent review -> final combined report
- [x] #5 No change is made to the numerical PASS/WARNING/FAIL/INCOMPLETE logic already defined in src/gmat_verify.py or src/verification_report.py
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-15:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Red: add tests/test_rendezvous_prompt_reviewer_step.py (static guard: new step between GMAT tool call and final report, advisory-only wording, skipped/unavailable fallback, no-override, mission-type/NO CORPUS ENTRY handling, coast exception) and run it before editing the prompt.
2. Edit .pi/prompts/rendezvous.md: insert new step 4 (GMAT-example review via subagent tool), renumber final report to 5 and GUI step to 6, update step-number cross references (step-4 summary, step 3-4).
3. Green: rerun new test plus existing prompt-guard tests.
4. Produce a worked end-to-end example doc (docs/gmat-example-reviewer-workflow-example.md) from a real GMAT run + reviewer run, labelled precisely for provenance; update docs/gmat-example-reviewer-example-run.md note that it is now wired.
5. Confirm src/gmat_verify.py and src/verification_report.py unchanged (git diff --name-only); finalize Backlog; single commit TJC-15.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Red: pytest tests/test_rendezvous_prompt_reviewer_step.py -> 7 failed (before editing .pi/prompts/rendezvous.md: e.g. ValueError/AssertionError 'step 4 not found'/'gmat-example-reviewer' absent; 'step-5 summary' not in PROMPT). The 8th test (forbids self-authored verdicts) was added after the first worked-example run showed the agent fabricating a review via shell echo; its red was shown by temporarily removing the sentence: 1 failed, 7 passed (AssertionError: 'Never write, echo' not in step 4). Green: same file -> 8 passed. Also tests/test_gmat_example_reviewer_agent.py + new test: 17 passed. Wider suite (venv from main checkout lacks plotly/hypothesis, so 9 files with pre-existing collection errors ignored: test_cw_state_histories_helpers, test_cw_targeting_singularities, test_physics_properties, test_rendezvous_visualization_stage_cli, test_visualization_*, test_workflow, test_workflow_visualization): 182 passed. The existing prompt guard in test_rendezvous_visualization_stage_cli.py cannot be collected here (plotly import), so its assertions were executed standalone against the edited prompt: OK; the step renumbering (step-4 summary -> step-5, 'step 3-4' reworded) does not touch strings it checks.

Design: new step 4 in .pi/prompts/rendezvous.md calls the subagent tool (agent gmat-example-reviewer, agentScope project) with script path + real mission type; for CW rendezvous passes the real mission type and reports NO CORPUS ENTRY as-is (no orbit_transfer substitution; corpus has no rendezvous entry per TJC-14); advisory/stylistic only, never changes FAIL<->VERIFIED; unavailable/error -> 'GMAT-example review skipped/unavailable' and workflow still completes; no script -> skipped; self-authored verdicts forbidden. Old steps 4/5 renumbered 5/6; cross refs updated. src/gmat_verify.py and src/verification_report.py untouched (git diff --name-only shows only prompt, docs, new test, this task file).

Worked example: docs/rendezvous-gmat-example-review-worked-example.md. Real headless 'pi -p /rendezvous ...' run: formalizer -> selector -> real run_gmat_verification (VERIFIED, PASS, pos err 7.94e-3 m) -> report. The headless session had no subagent tool (also not with -e pi-subagents), so step 4 honestly fell back to 'skipped/unavailable' (exercises AC3). The reviewer verdict (NO CORPUS ENTRY, 2 of 3 samples; 1 DIVERGENT sample documented) comes from separate real runs of the agent definition via 'pi -p --system-prompt' as in TJC-14, so the combined report is a labelled composite. An earlier run where the agent fabricated a review via echo was discarded and led to the no-self-authored-verdict rule. Not exercised: real subagent-tool invocation, two-body fallback path, coast exception, infeasible/no-script skip.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added step 4 to .pi/prompts/rendezvous.md (GMAT-example review via the subagent tool, advisory/stylistic only, non-blocking skipped/unavailable fallback, real mission type with NO CORPUS ENTRY accepted for CW rendezvous, no self-authored verdicts); renumbered final report/GUI steps to 5/6. Added tests/test_rendezvous_prompt_reviewer_step.py (8 tests, red-then-green recorded) and docs/rendezvous-gmat-example-review-worked-example.md (real /rendezvous run + separately-run reviewer, labelled composite, with not-exercised list). src/gmat_verify.py and src/verification_report.py unchanged. Verified: new+reviewer-agent tests 17 passed; 182 passed in the collectable suite.
<!-- SECTION:FINAL_SUMMARY:END -->
