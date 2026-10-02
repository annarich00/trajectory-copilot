---
id: TJC-1.20
title: Build an early CW-to-GMAT vertical slice with screenshot capture
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-02 14:11'
labels: []
dependencies:
  - TJC-1.25
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Immediately prove the riskiest end-to-end path using one recovered, well-specified CW rendezvous case. Reuse existing formalization/physics components as-is where possible: load or form the structured case, run deterministic CW targeting, generate and execute GMAT, compare results, capture a trajectory visualization, and return one combined report. Hardening and broader benchmark coverage come later.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 One well-specified circular-LEO CW case runs from structured input through deterministic CW solution and an automatically generated GMAT script
- [ ] #2 The supported GMAT executable is invoked non-interactively or through a documented automatable mechanism and its exit status and outputs are captured
- [ ] #3 The slice compares at least final position, final velocity, and maneuver delta-v using explicit units and provisional tolerances
- [ ] #4 The run automatically produces a non-empty orbit/trajectory screenshot or plot and returns it in the verification result, not only as an undocumented repository file
- [ ] #5 A single documented command reproduces the complete slice and reports failures without claiming verification
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [ ] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [ ] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [ ] #4 Publish an early vertical-slice demo page that traces the selected case from input through CW code, generated GMAT script, numerical comparison, and returned trajectory screenshot.
- [ ] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [ ] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [ ] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [ ] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->
