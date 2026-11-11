---
id: TJC-21.8
title: >-
  Phase 2: Stream live runs into the saved-run format and the shared front end,
  with model picker
status: To Do
assignee: []
created_date: '2026-11-10 13:37'
updated_date: '2026-11-10 13:52'
labels:
  - web-demo
dependencies:
  - TJC-21.4
  - TJC-21.7
documentation:
  - docs/web-interface-decisions.md
parent_task_id: TJC-21
priority: high
type: feature
ordinal: 80000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The same page that replays the stored demo cases should show a live run as it happens, so a demo shows real steps and plots instead of a recording. The user should be able to choose any model pi can reach. New problems use the user own provider key, and stored cases need none.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Live events are converted into the Phase 1 saved-run format and rendered by the same front end in both modes
- [ ] #2 A model picker lists models from pi --list-models and the chosen model is the one used for the run
- [ ] #3 The user supplies their own API key for new problems, held only in server memory and never written to logs, stored runs or developer-mode output
- [ ] #4 Stored cases still replay without a key
- [ ] #5 A finished live run can be saved as a stored run after redaction
- [ ] #6 The interface does not claim every model has been validated against the skills
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
- [ ] #3 Project owner has opened the result in a browser, checked it against the acceptance criteria, and approved it before the task is marked Done
<!-- DOD:END -->
