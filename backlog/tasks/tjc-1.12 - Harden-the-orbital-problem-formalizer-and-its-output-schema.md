---
id: TJC-1.12
title: Narrow and harden the rendezvous problem formalizer
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
type: feature
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Limit natural-language interpretation to the semester rendezvous class: two spacecraft, primarily circular LEO, impulsive maneuvers, a relative state, and a specified time of flight or period count. Preserve the recovered formalizer where it already works and make assumptions and clarification needs explicit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Structured output covers central body, reference orbit or altitude/elements, relative position and velocity, LVLH convention, time of flight or period count, maneuver assumptions, and requested outputs
- [ ] #2 Every value is labeled as specified, derived, or assumed; missing and ambiguous fields remain explicit
- [ ] #3 Materially missing frame, reference orbit, state, units, or timing prevents solution and yields focused clarification questions
- [ ] #4 The formalizer does not invent altitude, gravitational parameter, circularity, coordinate convention, units, or terminal conditions
- [ ] #5 Schema tests cover complete, incomplete, contradictory, and unit-inconsistent scoped requests
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
