---
id: TJC-1.16
title: Harden the complete workflow after the early vertical slice
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-02 14:11'
labels: []
dependencies:
  - TJC-1.5
  - TJC-1.12
  - TJC-1.14
  - TJC-1.15
  - TJC-1.19
  - TJC-1.21
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After the thin CW/GMAT slice works, connect the narrowed formalizer, assumption-based model selector, deterministic CW and two-body paths, GMAT verification, screenshot artifact, discrepancy handling, and explanation into the semester prototype. Reuse the slice rather than replacing it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Supported complete requests traverse formalization, selection, deterministic solution, GMAT verification, screenshot return, and explanation
- [ ] #2 Ambiguous requests stop before physics execution and return focused clarification questions
- [ ] #3 CW-invalid supported cases route to the two-body fallback and still receive GMAT verification
- [ ] #4 Numerical disagreement, missing screenshot, GMAT execution failure, and unsupported requests produce distinct non-authoritative outcomes
- [ ] #5 Execution records specified facts, assumptions, model reasoning, tool inputs/outputs, tolerances, artifacts, and final trust statement
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
