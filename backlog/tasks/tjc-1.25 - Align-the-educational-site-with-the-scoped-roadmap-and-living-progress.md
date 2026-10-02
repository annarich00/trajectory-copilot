---
id: TJC-1.25
title: Align the educational site with the scoped roadmap and living progress
status: To Do
assignee: []
created_date: '2026-10-01 19:40'
updated_date: '2026-10-02 14:11'
labels: []
dependencies:
  - TJC-1.24
references:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
parent_task_id: TJC-1
priority: high
type: docs
ordinal: 2200
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The recovered site describes an older roadmap in which optimization was planned and GMAT was future work. Reframe it around the approved narrow rendezvous scope and make it the living demonstration surface that each completed task updates. Keep it static, offline, and dependency-free; do not introduce a framework or build step.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Overview, research, project-map, and roadmap content reflect the scoped natural-language → formalization → CW/two-body → GMAT numerical plus screenshot verification workflow
- [ ] #2 General optimization, Pareto analysis, learned CW-validity boundaries, and other semester non-goals are visibly labeled deferred or excluded rather than planned next work
- [ ] #3 A project-progress page lists active, completed, and deferred Backlog work and links each completed task to affected code, derivation pages, and verification evidence
- [ ] #4 A documented task-completion checklist requires updating site status/content, synchronizing displayed authoritative files, and smoke-testing changed routes before a task is marked Done
- [ ] #5 Detailed physics pages provide a consistent structure for assumptions, derivation, symbol definitions, source-code mapping, tests/evidence, limitations, and links to verbatim `reference/SOURCE.md` and deterministic Python
- [ ] #6 The site remains launchable through `./run_site.sh` at `127.0.0.1:4173` with no external runtime assets or network requests
- [ ] #7 A dependency-free synchronization/check command refreshes authoritative `site/data/` mirrors from repository files and fails clearly when displayed copies drift from their sources
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
