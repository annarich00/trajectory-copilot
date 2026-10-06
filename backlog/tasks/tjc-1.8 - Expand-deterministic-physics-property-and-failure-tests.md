---
id: TJC-1.8
title: Add focused tests for the scoped end-to-end workflow
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-06 15:27'
labels: []
dependencies:
  - TJC-1.16
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: task
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add only the unit, physical-property, routing, failure, and integration tests needed to protect the narrowed rendezvous workflow. Tests should exercise deterministic physics, model selection, GMAT result handling, screenshot inclusion, and refusal/clarification behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Tests cover CW propagation/targeting, two-body propagation, and LVLH/inertial transformation properties used by the supported workflow
- [ ] #2 Tests cover ambiguous input, CW-applicable routing, CW-invalid routing, singular targeting, GMAT disagreement, and unavailable-GMAT behavior
- [ ] #3 A verification result cannot pass when numerical output or the required screenshot artifact is missing
- [ ] #4 Tests confirm the LLM-facing layer never supplies authoritative orbital states or delta-v without deterministic tool output
- [ ] #5 The full focused suite runs from the documented clean-checkout command
- [ ] #6 Tests enforce that supported two-body outputs invoke or retain pinned Poliastro evidence, while UNAVAILABLE, UNSUPPORTED, and disagreement outcomes cannot be represented as verified
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
