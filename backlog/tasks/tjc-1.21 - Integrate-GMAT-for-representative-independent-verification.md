---
id: TJC-1.21
title: 'Harden GMAT execution, comparison, and screenshot capture'
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-02 14:11'
labels: []
dependencies:
  - TJC-1.6
  - TJC-1.20
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn the proven vertical-slice integration into the narrow reusable verification tool. GMAT remains an independent verifier for supported CW and two-body rendezvous outputs and must always return numerical evidence plus a trajectory visualization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The tool validates the supported GMAT version/location and generates traceable scripts from structured problem and solution data
- [ ] #2 It executes GMAT, captures logs/exit status, parses final position, velocity, maneuver delta-v, and trajectory/state history with explicit units
- [ ] #3 It compares candidate and GMAT outputs using configured tolerances and returns structured PASS/WARNING/FAIL evidence
- [ ] #4 It automatically captures a non-empty orbit/trajectory screenshot or plot and exposes that artifact directly in the returned result
- [ ] #5 Missing GMAT, execution errors, malformed output, numerical disagreement, and screenshot failure are distinguishable and never reported as successful verification
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [ ] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [ ] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [ ] #4 Update the GMAT verification lesson with script-generation mapping, execution flow, parsed outputs, tolerance logic, screenshot capture, artifact return, and failure-state examples.
- [ ] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [ ] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [ ] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [ ] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->
