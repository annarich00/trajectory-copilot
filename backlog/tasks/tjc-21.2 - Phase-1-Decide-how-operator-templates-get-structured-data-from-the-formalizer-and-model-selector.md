---
id: TJC-21.2
title: >-
  Phase 1: Decide how operator templates get structured data from the formalizer
  and model selector
status: To Do
assignee: []
created_date: '2026-11-10 13:37'
updated_date: '2026-11-12 13:35'
labels:
  - web-demo
dependencies:
  - TJC-21.1
documentation:
  - docs/web-interface-decisions.md
parent_task_id: TJC-21
priority: high
type: task
ordinal: 74000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GMAT results and artifact paths are already JSON, but the orbital-problem-formalizer and orbital-model-selector produce Markdown prose. Operator mode uses fixed templates filled with real values, so it needs reliable fields from those two steps (or an agreed fallback). The choice affects skills that have benchmark evaluations under evaluations/, so it needs an explicit decision before templates are written.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A recorded decision chooses between parsing the Markdown output and having the skills also emit a structured block, with the reason
- [ ] #2 If skills change, the evaluations under evaluations/ still pass and the formalizer and selector output sections remain unchanged
- [ ] #3 The chosen approach extracts the values operator templates need from Demo A, B and C and from at least one NEEDS CLARIFICATION result
- [ ] #4 The chosen approach extracts the values operator templates need from Demo A, B and C and from at least one NEEDS CLARIFICATION result
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
<!-- DOD:END -->
