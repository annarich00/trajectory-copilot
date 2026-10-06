---
id: TJC-1.5
title: Harden the deterministic two-body rendezvous fallback
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-06 15:27'
labels: []
dependencies:
  - TJC-1.25
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - docs/poliastro-verification-architecture.md
parent_task_id: TJC-1
priority: high
type: task
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Preserve the recovered nonlinear two-body propagator and make it sufficient for the explicitly supported rendezvous fallback cases when CW assumptions are not satisfied. This is a bounded propagation/solution path, not generalized targeting or trajectory optimization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The supported two-body fallback inputs, outputs, units, frames, and maneuver limitations are explicitly defined
- [ ] #2 At least one scoped CW-invalid rendezvous case produces a deterministic two-body trajectory or propagation result suitable for GMAT verification
- [ ] #3 A known two-body orbit agrees with an analytical or independent reference within declared position and velocity tolerances
- [ ] #4 Specific orbital energy and angular momentum behavior are tested over representative supported durations
- [ ] #5 Unsupported targeting, perturbations, or optimization requests return an explicit limitation rather than an improvised result
- [ ] #6 The hardened current propagator exposes stable like-for-like Cartesian cases and metadata required by the pinned Poliastro verification adapter in TJC-1.7
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [ ] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [ ] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [ ] #4 Update the two-body lesson with the point-mass equation, state derivative, RK4 stages, invariants, supported fallback semantics, and links to exact code/tests.
- [ ] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [ ] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [ ] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [ ] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->
