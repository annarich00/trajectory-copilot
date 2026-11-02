---
id: TJC-16.1
title: >-
  Add matplotlib/plotly plotting dependencies with Hypothesis-driven TDD
  groundwork
status: To Do
assignee: []
created_date: '2026-10-30 16:38'
updated_date: '2026-11-02 02:06'
labels: []
dependencies:
  - TJC-6
parent_task_id: TJC-16
priority: medium
type: task
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
None of the visualization subtasks under this parent can start until plotting/property-testing libraries exist in this project. `requirements-dev.txt` currently pins only numpy/pytest/mss/python-xlib (confirmed by inspection); hypothesis is also still absent despite TJC-6 already documenting that gap for the physics core. This task is the shared, one-time dependency and test-scaffolding setup other visualization subtasks depend on, so each of them can add Hypothesis property tests and plotting code immediately instead of repeating setup.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 matplotlib and/or plotly (whichever the chosen 3D-earth and 2D-plot subtasks actually need) are added to requirements-dev.txt with explicit pinned versions, and the documented clean-checkout setup/test commands in README.md still work unchanged
- [ ] #2 hypothesis is added to requirements-dev.txt with an explicit pinned version if not already added by TJC-6 by the time this task starts
- [ ] #3 A shared test-only helper or fixture module exists for generating valid CW/two-body state histories (reusing src/cw.py::solve_cw_rendezvous and src/twobody.py::propagate_cartesian_state outputs) for use by this task's sibling visualization subtasks' Hypothesis tests, documented in one place rather than duplicated per subtask
- [ ] #4 The full existing test suite continues to pass unchanged after the new dependencies are added
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed 'TJC-16.1:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->
