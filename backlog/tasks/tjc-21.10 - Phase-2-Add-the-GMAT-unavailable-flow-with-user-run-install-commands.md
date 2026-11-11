---
id: TJC-21.10
title: 'Phase 2: Add the GMAT-unavailable flow with user-run install commands'
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
ordinal: 82000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
If GMAT is missing, the project already reports NOT VERIFIED instead of faking a PASS. The interface should help a user get GMAT without the server ever installing software: it asks whether they want to install it and whether they want step-by-step help, and shows commands they run themselves.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 When GMAT is not found, the interface reports NOT VERIFIED with the existing failure mode
- [ ] #2 The interface asks whether to install GMAT and whether step-by-step help is wanted
- [ ] #3 Install commands are shown for the user to run, and the server and agent never run them
- [ ] #4 The run does not claim verification and does not substitute the deterministic plot as GMAT verification
- [ ] #5 A test or recorded run covers a run with GMAT unavailable
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
- [ ] #3 Project owner has opened the result in a browser, checked it against the acceptance criteria, and approved it before the task is marked Done
<!-- DOD:END -->
