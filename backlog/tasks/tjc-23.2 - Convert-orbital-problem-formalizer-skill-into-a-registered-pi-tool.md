---
id: TJC-23.2
title: Convert orbital-problem-formalizer skill into a registered pi tool
status: To Do
assignee: []
created_date: '2026-11-11 14:44'
updated_date: '2026-11-11 14:47'
labels: []
dependencies: []
parent_task_id: TJC-23
priority: high
type: feature
ordinal: 87000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn .pi/skills/orbital-problem-formalizer/SKILL.md's required Markdown schema and provenance rules into a registered pi tool (e.g. an extension under .pi/extensions/) that an agent calls explicitly instead of applying free-form skill instructions, mirroring the existing run_gmat_verification tool's auditable-call pattern.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A new pi tool implements the formalizer's required output schema (Scope through Readiness) and provenance-label rules
- [ ] #2 The tool's input/output contract is structured (not free text) wherever the skill specifies structured fields
- [ ] #3 The old SKILL.md is removed once the tool is wired into the pipeline
- [ ] #4 Unit/integration tests cover at least one READY TO SOLVE and one NEEDS CLARIFICATION case
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.2: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->
