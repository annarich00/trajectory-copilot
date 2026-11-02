---
id: TJC-16.4
title: >-
  Add a CW-vs-two-body-vs-GMAT verification comparison plot with
  position/velocity error histories
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
ordinal: 65000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The operator wants a single graph for a demo that visually backs up the numeric GMAT comparison already produced by src/gmat_verify.py::compare_gmat_final_state and src/verification_report.py: the CW (or two-body) prediction, the independent GMAT reference, plotted together, plus the position-error and velocity-error time histories (not just the single final-state error already reported numerically) so disagreement or agreement is visible over the whole transfer, not only at the terminal point.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A plotting function accepts the CW/two-body trajectory time history and the GMAT-parsed report time history (src/gmat_verify.py::parse_inertial_report or the LVLH-report equivalent) for the same case, and renders overlaid position trajectories for both sources on one set of axes
- [ ] #2 The same function (or a paired one sharing inputs) renders position-error and velocity-error magnitude versus time, computed only from the already-parsed/compared state histories, with the existing declared tolerance (position_m/velocity_mps) drawn as a reference line so pass/fail is visible, not just stated
- [ ] #3 The function reports an explicit error rather than a plot when the GMAT comparison status is INCOMPLETE/UNAVAILABLE (no fabricated GMAT trace is ever drawn), consistent with this project's existing VERIFIED-vs-solver-only distinction
- [ ] #4 Hypothesis property tests assert that, for randomly generated matching CW/GMAT time-aligned state-history pairs, the computed error-history values plotted equal the independently computed pointwise difference to numerical tolerance, and that mismatched time bases are rejected rather than silently interpolated or misaligned
- [ ] #5 Each new test is recorded with red-then-green evidence per TJC-5/TJC-6's established policy before being marked passing
- [ ] #6 The rendered figure(s) are saved to returned artifact path(s) suitable for direct display during a demo, and the existing unified verification report gains a reference to this artifact path alongside its existing numeric comparison fields
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed 'TJC-16.4:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->
