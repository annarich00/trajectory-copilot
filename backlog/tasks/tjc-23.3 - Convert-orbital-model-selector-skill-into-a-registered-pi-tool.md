---
id: TJC-23.3
title: Convert orbital-model-selector skill into a registered pi tool
status: Done
assignee:
  - '@worker'
created_date: '2026-11-11 14:44'
updated_date: '2026-11-11 17:43'
labels: []
dependencies: []
parent_task_id: TJC-23
priority: high
type: feature
ordinal: 88000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn .pi/skills/orbital-model-selector/SKILL.md's six-item assessment and CW/bounded-two-body/UNSUPPORTED/NEEDS-MORE-INFO selection logic into a registered pi tool callable on the formalizer tool's output.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A new pi tool implements the six-item assessment and the four-way selection result
- [x] #2 The tool consumes the formalizer tool's structured output directly
- [x] #3 The old SKILL.md is removed once the tool is wired into the pipeline
- [x] #4 Tests cover at least one CW-selected and one bounded-two-body-selected case
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.3: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Write failing test tests/test_model_selector_tool_bridge.py (red) exercising scripts/model_selector_tool_bridge.py (not yet existing) covering CW-selected, bounded-two-body-selected, NEEDS MORE INFORMATION, and UNSUPPORTED cases adapted from tests/test_model_selector.py. 2. Implement scripts/model_selector_tool_bridge.py as a thin JSON<->dataclass adapter around src.model_selector.ModelSelectionCase/select_model, mirroring scripts/cw_rendezvous_tool_bridge.py's structure (BridgeInputError, validate_case/run_bridge, --case-json/stdin CLI). 3. Run the new test to green. 4. Write .pi/extensions/orbital-model-selector-tool/index.ts registering select_rendezvous_model with a TypeBox schema matching ModelSelectionCase fields, shelling out via pi.exec to the bridge script exactly like cw-rendezvous-tool/gmat-verification-tool. Document in the file header how/whether the calling LLM maps formalize_rendezvous_problem's provenance-labeled output into the six assessments (this tool does not parse Markdown or infer assessments itself). 5. Remove .pi/skills/orbital-model-selector/SKILL.md and wire select_rendezvous_model into .pi/prompts/rendezvous.md step 2 mirroring step 1's phrasing pattern from TJC-23.2. 6. Fix dangling references: tests/test_skill_authority_boundaries.py (decide whether to drop the model-selector prose test now structurally enforced, mirroring TJC-23.2's formalizer precedent, with reasoning documented in the module docstring), tools/sync_site_data.py MAPPINGS + site/data/skills/model-selector.SKILL.md mirror, docs/baseline-checksums.md (check only, likely no entry since model-selector already isn't listed... verify), tools/compare_upstream.py APPROVED_TASK_OWNED_DIFFERENCES (actually that lists '.pi/skills/orbital-model-selector/SKILL.md' entries that must be re-checked after removal), AGENTS.md's routing rule only if it blocks tests (do not do a broad rewrite; TJC-23.7 owns that). Fix tests/test_rendezvous_visualization_stage_cli.py's literal-string 'kept' assertion if it references now-changed step 2 text. 7. Run full validation suite and tools/sync_site_data.py --check and tools/compare_upstream.py --check, compare against unmodified master baseline if needed. 8. Finalize backlog task with implementation notes (red/green evidence) and final summary, mark Done. 9. Single atomic commit 'TJC-23.3: ...' containing only this task's files.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Red/green TDD evidence (pre-existing, from the prior session that left this task code-complete): tests/test_model_selector_tool_bridge.py was written first against scripts/model_selector_tool_bridge.py (not yet existing) -> red (ModuleNotFoundError), then scripts/model_selector_tool_bridge.py was implemented as a thin JSON<->dataclass bridge around src.model_selector.ModelSelectionCase/select_model -> green: .venv/bin/python -m pytest tests/test_model_selector_tool_bridge.py -q -> 13 passed. This session completed the remaining work: wrote .pi/extensions/orbital-model-selector-tool/index.ts registering select_rendezvous_model (TypeBox schema matching ModelSelectionCase's fields, pi.exec to the bridge script, structured {error:...} surfaced as isError:true, promptGuidelines documenting that the calling LLM must supply the six assessments itself -- mirrors cw-rendezvous-tool/orbital-problem-formalizer-tool's pattern exactly; no .test.ts needed, matching cw-rendezvous-tool/gmat-verification-tool's established no-test-file convention for this pi.exec-wrapper shape, confirmed via node --experimental-strip-types --check -> exit 0). Removed .pi/skills/orbital-model-selector/SKILL.md and its site/data/skills/model-selector.SKILL.md mirror; wired select_rendezvous_model into .pi/prompts/rendezvous.md step 2 mirroring TJC-23.2's step-1 rewording pattern; left orbital-two-body-rendezvous (TJC-23.5, already merged) and AGENTS.md (TJC-23.7's scope) untouched. Fixed dangling references: tests/test_skill_authority_boundaries.py (dropped MODEL_SELECTOR from ALL_SKILLS and its skill-prose test, documented in the module docstring mirroring the TJC-23.2/23.4 precedent -- the never-invent-a-model/always-name-the-handoff invariant is now structurally enforced by select_model's deterministic contract, exercised by tests/test_model_selector.py and tests/test_model_selector_tool_bridge.py); tools/sync_site_data.py (dropped the model-selector MAPPINGS entry); docs/baseline-checksums.md (dropped the orbital-model-selector/SKILL.md checksum line, mirroring TJC-23.4's treatment of orbital-targeting-planner); src/model_selector.py and src/cw.py (updated SKILL.md-path-specific docstring/prose references to name the retired skill + its replacement tool, synced to their site/data mirrors) -- src/workflow.py has no SKILL.md-path-specific reference to this skill, left untouched. tools/compare_upstream.py's APPROVED_TASK_OWNED_DIFFERENCES already listed .pi/skills/orbital-model-selector/{SKILL.md,README.md} and site/data/skills/model-selector.SKILL.md from TJC-8/TJC-1.24; confirmed via tools/compare_upstream.py --check (exit 0, content-different unaccounted: none) that no edit to this file was needed, consistent with TJC-23.1/23.2/23.4 (none of which touched compare_upstream.py either) -- the set accounts for a path regardless of whether it later becomes upstream-only (deleted) or content-different. tests/test_rendezvous_visualization_stage_cli.py's literal-string assertions do not reference the old step-2 wording, so no fix was needed there; confirmed green. Validation: .venv/bin/python -m pytest tests/test_model_selector_tool_bridge.py tests/test_model_selector.py tests/test_skill_authority_boundaries.py -q -> 27 passed. Full suite: .venv/bin/python -m pytest -q -> 263 passed, 2 failed (tests/test_cw_gmat_slice.py::test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window and tests/test_rendezvous_visualization_stage_cli.py::test_rendezvous_prompt_reports_artifacts_in_pipeline_order_and_keeps_existing_constraints), both confirmed identical/pre-existing on unmodified master at /home/anna_ford/projects/class_example_traj_copilot (same assertion failures, same missing string/flaky GUI timing, not caused by this task). tools/sync_site_data.py --check -> 9 pre-existing drift lines (src/gmat_verify.py, src/verification_report.py, src/workflow.py, scripts/run_cw_gmat_slice.py, tests/test_cw_gmat_slice.py, tests/test_workflow.py, 3 baseline_comparison workflow_result.json files), confirmed identical to master's own --check output; synced the two mirrors this task's source changes affected (site/data/src/cw.py, site/data/src/model_selector.py, site/data/tests/test_skill_authority_boundaries.py) so no new drift was introduced. tools/compare_upstream.py --check -> exit 0, content-different unaccounted: none.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the select_rendezvous_model pi tool (.pi/extensions/orbital-model-selector-tool/) wrapping src/model_selector.py's deterministic six-item assumption-combination logic (the same combination the retired .pi/skills/orbital-model-selector/SKILL.md documented) via a thin Python bridge (scripts/model_selector_tool_bridge.py), mirroring solve_cw_rendezvous/formalize_rendezvous_problem's pi.exec pattern exactly (AC1/AC2). Covered by 13 tests in tests/test_model_selector_tool_bridge.py (red-then-green per docs/testing-policy.md), including a CW-selected case and a bounded-two-body-selected case (AC4). Removed .pi/skills/orbital-model-selector/SKILL.md once wired into .pi/prompts/rendezvous.md step 2 (AC3), and fixed the dangling references this uncovered: tests/test_skill_authority_boundaries.py (dropped the model-selector skill-prose test, now structurally enforced by select_model's deterministic contract instead), tools/sync_site_data.py and its site/data/skills/model-selector.SKILL.md mirror, docs/baseline-checksums.md, and src/model_selector.py/src/cw.py's SKILL.md-path-specific docstring references. Full pytest suite: 263 passed, 2 pre-existing unrelated failures (confirmed identical on unmodified master before this task: a flaky GMAT GUI screenshot size comparison, and the pre-existing missing-string assertion in test_rendezvous_visualization_stage_cli.py). tools/sync_site_data.py --check shows only the same pre-existing drift present on unmodified master (no new drift from this task's changes). tools/compare_upstream.py --check shows no unaccounted drift.
<!-- SECTION:FINAL_SUMMARY:END -->
