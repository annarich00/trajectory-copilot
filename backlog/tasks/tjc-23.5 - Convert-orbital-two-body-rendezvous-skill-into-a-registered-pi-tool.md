---
id: TJC-23.5
title: Convert orbital-two-body-rendezvous skill into a registered pi tool
status: Done
assignee:
  - '@annarich00'
created_date: '2026-11-11 14:45'
updated_date: '2026-11-11 16:35'
labels: []
dependencies: []
parent_task_id: TJC-23
priority: high
type: feature
ordinal: 90000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn .pi/skills/orbital-two-body-rendezvous/SKILL.md's bounded inertial Cartesian coast fallback into a registered pi tool wrapping src/twobody.py (TwoBodyCase, propagate_cartesian_state/kepler_propagate_state).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A new pi tool wraps src/twobody.py's propagation with the same required-input validation the skill documents
- [x] #2 Non-finite inputs, non-positive mu/steps, and zero-radius singularities are rejected, not improvised
- [x] #3 The old SKILL.md is removed once the tool is wired into the pipeline
- [x] #4 Tests cover a normal coast propagation and at least one rejected invalid-input case
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.5: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create scripts/two_body_tool_bridge.py: thin CLI bridge reading structured JSON (state0_m_mps[6], mu_m3_s2, duration_s, steps, optional epoch) via --case-json or stdin, calling src/twobody.py::propagate_cartesian_state, returning {final_state_m_mps, frame, central_body, dynamics, integrator, epoch} JSON on success, or {error: ...} with nonzero exit on ValueError (non-finite inputs, non-positive mu/steps, zero-radius singularity) -- mirroring scripts/gmat_tool_bridge.py's pattern.
2. Create .pi/extensions/two-body-rendezvous-tool/index.ts registering propagate_two_body_coast tool with typebox schema requiring initial_state_m_mps (6 numbers), mu_m3_s2 (number), duration_s (number), steps (integer), optional epoch (string); shells out via pi.exec to the bridge script mirroring gmat-verification-tool/index.ts's resolvePythonExecutable/pi.exec pattern; relays bridge JSON verbatim, isError on bridge error.
3. Write tests/test_two_body_tool_bridge.py covering: normal coast propagation matches src/twobody.py::propagate_cartesian_state directly, and at least one rejected invalid-input case (e.g. zero mu or zero-radius state) returns a structured error not a crash. Follow TDD red/green evidence per docs/testing-policy.md.
4. Run .venv/bin/python -m pytest tests/test_two_body_tool_bridge.py (scoped only) and record red/green evidence in task notes.
5. Remove .pi/skills/orbital-two-body-rendezvous/SKILL.md (and its now-empty directory) now that the tool is wired in.
6. Finalize: check ACs/DoD with evidence, append notes, mark Done, then make exactly one atomic git commit 'TJC-23.5: ...' containing only these changes plus finalized Backlog metadata.

7. Wire .pi/prompts/rendezvous.md step 1's single-spacecraft-coast exception to name the registered propagate_two_body_coast pi tool instead of the retired skill (step 3's bounded-two-body-fallback branch already only named src/workflow.py::run_rendezvous_workflow, not the skill by name, so it needed no edit). Fix dangling references in tests/test_skill_authority_boundaries.py (drop the TWO_BODY entry and its two skill-prose tests, document in the module docstring that their invariants are now structurally enforced by scripts/two_body_tool_bridge.py's ValueError propagation -- covered by tests/test_two_body_tool_bridge.py's existing rejection tests -- and by propagate_two_body_coast's own description/promptGuidelines strings) and tools/sync_site_data.py's MAPPINGS entry plus its site/data/skills/two-body-rendezvous.SKILL.md mirror file. Checked and left unchanged: docs/baseline-checksums.md (no two-body entry), src/model_selector.py and src/workflow.py (no skill-name references, only 'two-body'/'two_body' as a model-selection label), docs/architecture-graph.html and evaluations/benchmark/case_c_two_body.json (historical/presentation docs, out of scope per task).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Set up this worktree's .venv (python3 -m venv .venv && .venv/bin/python -m pip install -r requirements-dev.txt); confirmed the prior session's tests/test_two_body_tool_bridge.py is 11/11 green (AC1/AC2/AC4 evidence) before touching anything else.

AC3 completed: removed .pi/skills/orbital-two-body-rendezvous/SKILL.md via git rm (its parent directory, now empty, was removed automatically by git). Verified with fresh evidence: 'test -f .pi/skills/orbital-two-body-rendezvous/SKILL.md' -> not found, 'test -d .pi/skills/orbital-two-body-rendezvous' -> not found.

Wired .pi/prompts/rendezvous.md step 1's single-spacecraft-coast exception to name the registered propagate_two_body_coast pi tool (.pi/extensions/two-body-rendezvous-tool/) instead of the retired orbital-two-body-rendezvous skill, following TJC-23.2's rewording pattern for the formalizer tool. grep confirms zero remaining 'orbital-two-body-rendezvous' references in .pi/prompts/rendezvous.md. Step 3's bounded-two-body-fallback branch never named the skill directly (only src/workflow.py::run_rendezvous_workflow by name), so it needed no wording change.

Dangling-reference sweep (active pipeline only, per task scope):
- tests/test_skill_authority_boundaries.py: removed the TWO_BODY skill entry, its test_every_referenced_skill_file_exists coverage, test_two_body_skill_requires_the_deterministic_implementation_and_refuses_to_improvise, and the two-body case of test_every_solver_skill_hands_off_to_gmat_verification_before_pass. Reasoning (same pattern TJC-23.1/23.2 used for their own retired skills in this file): the never-improvise-a-rejected-input half of the old skill-prose invariant is now structurally enforced by scripts/two_body_tool_bridge.py's run_bridge propagating propagate_cartesian_state's own ValueError unchanged, already exercised by tests/test_two_body_tool_bridge.py::test_run_bridge_rejects_invalid_inputs_without_improvising_a_result (parametrized over non-finite/non-positive-mu/non-positive-steps/zero-radius cases) -- no new test needed, just documented the mapping in the module docstring. The never-claim-unsupported-capabilities and GMAT-verification-handoff halves are now carried by propagate_two_body_coast's own description/promptGuidelines strings in the TypeScript tool registration rather than a Markdown skill file a human/LLM reads voluntarily, so they are no longer part of this Python module's prose-only skill-layer coverage either. Removed the now-unused 'import pytest' (its only use was the retired @pytest.mark.parametrize). Ran tools/sync_site_data.py to update the site/data/tests/test_skill_authority_boundaries.py mirror to match (then reverted the unrelated pre-existing-drift files it also touched, to keep this commit scoped to only this task's files).
- tools/sync_site_data.py: removed the '.pi/skills/orbital-two-body-rendezvous/SKILL.md': 'site/data/skills/two-body-rendezvous.SKILL.md' MAPPINGS entry and git-rm'd the now-orphaned site/data/skills/two-body-rendezvous.SKILL.md mirror file.
- Checked and left unchanged (no dangling reference found, or out of scope): docs/baseline-checksums.md (no two-body-skill checksum entry present), src/model_selector.py and src/workflow.py (grep shows only the 'bounded two-body fallback' selection-label text and 'two_body'-named functions/variables, never a reference to the retired skill file/name), docs/architecture-graph.html and evaluations/benchmark/case_c_two_body.json's _comment field (historical/presentation docs and a committed benchmark fixture's prose, both explicitly out of scope per the task's ACTIVE-pipeline-only instruction -- the benchmark JSON's structured fields, which .pi/prompts/rendezvous.md step 1 cross-references, are unaffected). AGENTS.md intentionally left untouched (TJC-23.7's separate job).

Validation:
- .venv/bin/python -m pytest tests/test_two_body_tool_bridge.py tests/test_twobody.py tests/test_skill_authority_boundaries.py -q -> 23 passed.
- .venv/bin/python -m pytest -q (full suite) -> 261 passed, 1 failed: tests/test_rendezvous_visualization_stage_cli.py::test_rendezvous_prompt_reports_artifacts_in_pipeline_order_and_keeps_existing_constraints. Confirmed this exact failure (same AssertionError, same missing 'exactly this: state plainly that an interactive GMAT window cannot be' substring) is pre-existing on unmodified master at /home/anna_ford/projects/class_example_traj_copilot, unrelated to this task's prompt edit (none of that test's other 'kept' literal-string assertions touch 'orbital-two-body-rendezvous' text, and all of those other assertions still pass here).
- .venv/bin/python tools/sync_site_data.py --check -> same 10-file DRIFT list as unmodified master (src/cw.py, src/gmat_verify.py, src/verification_report.py, src/workflow.py, scripts/run_cw_gmat_slice.py, tests/test_cw_gmat_slice.py, tests/test_workflow.py, and 3 baseline_comparison workflow_result.json mirrors) -- pre-existing, unrelated drift, confirmed identical on master.
- .venv/bin/python tools/compare_upstream.py --check -> 'content-different unaccounted: none' on both this worktree and unmodified master; identical upstream-only/content-different-accepted lists on both; no new drift introduced by this task.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed the remaining TJC-23.5 work on top of a prior session's code-complete, TDD-tested implementation (scripts/two_body_tool_bridge.py, .pi/extensions/two-body-rendezvous-tool/index.ts, tests/test_two_body_tool_bridge.py, 11/11 green). Removed .pi/skills/orbital-two-body-rendezvous/SKILL.md (AC3, verified by fresh existence checks) now that propagate_two_body_coast is registered and wired into .pi/prompts/rendezvous.md step 1 in place of the retired skill name. Fixed the resulting dangling references across the active pipeline: tests/test_skill_authority_boundaries.py (retired the TWO_BODY skill-prose tests, documenting that their invariants are now structurally enforced by the bridge script's ValueError propagation and the tool's own description/promptGuidelines text) and tools/sync_site_data.py plus its orphaned site mirror file. docs/baseline-checksums.md, src/model_selector.py, and src/workflow.py needed no change (no skill-name reference found); docs/architecture-graph.html and the benchmark fixture's prose were left alone as out-of-scope historical/presentation material. Verified with: pytest tests/test_two_body_tool_bridge.py tests/test_twobody.py tests/test_skill_authority_boundaries.py -q (23 passed); full pytest -q (261 passed, 1 pre-existing unrelated failure confirmed identical on master); tools/sync_site_data.py --check and tools/compare_upstream.py --check (both show only pre-existing drift identical to master, no new unaccounted differences).
<!-- SECTION:FINAL_SUMMARY:END -->
