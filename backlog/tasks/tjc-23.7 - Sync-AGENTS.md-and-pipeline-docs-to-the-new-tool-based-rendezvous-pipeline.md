---
id: TJC-23.7
title: Sync AGENTS.md and pipeline docs to the new tool-based rendezvous pipeline
status: Done
assignee:
  - '@worker'
created_date: '2026-11-11 14:45'
updated_date: '2026-11-12 12:30'
labels: []
dependencies:
  - TJC-23.1
  - TJC-23.2
  - TJC-23.3
  - TJC-23.4
  - TJC-23.5
parent_task_id: TJC-23
priority: medium
type: docs
ordinal: 92000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once the formalizer, model-selector, CW, two-body, and orchestration steps are all registered pi tools instead of skills/prompts, AGENTS.md's standing rendezvous-routing rule and any other active pipeline documentation that names the old skills/prompt must be updated to name the new tools, and the full test suite must still pass.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 AGENTS.md's rendezvous routing rule names the new tools (not the retired skills/prompt) in pipeline order
- [x] #2 No active pipeline doc (outside historical docs/evaluation artifacts) still instructs applying a retired skill or invoking the retired /rendezvous prompt
- [x] #3 The existing test suite (including src/workflow.py and run_gmat_verification coverage) passes unchanged
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.7: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Research pass (done): re-grep retired skill/prompt names across *.md/*.py/*.ts, confirmed scope is exactly AGENTS.md's routing rule prose, docs/web-demo-cases.md's stale prompt-file reference, and docs/web-interface-decisions.md's 'Fixed pipeline' numbered list; confirmed docs/baseline-checksums.md and tools/compare_upstream.py's APPROVED_* sets are deliberately preserved historical provenance (per TJC-23.2/23.3/23.5 notes) and tools/sync_site_data.py has no dangling MAPPINGS entry -- none of these three need edits.
2. Edit AGENTS.md's 'Rendezvous request routing (standing rule)' section: replace the retired-skill-named pipeline chain 'orbital-problem-formalizer -> orbital-model-selector -> src/workflow.py::run_rendezvous_workflow -> GMAT verification' with the new tool names in pipeline order (formalize_rendezvous_problem -> select_rendezvous_model -> solve_cw_rendezvous/propagate_two_body_coast -> run_gmat_verification), reword the two '/rendezvous prompt template'/'/rendezvous itself was not typed' sentences to refer to the new rendezvous-shaped-request trigger via the orchestrator skill instead of the retired prompt, and update the stop-condition paragraph's '`orbital-problem-formalizer` result' phrase to name formalize_rendezvous_problem. Leave the two already-correct .pi/skills/rendezvous-pipeline-orchestrator/SKILL.md path references untouched.
3. Edit docs/web-demo-cases.md line ~37 to name .pi/skills/rendezvous-pipeline-orchestrator/SKILL.md's step-1 exception instead of the deleted .pi/prompts/rendezvous.md.
4. Edit docs/web-interface-decisions.md's 'Fixed pipeline' numbered list items 1-2 to name formalize_rendezvous_problem and select_rendezvous_model instead of the retired orbital-problem-formalizer/orbital-model-selector skill names, keeping the rest of the list (items 3-7) and the surrounding SKILL.md references unchanged and consistent.
5. Run .venv/bin/python -m pytest -q (full suite) and confirm it matches the known baseline (272 passed, 2 pre-existing failures) with no new regressions.
6. Run .venv/bin/python tools/compare_upstream.py --check and confirm 'content-different unaccounted: none'.
7. Finalize per task-finalization: check AC1/AC2/AC3 with evidence, check DoD 1 after the commit, append notes, final summary, mark Done.
8. Make exactly one atomic commit 'TJC-23.7: <summary>' with implementation + finalized Backlog metadata via amend, per docs/task-commit-policy.md.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Resumption worker (after a connectivity-pause worktree loss) independently re-verified the prior worker's research-pass claims before trusting them: (a) confirmed docs/baseline-checksums.md's one retired-name line and tools/compare_upstream.py's APPROVED_TASK_OWNED_DIFFERENCES/APPROVED_LOCAL_SITE_ALIGNMENT entries are checksum-provenance records of historical paths, not instructional text telling a reader to apply a retired skill -- correctly out of this task's 'active pipeline docs' scope; (b) confirmed every one of tools/sync_site_data.py's 57 MAPPINGS source paths exists on disk (no dangling entry); (c) ran a fresh grep -rln for orbital-problem-formalizer|orbital-model-selector|orbital-targeting-planner|orbital-two-body-rendezvous across *.md/*.py/*.ts (excluding .git, node_modules, backlog/) and manually read every hit: all are either (i) the now-correct .pi/extensions/*-tool/*.ts and .pi/skills/rendezvous-pipeline-orchestrator/SKILL.md source files that document their own retired-skill provenance by design, (ii) src/*.py and tests/*.py module/docstring provenance notes pointing at the retired skills they replace (correct historical attribution, not routing instructions), (iii) scripts/*_tool_bridge.py docstrings citing the retired skill they port logic from, (iv) evaluations/benchmark/README.md and artifacts/manual_runs/**/*.md, which are frozen historical run records/fixture docs (not active pipeline instructions), or (v) docs/baseline-checksums.md and tools/compare_upstream.py (already covered above). Nothing newly in-scope was found; no additional edits were needed beyond the three doc files + AGENTS.md already restored from the captured patch. Built a fresh .venv (uv venv + uv pip install -r requirements-dev.txt; the prior venv was lost with the cleaned-up worktree) and ran the full suite: 'python -m pytest -q' -> 1 failed, 273 passed (tests/test_rendezvous_visualization_stage_cli.py::test_rendezvous_prompt_reports_artifacts_in_pipeline_order_and_keeps_existing_constraints failed on the same pre-existing stale GUI-limitation string assertion recorded as already-failing before TJC-23.6; the other known-flaky Xvfb screenshot test passed this run -- both are the documented pre-existing baseline, no new regressions from this task's prose-only doc edits). Ran 'python tools/compare_upstream.py --check' -> exit 0, 'content-different unaccounted: none'. One unrelated file (evidence/poliastro/contract-test-evidence.json, a host_python value rewritten as a side effect of running tests/test_poliastro_verify.py's evidence-writing test under a different local Python build) was reverted with git checkout before committing, since it is out of this task's scope.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated AGENTS.md's 'Rendezvous request routing (standing rule)' section, docs/web-demo-cases.md's Demo C step-1-exception reference, and docs/web-interface-decisions.md's 'Fixed pipeline' list items 1-2 to name the new registered pi tools (formalize_rendezvous_problem, select_rendezvous_model, solve_cw_rendezvous/propagate_two_body_coast, run_gmat_verification) and the rendezvous-pipeline-orchestrator skill, instead of the retired orbital-problem-formalizer/orbital-model-selector skills and the deleted /rendezvous prompt. Verified with a fresh repo-wide grep for all four retired skill names (confirming no other active pipeline doc still instructs applying them), the full pytest suite (1 failed, 273 passed -- matching the documented pre-existing baseline exactly, no regressions), and tools/compare_upstream.py --check (exit 0, 'content-different unaccounted: none').
<!-- SECTION:FINAL_SUMMARY:END -->
