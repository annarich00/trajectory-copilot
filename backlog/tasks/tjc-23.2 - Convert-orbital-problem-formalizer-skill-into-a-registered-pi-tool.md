---
id: TJC-23.2
title: Convert orbital-problem-formalizer skill into a registered pi tool
status: Done
assignee:
  - '@delegate'
created_date: '2026-11-11 14:44'
updated_date: '2026-11-11 16:06'
labels: []
dependencies: []
parent_task_id: TJC-23
priority: high
type: feature
ordinal: 87000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn .pi/skills/orbital-problem-formalizer/SKILL.md's required Markdown schema and provenance rules into a registered pi tool (e.g. an extension under .pi/extensions/) that an agent calls explicitly instead of applying free-form skill instructions, mirroring the existing run_gmat_verification tool's auditable-call pattern.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A new pi tool implements the formalizer's required output schema (Scope through Readiness) and provenance-label rules
- [x] #2 The tool's input/output contract is structured (not free text) wherever the skill specifies structured fields
- [x] #3 The old SKILL.md is removed once the tool is wired into the pipeline
- [x] #4 Unit/integration tests cover at least one READY TO SOLVE and one NEEDS CLARIFICATION case
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.2: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review the already-written .pi/extensions/orbital-problem-formalizer-tool/{index.ts,formalizer.ts,formalizer.test.ts} (code-complete from a prior session; 7 node tests passing). 2. Remove .pi/skills/orbital-problem-formalizer/SKILL.md (AC3). 3. Fix dangling references in active pipeline files: .pi/prompts/rendezvous.md step 1 ('Apply the orbital-problem-formalizer skill'), AGENTS.md's routing rule mention (scoped minimally; full AGENTS.md sync is TJC-23.7's job), tests/test_skill_authority_boundaries.py (FORMALIZER entry removed from ALL_SKILLS since the skill file no longer exists), tools/sync_site_data.py MAPPINGS + site/data/skills/formalizer.SKILL.md mirror. 4. Check src/workflow.py's docstring mention of orbital-problem-formalizer and tests/test_formalizer_schema.py -- confirm whether they describe the skill file or the general formalization step; update only if they assert the retired skill file's existence. 5. Re-run node --experimental-strip-types --test formalizer.test.ts and the full pytest suite; confirm only the pre-existing unrelated failure remains. 6. Finalize Backlog and commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Took over from a prior session's in-progress worktree where .pi/extensions/orbital-problem-formalizer-tool/{index.ts,formalizer.ts,formalizer.test.ts} were already written and passing (7 node --test cases covering READY TO SOLVE, NEEDS CLARIFICATION, illegal-label rejection, readiness-consistency rejection, and OUT OF SCOPE short-circuit -- AC1/AC2/AC4). Completed the remaining work: removed .pi/skills/orbital-problem-formalizer/SKILL.md (AC3); updated .pi/prompts/rendezvous.md step 1 to reason over the request and call formalize_rendezvous_problem instead of 'applying the orbital-problem-formalizer skill'; fixed src/workflow.py's two docstring mentions and src/cw.py's UNSUPPORTED recommended_next_step prose to name the new tool; rewrote tests/test_formalizer_schema.py to check formalizer.ts's schema/labels (was reading the now-deleted skill file) while keeping its fixture-based NEEDS CLARIFICATION/complete/contradictory/unit-inconsistent coverage unchanged; dropped the retired-skill-specific FORMALIZER entry and test_formalizer_never_solves_or_invents_a_numerical_result from tests/test_skill_authority_boundaries.py (that invariant is now structurally enforced by the tool's deterministic validator, exercised directly by formalizer.test.ts, not re-asserted as skill prose); fixed two tests whose literal-string assertions broke from the prompt step-1 rewording (test_rendezvous_visualization_stage_cli.py's 'kept' list, confirmed red via pytest before the fix). Removed tools/sync_site_data.py's dangling MAPPINGS entry and the site/data/skills/formalizer.SKILL.md mirror; synced the mirrors this task's source changes affected.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the formalize_rendezvous_problem pi tool (.pi/extensions/orbital-problem-formalizer-tool/) implementing the retired orbital-problem-formalizer skill's Scope-through-Readiness Markdown schema and eight-label provenance vocabulary as a deterministic TypeBox-validated tool call (AC1/AC2), verified by 7 node --test cases covering one READY TO SOLVE case, one NEEDS CLARIFICATION case, illegal-provenance rejection, readiness-consistency rejection, and OUT OF SCOPE short-circuit (AC4). Removed .pi/skills/orbital-problem-formalizer/SKILL.md once wired into .pi/prompts/rendezvous.md step 1 (AC3), and fixed the dangling references this uncovered: src/workflow.py docstrings, src/cw.py's UNSUPPORTED guidance text, tests/test_formalizer_schema.py (now checks formalizer.ts instead of the deleted skill file), tests/test_skill_authority_boundaries.py (dropped the formalizer-specific prose assertion, now structurally enforced by the tool instead), tests/test_rendezvous_visualization_stage_cli.py (updated a literal-string assertion broken by the prompt rewording), tools/sync_site_data.py and its site/data/skills/formalizer.SKILL.md mirror. Full pytest suite: 252 passed, 1 pre-existing unrelated failure (confirmed identical on unmodified master before this task). tools/sync_site_data.py --check and tools/compare_upstream.py --check show no new drift beyond master's pre-existing baseline.
<!-- SECTION:FINAL_SUMMARY:END -->
