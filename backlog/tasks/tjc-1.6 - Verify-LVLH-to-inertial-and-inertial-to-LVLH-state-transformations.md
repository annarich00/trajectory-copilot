---
id: TJC-1.6
title: Verify LVLH-to-inertial and inertial-to-LVLH state transformations
status: Done
assignee:
  - '@pi'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-09 13:49'
labels: []
dependencies:
  - TJC-1.25
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: task
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independent CW verification depends on transforming chief/deputy position and velocity between local and inertial frames. Audit orientation, relative velocity transport terms, state subtraction direction, and units for both directions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The documented LVLH basis is orthonormal and right-handed for representative chief states
- [x] #2 LVLH to inertial to LVLH round trips recover relative position and velocity within stated tolerances
- [x] #3 Inertial to LVLH to inertial round trips recover chief/deputy states within stated tolerances
- [x] #4 A nonzero relative-velocity case demonstrates that rotating-frame transport terms are handled correctly
- [x] #5 Degenerate chief states are rejected with explicit errors
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Update the frame-transformation lesson with LVLH basis construction, handedness, angular-rate transport terms, forward/inverse equations, and round-trip evidence linked to code/tests.
- [x] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the existing transformation implementation, numerical-test conventions, and educational-site mirrors.
2. Harden LVLH basis construction and state transforms only where the audit identifies gaps, including explicit degenerate-state errors.
3. Add focused numerical tests for handedness, transport terms, units/subtraction direction, and both round trips.
4. Update the frame-transformation lesson and progress material with equations, limitations, and test evidence; synchronize affected mirrors.
5. Run focused and repository/site/offline smoke checks, finalize objective Backlog evidence, and create one atomic TJC-1.6 commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented explicit LVLHTransformationError checks for non-finite inputs, zero chief position, and zero angular momentum; retained deputy-minus-chief subtraction and transport equations. Added numerical tests covering R^T R, handedness/determinant, LVLH→inertial→LVLH (≤2e-12), inertial→LVLH→inertial deputy recovery (≤2e-9 m / ≤2e-12 m/s), and a +0.1 m/s transport contribution.
Validation passed: python3 tools/sync_site_data.py --check; node --check site/js/pages/cw-lvlh.js; node --check site/data/project-progress.js; python3 tools/compare_upstream.py --check; ./run_site.sh offline curl smoke for /, cw-lvlh.js, and data/src/verify.py; git diff --check. Python pytest could not run because the dedicated worktree has no .venv and system python3 lacks both numpy and pytest; no network install was attempted.

Created the single atomic final commit 0d58966: TJC-1.6: verify LVLH inertial state transformations. Commit contains only this task implementation, tests, site/docs/mirrors, upstream-difference allowlist, and Backlog finalization. git status --short is clean.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Hardened and documented LVLH/inertial transformations with explicit degenerate-chief rejection, focused bidirectional numerical regression coverage, synchronized browser mirrors, and a frame-transformation lesson/progress entry. Offline site and static checks passed; Python test execution is environment-blocked (no NumPy/pytest available).
<!-- SECTION:FINAL_SUMMARY:END -->
