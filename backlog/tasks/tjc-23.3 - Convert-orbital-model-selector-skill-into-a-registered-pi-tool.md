---
id: TJC-23.3
title: Convert orbital-model-selector skill into a registered pi tool
status: To Do
assignee: []
created_date: '2026-11-11 14:44'
updated_date: '2026-11-11 14:47'
labels: []
dependencies: []
parent_task_id: TJC-23
priority: high
type: feature
ordinal: 88000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn .pi/skills/orbital-model-selector/SKILL.md's six-item assessment and CW/bounded-two-body/UNSUPPORTED/NEEDS-MORE-INFO selection logic into a registered pi tool callable on the formalizer tool's output.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A new pi tool implements the six-item assessment and the four-way selection result
- [ ] #2 The tool consumes the formalizer tool's structured output directly
- [ ] #3 The old SKILL.md is removed once the tool is wired into the pipeline
- [ ] #4 Tests cover at least one CW-selected and one bounded-two-body-selected case
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.3: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->
