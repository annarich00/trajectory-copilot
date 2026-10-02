---
id: TJC-1.19
title: Return a unified numerical and visual verification report
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-02 14:11'
labels: []
dependencies:
  - TJC-1.21
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Define the operator-facing verification contract around GMAT. Numerical comparison, tolerance outcome, trajectory screenshot, model-selection reasoning, discrepancy status, and trust guidance must be returned together rather than scattered across repository files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The structured result includes GMAT version/run identity, compared states or trajectory quantities, units, tolerances, measured discrepancies, and PASS/WARNING/FAIL status
- [ ] #2 The result includes a directly accessible screenshot artifact reference with media type, path or URI, caption, and case/run association
- [ ] #3 Missing numerical output, failed GMAT execution, or missing screenshot cannot produce PASS
- [ ] #4 The human-readable report distinguishes solver success from independent verification success and explains likely discrepancy causes when supported by evidence
- [ ] #5 Tests cover agreement, tolerance warning, disagreement, GMAT failure, and missing/corrupt screenshot cases
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [ ] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [ ] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [ ] #4 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [ ] #5 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [ ] #6 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [ ] #7 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->
