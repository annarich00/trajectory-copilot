---
id: TJC-16.2
title: Add an interactive 3D relative-position visualization of target and chaser
status: To Do
assignee: []
created_date: '2026-10-30 16:38'
updated_date: '2026-11-02 02:06'
labels: []
dependencies:
  - TJC-16.1
parent_task_id: TJC-16
priority: medium
type: feature
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The operator wants a 3D visual during a live demo showing where the target and chaser spacecraft are relative to each other around an illustrative Earth, without exposing or requiring any real TLE/ephemeris data (the exact inertial placement around Earth may be illustrative/made up; the relative position between target and chaser must be the physically exact one from the already-computed state history). This gives a visually intuitive companion to the numeric LVLH relative state already in every workflow result.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A plotting function accepts an already-computed relative-state time history (same array shape/units already produced by src/cw.py::solve_cw_rendezvous or src/twobody.py::propagate_cartesian_state) and an illustrative target orbit radius/epoch, and renders an interactive 3D scene (plotly) showing a representative Earth, the target near a representative circular-orbit location, and the chaser offset from it by the exact relative position at each sampled time
- [ ] #2 The function never requires, accepts, or fabricates real TLE/ephemeris/epoch data; any inertial placement used only to anchor the illustrative scene is clearly labeled illustrative/not-authoritative in the figure, separate from the authoritative relative-state values driving the chaser offset
- [ ] #3 Hypothesis property tests assert that, for randomly generated non-degenerate relative-state histories, the rendered chaser-minus-target offset recovered from the figure data matches the input relative-state position to numerical tolerance, and that degenerate/empty input is rejected rather than silently rendered
- [ ] #4 Each new test is recorded with red-then-green evidence per TJC-5/TJC-6's established policy before being marked passing
- [ ] #5 The rendered figure is saved as a standalone HTML (or equivalent) artifact path returned by the function, so it can be opened directly during a demo without a live Python session
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed 'TJC-16.2:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->
