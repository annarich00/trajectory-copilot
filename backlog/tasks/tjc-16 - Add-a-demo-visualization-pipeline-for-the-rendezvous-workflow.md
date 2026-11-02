---
id: TJC-16
title: Add a demo visualization pipeline for the rendezvous workflow
status: To Do
assignee: []
created_date: '2026-10-30 16:37'
updated_date: '2026-11-02 02:06'
labels: []
dependencies: []
priority: medium
type: feature
ordinal: 61000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The operator needs to demo a solved rendezvous case to their advisor live, and the current workflow only returns Markdown/JSON plus a static SVG/GMAT screenshot at the very end. There is no incremental, visual way to show what each pipeline stage (formalize, model-select, CW/two-body solve, GMAT verification) actually produced, and no 3D sense of where the target/chaser are relative to each other. This parent task groups the visualization subtasks that add that without adding new physics: every plot consumes already-computed, already-verified numeric state histories from `src/cw.py::solve_cw_rendezvous`, `src/twobody.py::propagate_cartesian_state`, and `src/gmat_verify.py` comparison output, and must not become a generalized trajectory-optimization or Pareto-front feature (both are explicit semester non-goals per `backlog/docs/specifications/semester-scope/doc-1 - Trajectory-CoPilot-Semester-Scope.md`).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All subtasks are completed and linked under this parent
- [ ] #2 No subtask introduces a new optimization, trade-study, or Pareto-front capability; each one only visualizes existing deterministic solver/GMAT output
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed 'TJC-16:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->
