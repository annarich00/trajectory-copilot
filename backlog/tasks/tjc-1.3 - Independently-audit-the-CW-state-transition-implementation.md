---
id: TJC-1.3
title: Independently audit the CW state-transition implementation
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
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The CW state-transition matrix is foundational and must be reviewed against an authoritative derivation rather than validated only by its own tests. Check each block, state ordering, signs, dimensions, time-zero behavior, and circular-chief assumptions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 An audit note maps every implemented STM term to an independently cited equation
- [ ] #2 The implementation uses the documented state ordering and LVLH convention consistently
- [ ] #3 At t=0 the STM is identity within a stated numerical tolerance
- [ ] #4 Any sign, unit, or equation defect found by the audit is corrected and covered by a regression test
- [ ] #5 The CW assumptions and unsupported regimes are visible in code-facing documentation
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [ ] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [ ] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [ ] #4 Update the CW STM lesson with a step-by-step derivation of every matrix block, symbol definitions, axis/sign conventions, and term-level links to `src/cw.py` and its tests.
- [ ] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [ ] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [ ] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [ ] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->
