---
id: TJC-1.22
title: Evaluate the scoped workflow against a direct-LLM baseline
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-02 14:11'
labels: []
dependencies:
  - TJC-1.8
  - TJC-1.9
  - TJC-1.16
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the four-category rendezvous benchmark through a direct natural-language-to-LLM-answer baseline and the complete structured workflow. Evaluate which formulation, model-selection, numerical, verification, visual-artifact, and explanation errors the architecture prevents or detects; do not claim universal superiority.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Both the direct-LLM baseline and full workflow run against the same versioned benchmark requests
- [ ] #2 Scoring covers structured formulation, ambiguity detection, model selection, numerical agreement, GMAT invocation, discrepancy handling, screenshot availability, and explanation quality
- [ ] #3 Results retain prompts, model/tool versions, deterministic inputs/outputs, GMAT artifacts, tolerances, and reproducibility settings
- [ ] #4 The report includes aggregate and per-case analysis for all four benchmark categories
- [ ] #5 Conclusions identify prevented/detected error types and limitations without asserting broad astrodynamics validity
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
