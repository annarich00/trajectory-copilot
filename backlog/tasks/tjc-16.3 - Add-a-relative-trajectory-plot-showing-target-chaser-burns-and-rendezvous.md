---
id: TJC-16.3
title: 'Add a relative-trajectory plot showing target, chaser, burns, and rendezvous'
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
ordinal: 64000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The operator wants a single clear picture of the solved relative trajectory: target at origin, chaser path, the two burn locations/vectors, and the final rendezvous point, reusing exactly the CW and two-body state histories already computed by src/cw.py::solve_cw_rendezvous (trajectory_states/trajectory_times, dv0_mps/dv1_mps, final_state) and src/twobody.py::propagate_cartesian_state, so the plot is a direct visualization of the authoritative numeric result rather than a new calculation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A plotting function accepts a CWRendezvousSolution (or equivalent two-body state history plus burn vectors) and renders a 2D/3D LVLH-frame or inertial-frame trajectory plot showing the target reference point, the chaser's full path, markers at the two burn locations with annotated delta-v vectors, and the final rendezvous/terminal point
- [ ] #2 The function works for both the CW path (via solve_cw_rendezvous output) and the bounded two-body fallback path (via propagate_cartesian_state output), sharing one plotting implementation rather than two divergent ones where the underlying data shape allows it
- [ ] #3 A singular-infeasible CW result (no burns/trajectory) is rejected by the plotting function with an explicit error rather than silently plotting a fabricated or partial trajectory
- [ ] #4 Hypothesis property tests assert that, for randomly generated non-singular feasible CW solutions, the plotted terminal point matches the solution's final_state position to numerical tolerance, and that burn markers' plotted positions match the known burn-application points (start and end of the transfer) from the input trajectory
- [ ] #5 Each new test is recorded with red-then-green evidence per TJC-5/TJC-6's established policy before being marked passing
- [ ] #6 The rendered figure is saved to a returned artifact path (PNG/SVG/HTML) suitable for direct display during a demo
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed 'TJC-16.3:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->
