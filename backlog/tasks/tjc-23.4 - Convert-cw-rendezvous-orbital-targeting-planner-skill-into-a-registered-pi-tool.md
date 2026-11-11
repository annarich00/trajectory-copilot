---
id: TJC-23.4
title: >-
  Convert cw-rendezvous (orbital-targeting-planner) skill into a registered pi
  tool
status: To Do
assignee: []
created_date: '2026-11-11 14:45'
updated_date: '2026-11-11 14:47'
labels: []
dependencies: []
parent_task_id: TJC-23
priority: high
type: feature
ordinal: 89000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn .pi/skills/orbital-targeting-planner/SKILL.md's deterministic CW two-impulse targeting handoff into a registered pi tool that wraps src/cw.py (mean_motion, two_burn_targeting) the same way run_gmat_verification wraps GMAT execution, instead of relying on the LLM to call src/cw.py itself.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A new pi tool wraps src/cw.py's two_burn_targeting/mean_motion with the same required-input validation the skill documents
- [ ] #2 CWSingularTransferError is surfaced as a structured rejection, not approximated
- [ ] #3 The old SKILL.md is removed once the tool is wired into the pipeline
- [ ] #4 Tests cover a normal two-impulse solve and a singular-transfer rejection
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.4: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->
