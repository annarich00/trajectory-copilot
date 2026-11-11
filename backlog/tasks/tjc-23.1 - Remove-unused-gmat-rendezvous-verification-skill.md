---
id: TJC-23.1
title: Remove unused gmat-rendezvous-verification skill
status: To Do
assignee: []
created_date: '2026-11-11 14:44'
updated_date: '2026-11-11 14:47'
labels: []
dependencies: []
parent_task_id: TJC-23
priority: medium
type: chore
ordinal: 86000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
gmat-rendezvous-verification's SKILL.md is not invoked by .pi/prompts/rendezvous.md; verification is already performed via the registered run_gmat_verification pi tool. Other skills (orbital-model-selector, cw-rendezvous, orbital-two-body-rendezvous) reference it only as prose ('hand off to gmat-rendezvous-verification'), which must be updated once it is deleted.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The .pi/skills/gmat-rendezvous-verification directory is deleted
- [ ] #2 No remaining active skill or prompt file (orbital-model-selector, orbital-targeting-planner, orbital-two-body-rendezvous, rendezvous.md) references gmat-rendezvous-verification by name
- [ ] #3 A repo-wide search confirms only historical docs/evaluation artifacts (not active pipeline files) mention the old skill name
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.1: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->
