---
id: TJC-16
title: Add a demo visualization pipeline for the rendezvous workflow
status: Done
assignee: []
created_date: '2026-10-30 16:37'
updated_date: '2026-11-05 14:38'
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
- [x] #1 All subtasks are completed and linked under this parent
- [x] #2 No subtask introduces a new optimization, trade-study, or Pareto-front capability; each one only visualizes existing deterministic solver/GMAT output
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-16:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Parent closure only; no new code. AC1: TJC-16.1-16.5 all Done (backlog task view), commits 6480e43, 9b5be4e, b59775f, 396e711, 12549cc on master. AC2: grep of added lines in src/ and scripts/ since 6480e43 for pareto/optimi*/minimi*/scipy.optimize/trade study found only a docstring stating that no optimization logic exists; each plot consumes solve_cw_rendezvous / propagate_cartesian_state / GMAT output. Full suite on the rebased tree (identical tracked content to master 12549cc): 206 passed in 132 s with real GMAT on PATH (a first run had one failure in tests/test_cw_gmat_slice.py::test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window, a PNG-size comparison of two real Xvfb captures, 70946 vs 71168 bytes; it passed on isolated rerun and on the next full run, and the diff does not touch that code path). Known gaps: two-body path reports not_generated for its plot stages (TJC-16.5); /rendezvous not yet exercised in a live interactive pi session.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Closed the TJC-16 visualization parent: all five subtasks (plot dependencies, 3D scene, trajectory/burns plot, CW-vs-two-body-vs-GMAT comparison plot, live per-stage artifact reporting) are merged on master and add no optimization or Pareto capability. Verified by subtask status, a diff search for optimization code, and a 206-test full-suite pass with real GMAT.
<!-- SECTION:FINAL_SUMMARY:END -->
