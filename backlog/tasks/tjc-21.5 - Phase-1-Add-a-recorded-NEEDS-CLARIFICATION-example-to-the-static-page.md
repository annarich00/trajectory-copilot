---
id: TJC-21.5
title: 'Phase 1: Add a recorded NEEDS CLARIFICATION example to the static page'
status: To Do
assignee: []
created_date: '2026-11-10 13:37'
updated_date: '2026-11-10 13:52'
labels:
  - web-demo
dependencies:
  - TJC-21.4
documentation:
  - docs/web-demo-cases.md
parent_task_id: TJC-21
priority: low
type: feature
ordinal: 77000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The live app will ask the user for missing information when the formalizer returns NEEDS CLARIFICATION. GitHub Pages has no agent, so it can only show a recorded version of that flow. This is optional for the first release. Pages must make clear that the follow-up is a recorded continuation, so nobody believes a typed answer was processed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A stored run where the formalizer returned NEEDS CLARIFICATION lists the missing topics and stops before model selection
- [ ] #2 A button replays a saved continuation with the missing values, and no free-text input is offered on Pages
- [ ] #3 The page labels the stop and the continuation as a recorded run
- [ ] #4 The continuation run is captured from a real pipeline run, not hand-written
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
- [ ] #3 Project owner has opened the result in a browser, checked it against the acceptance criteria, and approved it before the task is marked Done
<!-- DOD:END -->
