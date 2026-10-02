---
id: TJC-1.4
title: Audit CW two-burn targeting and singularity handling
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-02 14:11'
labels: []
dependencies:
  - TJC-1.3
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: task
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The prior solver reportedly produced absurd delta-v near singular transfer times by silently using least squares. Independently review the two-burn boundary-value equations and ensure exact and near singular Phi_rv cases fail explicitly instead of returning plausible-looking trajectories.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Two-burn targeting reproduces at least one independently derived, non-singular benchmark within stated tolerances
- [ ] #2 The exact one-orbit case tf=2*pi/n is rejected with a machine-readable failure and human-readable reason
- [ ] #3 Near-singular cases are rejected using a documented conditioning criterion, with boundary tests on both sides of the criterion
- [ ] #4 No fallback silently changes transfer time or substitutes a least-squares answer
- [ ] #5 Returned burns satisfy the requested terminal state when propagated with CW in accepted cases
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [ ] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [ ] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [ ] #4 Update the targeting and singularity lessons with the partitioned STM derivation, burn equations, conditioning rationale, failure behavior, and links to exact code/tests.
- [ ] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [ ] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [ ] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [ ] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->
