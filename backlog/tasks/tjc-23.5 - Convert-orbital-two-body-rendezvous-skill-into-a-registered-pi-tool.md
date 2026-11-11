---
id: TJC-23.5
title: Convert orbital-two-body-rendezvous skill into a registered pi tool
status: To Do
assignee: []
created_date: '2026-11-11 14:45'
updated_date: '2026-11-11 14:47'
labels: []
dependencies: []
parent_task_id: TJC-23
priority: high
type: feature
ordinal: 90000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn .pi/skills/orbital-two-body-rendezvous/SKILL.md's bounded inertial Cartesian coast fallback into a registered pi tool wrapping src/twobody.py (TwoBodyCase, propagate_cartesian_state/kepler_propagate_state).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A new pi tool wraps src/twobody.py's propagation with the same required-input validation the skill documents
- [ ] #2 Non-finite inputs, non-positive mu/steps, and zero-radius singularities are rejected, not improvised
- [ ] #3 The old SKILL.md is removed once the tool is wired into the pipeline
- [ ] #4 Tests cover a normal coast propagation and at least one rejected invalid-input case
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.5: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->
