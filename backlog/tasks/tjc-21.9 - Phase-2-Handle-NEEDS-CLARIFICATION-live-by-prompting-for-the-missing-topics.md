---
id: TJC-21.9
title: 'Phase 2: Handle NEEDS CLARIFICATION live by prompting for the missing topics'
status: To Do
assignee: []
created_date: '2026-11-10 13:37'
updated_date: '2026-11-10 13:43'
labels:
  - web-demo
dependencies:
  - TJC-21.8
documentation:
  - docs/web-interface-decisions.md
parent_task_id: TJC-21
priority: medium
type: feature
ordinal: 81000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When the formalizer cannot proceed, the user should see what is missing and be able to answer, so the pipeline continues instead of silently stopping. The standing rule in AGENTS.md requires halting at NEEDS CLARIFICATION and genuinely OUT OF SCOPE results, so the web flow must not skip ahead to model selection or a solver call.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A NEEDS CLARIFICATION result shows the list of missing topics in the interface
- [ ] #2 The user can answer in the chat and the pipeline resumes from the formalizer with the answers
- [ ] #3 The pipeline never reaches model selection or a solver call while the result is NEEDS CLARIFICATION or OUT OF SCOPE
- [ ] #4 A genuinely OUT OF SCOPE result is reported and the run stops
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
- [ ] #3 Project owner has opened the result in a browser, checked it against the acceptance criteria, and approved it before the task is marked Done
<!-- DOD:END -->
