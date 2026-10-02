---
id: TJC-1.9
title: Create the four-category rendezvous benchmark
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-02 14:11'
labels: []
dependencies:
  - TJC-1.12
  - TJC-1.14
  - TJC-1.21
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: medium
type: task
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a small, reviewable benchmark for the semester experiment. It must cover straightforward CW, boundary, CW-invalid/two-body, and ambiguous or incomplete natural-language cases without expanding into broad astrodynamics coverage.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The benchmark contains at least one case in each of the four required categories: straightforward CW, boundary, CW-invalid, and ambiguous/incomplete
- [ ] #2 Each case records the request, expected structured problem, expected model, reference numerical result or expected clarification, GMAT tolerance, and expected explanation behavior
- [ ] #3 Solvable cases include a reproducible GMAT script/result and required trajectory screenshot reference
- [ ] #4 Boundary cases test documented CW assumptions without asserting a universal validity threshold
- [ ] #5 Fixtures are schema-validated and versioned with units, frames, assumptions, and provenance
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
