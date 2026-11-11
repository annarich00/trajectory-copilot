---
id: TJC-23.4
title: >-
  Convert cw-rendezvous (orbital-targeting-planner) skill into a registered pi
  tool
status: Done
assignee:
  - '@worker'
created_date: '2026-11-11 14:45'
updated_date: '2026-11-11 15:15'
labels: []
dependencies: []
parent_task_id: TJC-23
priority: high
type: feature
ordinal: 89000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn .pi/skills/orbital-targeting-planner/SKILL.md's deterministic CW two-impulse targeting handoff into a registered pi tool that wraps src/cw.py (mean_motion, two_burn_targeting) the same way run_gmat_verification wraps GMAT execution, instead of relying on the LLM to call src/cw.py itself.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A new pi tool wraps src/cw.py's two_burn_targeting/mean_motion with the same required-input validation the skill documents
- [x] #2 CWSingularTransferError is surfaced as a structured rejection, not approximated
- [x] #3 The old SKILL.md is removed once the tool is wired into the pipeline
- [x] #4 Tests cover a normal two-impulse solve and a singular-transfer rejection
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.4: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Write scripts/cw_rendezvous_tool_bridge.py: a thin CLI bridge (mirrors scripts/gmat_tool_bridge.py's pattern exactly) that reads one structured JSON case (reference_radius_m or mean_motion_rad_s, mu_m3_s2, lvlh_convention_confirmed, initial_relative_state (6), final_relative_state (6), transfer_time_s, model_selection_note) from --case-json/stdin, validates required fields, calls src.cw.mean_motion (if reference_radius_m given) and src.cw.two_burn_targeting, and prints a structured JSON result (dv0, dv1, final_state, status/feasible/singular/non_unique/reason, or a structured rejection for CWSingularTransferError/infeasible status) -- no new CW physics, same as the GMAT bridge's no-new-logic constraint.
2. Write .pi/extensions/cw-rendezvous-tool/index.ts registering solve_cw_rendezvous: TypeBox schema requiring reference_radius_m OR mean_motion_rad_s (oneOf-style: both optional but validated for at-least-one in execute()), mu_m3_s2, lvlh_convention_confirmed (boolean/string literal confirmation), initial_relative_state (6 numbers), final_relative_state (6 numbers, required per task), transfer_time_s (positive), model_selection_note (string, non-empty), shells out via pi.exec to the new bridge script exactly like run_gmat_verification does, relays stdout JSON verbatim as structuredContent, isError on infeasible/rejected outcome.
3. Write tests/test_cw_rendezvous_tool_bridge.py (pytest) covering: (a) a normal two-impulse case (quarter-orbit LEO, same worked example as test_cw.py::test_cw_rendezvous_benchmark) returns status unique/feasible with dv0/dv1/final_state; (b) a singular/unreachable transfer (e.g. GEO integer-period case with unreachable radial target, same as test_cw.py's singular-infeasible case) returns a structured rejection (feasible False, no fabricated dv/final_state), not an approximation; (c) missing required field raises a structured bridge input error. Run red-then-green per docs/testing-policy.md.
4. Run .venv/bin/python -m pytest tests/test_cw_rendezvous_tool_bridge.py -q (time-boxed), and tests/test_cw.py -q to confirm no regression to src/cw.py (untouched).
5. Remove .pi/skills/orbital-targeting-planner/SKILL.md once the tool is wired in, per AC3. Update docs/baseline-checksums.md (drop its checksum line), tools/compare_upstream.py (drop its entries from APPROVED_TASK_OWNED_DIFFERENCES since the file no longer exists locally -- confirm whether compare_upstream.py --check tolerates a missing-locally file or needs updating), tools/sync_site_data.py (drop its MAPPINGS entry and remove the stale site/data/skills/targeting-planner.SKILL.md mirror), and tests/test_skill_authority_boundaries.py (drop CW_TARGETING-related assertions since the skill file is gone) -- scoped strictly to removing now-dangling references to the deleted skill file, not widening into TJC-23.1/23.6/23.7's separate pipeline-doc-sync scope.
6. Verify: grep confirms no active (non-historical) code/doc/test references the deleted skill path other than Backlog's own task text; run the new test file and tests/test_cw.py again; run tools/compare_upstream.py --check and tools/sync_site_data.py --check if time permits (time-boxed, report partial evidence if slow).
7. Finalize Backlog (check ACs/DoD with evidence, notes, final summary, Done) and make exactly one atomic git commit 'TJC-23.4: ...' containing only this task's changes (new bridge script, new extension, new test file, SKILL.md removal, and the minimal reference-cleanup edits) plus finalized Backlog metadata.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created .venv (none existed in this worktree) per README's Reproducible setup, installed requirements-dev.txt. Implemented scripts/cw_rendezvous_tool_bridge.py (mirrors scripts/gmat_tool_bridge.py's bridge pattern): validates mu_m3_s2, lvlh_convention_confirmed (must be true), initial/final_relative_state (6-vectors), transfer_time_s, model_selection_note, and exactly one of reference_radius_m/mean_motion_rad_s; calls src.cw.mean_motion + two_burn_targeting unmodified; returns structured feasible result (dv0_mps/dv1_mps/final_state) or structured rejection (feasible:false, no fabricated dv/final_state) for CWSingularTransferError or an infeasible singular boundary. Implemented .pi/extensions/cw-rendezvous-tool/index.ts registering solve_cw_rendezvous, shelling out via pi.exec to the bridge script exactly like run_gmat_verification does. Added tests/test_cw_rendezvous_tool_bridge.py (11 tests): normal two-impulse LEO quarter-orbit solve (same worked case as test_cw.py::test_cw_rendezvous_benchmark), whole-period GEO unreachable-radial-target singular-infeasible rejection (same case family as test_cw.py/test_cw_targeting_singularities.py), input-validation errors, and end-to-end CLI invocations. Red: moved scripts/cw_rendezvous_tool_bridge.py aside and reran pytest tests/test_cw_rendezvous_tool_bridge.py -> ModuleNotFoundError: No module named 'scripts.cw_rendezvous_tool_bridge' (confirms the test exercises the intended module). Green: restored the file, reran -> 11 passed. Removed .pi/skills/orbital-targeting-planner/SKILL.md (now-empty dir also removed) and its dangling references: docs/baseline-checksums.md (dropped checksum line), tools/sync_site_data.py (dropped MAPPINGS entry), tests/test_skill_authority_boundaries.py + its site/data mirror (dropped CW_TARGETING skill-file assertions, kept formalizer/model-selector/two-body/gmat-verification coverage). tools/compare_upstream.py required no edit: the skill's path already sits in APPROVED_TASK_OWNED_DIFFERENCES, and a locally-deleted file surfaces there as 'upstream-only' (not 'unaccounted'), so --check still exits 0 after removal (confirmed). Validation: .venv/bin/python -m pytest tests/test_cw_rendezvous_tool_bridge.py tests/test_cw.py tests/test_skill_authority_boundaries.py tests/test_cw_targeting_singularities.py tests/test_model_selector.py -q -> 52 passed. Full suite: .venv/bin/python -m pytest -q -> 255 passed, 1 failed (test_rendezvous_visualization_stage_cli.py::test_rendezvous_prompt_reports_artifacts_in_pipeline_order_and_keeps_existing_constraints); confirmed via git stash that this exact failure pre-exists on the unmodified tree (unrelated stale .pi/prompts/rendezvous.md content, outside this task's scope). tools/compare_upstream.py --check -> exit 0 (0 unaccounted). tools/sync_site_data.py --check -> pre-existing drift on unrelated files (src/gmat_verify.py, src/verification_report.py, src/workflow.py, scripts/run_cw_gmat_slice.py, 2 test mirrors, 3 workflow_result.json fixtures), confirmed identical via git stash before this task's changes; synced the one mirror this task touched (site/data/tests/test_skill_authority_boundaries.py) to avoid adding new drift.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the solve_cw_rendezvous pi tool (.pi/extensions/cw-rendezvous-tool/index.ts) wrapping src/cw.py's mean_motion/two_burn_targeting via a new Python bridge script (scripts/cw_rendezvous_tool_bridge.py), mirroring run_gmat_verification's pi.exec bridge pattern exactly. The tool requires the retired skill's exact inputs (mu, reference radius or mean motion, explicit LVLH convention confirmation, initial/final 6-vector relative states, positive transfer duration, model-selection note) and returns either the two impulses + final state, or a structured rejection (no fabricated dv/final_state) when two_burn_targeting reports an infeasible singular boundary or raises CWSingularTransferError -- never a least-squares approximation. Removed .pi/skills/orbital-targeting-planner/SKILL.md and its dangling references (docs/baseline-checksums.md, tools/sync_site_data.py, tests/test_skill_authority_boundaries.py + site mirror); tools/compare_upstream.py needed no change since it already tracks this path as an approved, provenance-preserved local difference. Verified with tests/test_cw_rendezvous_tool_bridge.py (11 new tests, red-then-green evidence recorded in Implementation Notes): a normal two-impulse LEO quarter-orbit solve and a whole-period GEO unreachable-radial-target singular-infeasible rejection, plus input-validation and end-to-end CLI cases. Full pytest suite: 255 passed, 1 pre-existing unrelated failure (confirmed via git stash to predate this task). tools/compare_upstream.py --check passes; tools/sync_site_data.py --check shows only pre-existing, unrelated drift (also confirmed via git stash).
<!-- SECTION:FINAL_SUMMARY:END -->
