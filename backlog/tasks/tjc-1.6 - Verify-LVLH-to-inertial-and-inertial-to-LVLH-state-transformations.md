---
id: TJC-1.6
title: Verify LVLH-to-inertial and inertial-to-LVLH state transformations
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-02 14:11'
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
- [ ] #1 The documented LVLH basis is orthonormal and right-handed for representative chief states
- [ ] #2 LVLH to inertial to LVLH round trips recover relative position and velocity within stated tolerances
- [ ] #3 Inertial to LVLH to inertial round trips recover chief/deputy states within stated tolerances
- [ ] #4 A nonzero relative-velocity case demonstrates that rotating-frame transport terms are handled correctly
- [ ] #5 Degenerate chief states are rejected with explicit errors
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [ ] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [ ] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [ ] #4 Update the frame-transformation lesson with LVLH basis construction, handedness, angular-rate transport terms, forward/inverse equations, and round-trip evidence linked to code/tests.
- [ ] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [ ] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [ ] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [ ] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->
