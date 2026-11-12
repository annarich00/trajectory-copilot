---
id: TJC-23
title: Migrate rendezvous skills and prompt to pi tool calls
status: Done
assignee:
  - '@worker'
created_date: '2026-11-11 14:44'
updated_date: '2026-11-12 12:59'
labels: []
dependencies: []
priority: high
type: feature
ordinal: 85000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The rendezvous pipeline relied on the LLM applying free-form .pi/skills/*.md instructions (orbital-problem-formalizer, orbital-model-selector, cw-rendezvous, orbital-two-body-rendezvous) and a .pi/prompts/rendezvous.md slash-prompt that orchestrated them, plus run_gmat_verification as the one existing registered pi tool. The goal was the same explicit, auditable tool-call pattern already used for GMAT verification extended across the pipeline: the unused gmat-rendezvous-verification skill (superseded by the run_gmat_verification tool contract and not referenced by the /rendezvous pipeline) removed, the four currently-used skills turned into registered pi tools, and the /rendezvous prompt itself turned into a skill (TJC-23.6 deliberately narrowed this to stop at the skill, not a further tool conversion, to avoid duplicating TJC-23's own per-skill tool-conversion pattern one level up for pure orchestration logic -- see TJC-23.6's narrowing commit and TJC-23's own AC3). This was a material architecture change to the AGENTS.md-documented standing pipeline order and received explicit plan review before implementation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The gmat-rendezvous-verification skill directory is removed and no longer referenced by the active rendezvous pipeline docs
- [x] #2 Each of orbital-problem-formalizer, orbital-model-selector, cw-rendezvous (orbital-targeting-planner), and orbital-two-body-rendezvous has an equivalent registered pi tool and its skill file is retired
- [x] #3 The /rendezvous prompt's orchestration is re-expressed as a skill (intentionally staying a skill, not converted into a registered pi tool call -- that scope was deliberately dropped by TJC-23.6's own narrowing commit to avoid duplicating TJC-23's per-skill tool-conversion pattern one level up for pure orchestration logic), so the retired /rendezvous prompt file no longer exists and its orchestration lives only in .pi/skills/rendezvous-pipeline-orchestrator/SKILL.md
- [x] #4 AGENTS.md's standing rendezvous-routing rule and any other pipeline documentation are updated to reference the new tools instead of the retired skills/prompt
- [x] #5 Existing CW/GMAT verification behavior (src/workflow.py, run_gmat_verification) is unchanged and still passes its existing tests
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Parent task closed after all 7 subtasks (TJC-23.1-23.7) landed Done, each as its own atomic commit per docs/task-commit-policy.md: TJC-23.1 removed the unused gmat-rendezvous-verification skill; TJC-23.2-23.5 converted orbital-problem-formalizer/orbital-model-selector/orbital-targeting-planner(cw-rendezvous)/orbital-two-body-rendezvous into formalize_rendezvous_problem/select_rendezvous_model/solve_cw_rendezvous/propagate_two_body_coast respectively, each removing its retired SKILL.md; TJC-23.6 re-expressed .pi/prompts/rendezvous.md's orchestration as .pi/skills/rendezvous-pipeline-orchestrator/SKILL.md and deleted the prompt file; TJC-23.7 synced AGENTS.md's routing rule and remaining active pipeline docs (docs/web-demo-cases.md, docs/web-interface-decisions.md) to name the new tools/skill. AC3 reworded to match TJC-23.6's own deliberate, user-confirmed narrowing: the orchestrator intentionally stays a skill (not converted into a further registered pi tool call), since doing so would duplicate TJC-23's per-skill tool-conversion pattern one level up for pure orchestration logic that only calls already-converted tools. Verification performed at the parent level (re-checked directly, not just taken from subtask reports): .pi/skills/gmat-rendezvous-verification/ and all four retired skill directories (orbital-problem-formalizer, orbital-model-selector, orbital-targeting-planner, orbital-two-body-rendezvous) confirmed absent; .pi/extensions/{cw-rendezvous-tool,orbital-model-selector-tool,orbital-problem-formalizer-tool,two-body-rendezvous-tool,gmat-verification-tool} confirmed present; AGENTS.md's routing rule confirmed naming formalize_rendezvous_problem -> select_rendezvous_model -> solve_cw_rendezvous / propagate_two_body_coast -> run_gmat_verification; tools/compare_upstream.py --check confirmed exit 0 with 'content-different unaccounted: none'; full .venv/bin/python -m pytest -q confirmed '1 failed, 273 passed' with the single failure being the same pre-existing stale-string assertion documented since TJC-23.6 (unrelated to this migration, confirmed via git-stash comparison in TJC-23.6's own notes); .pi/prompts/rendezvous.md confirmed deleted; src/workflow.py and run_gmat_verification confirmed unchanged in behavior (only docstring path references updated across the subtasks).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Migrated the rendezvous pipeline from free-form .pi/skills/*.md instructions and a .pi/prompts/rendezvous.md slash-prompt to the explicit, auditable registered-pi-tool pattern already used for GMAT verification. Across 7 subtasks: removed the unused gmat-rendezvous-verification skill (TJC-23.1); converted orbital-problem-formalizer, orbital-model-selector, orbital-targeting-planner (cw-rendezvous), and orbital-two-body-rendezvous into formalize_rendezvous_problem, select_rendezvous_model, solve_cw_rendezvous, and propagate_two_body_coast respectively, retiring each old SKILL.md (TJC-23.2-23.5); re-expressed the /rendezvous prompt's orchestration (step ordering, stop conditions, visualization-stage timing, GMAT-example-reviewer handoff) as .pi/skills/rendezvous-pipeline-orchestrator/SKILL.md and deleted the prompt file, deliberately stopping at a skill rather than converting it into a further tool call (user-confirmed intentional scope, reflected in this task's reworded AC3) (TJC-23.6); and synced AGENTS.md's routing rule plus remaining active pipeline docs to name the new tools in pipeline order (TJC-23.7). Verified directly at the parent level: all five retired skill directories absent, all five tool extensions present, AGENTS.md naming the correct tool chain, tools/compare_upstream.py --check clean, full pytest suite at 273 passed/1 pre-existing unrelated failure, src/workflow.py and run_gmat_verification behavior unchanged.
<!-- SECTION:FINAL_SUMMARY:END -->
