---
id: TJC-1
title: Deliver the scoped Trajectory CoPilot rendezvous prototype
status: To Do
assignee: []
created_date: '2026-10-01 14:16'
updated_date: '2026-10-02 14:11'
labels: []
dependencies: []
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
priority: high
type: feature
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build and evaluate a deliberately narrow rendezvous workflow: natural-language request → structured problem → documented CW applicability assessment → deterministic CW or two-body path → independent GMAT numerical and visual verification → human-readable explanation. Preserve and harden the recovered baseline rather than rebuilding it. Semester scope is circular-LEO-oriented two-spacecraft rendezvous with impulsive maneuvers; generalized astrodynamics, learned validity boundaries, and trajectory optimization are explicitly deferred.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A supported natural-language rendezvous request reaches a deterministic CW or two-body result and independent GMAT verification through one reproducible workflow
- [ ] #2 The workflow distinguishes specified information from agent assumptions and requests clarification when ambiguity materially affects the solution
- [ ] #3 CW selection is justified from documented physical assumptions; unsuitable cases escalate to the scoped two-body path without using an arbitrary universal distance threshold
- [ ] #4 Every successful verification result includes numerical GMAT comparison, tolerance outcome, and an orbit/trajectory screenshot directly accessible in the returned report
- [ ] #5 A reproducible benchmark covers straightforward CW, boundary, CW-invalid, and ambiguous cases and compares the structured workflow with a direct-LLM baseline
- [ ] #6 No semester deliverable implements generalized optimization, Pareto analysis, CR3BP, cislunar dynamics, broad mission planning, or a learned CW-validity boundary
- [ ] #7 The dependency-free educational site runs through `./run_site.sh` and reflects the current completed-task state, code, derivations, evidence, and scoped roadmap
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Confirm every completed in-scope child task is represented accurately in the educational site and all displayed authoritative artifacts match the repository.
- [ ] #2 Run the complete site smoke check locally at `http://127.0.0.1:4173` with no package installation or network access.
- [ ] #3 Verify every completed post-policy child task is represented by one independently reviewable and revertible atomic commit whose subject begins with its task ID.
- [ ] #4 Confirm the final repository working tree is clean and the educational site’s progress entries map completed tasks to their Git commit subjects.
<!-- DOD:END -->
