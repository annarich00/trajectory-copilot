---
id: TJC-21.4
title: 'Phase 1: Build the static demo page with operator and developer modes'
status: To Do
assignee: []
created_date: '2026-11-10 13:37'
updated_date: '2026-11-10 13:52'
labels:
  - web-demo
dependencies:
  - TJC-21.1
  - TJC-21.3
documentation:
  - docs/web-interface-decisions.md
parent_task_id: TJC-21
priority: high
type: feature
ordinal: 76000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
This is the page the advisor will see on GitHub Pages and the front end that Phase 2 reuses. It replays a stored run step by step with a mode toggle: operator mode shows the fixed templates, developer mode shows the raw agent output and tool calls. It also needs to settle whether it extends the existing site/ lab or lives in a new directory, which the decisions document leaves open.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A decision on extending site/ versus a new directory is recorded and applied
- [ ] #2 A toggle switches between operator mode (templates) and developer mode (raw agent output and tool calls)
- [ ] #3 The page is labelled as a recorded run, and works from static files with no server and no API key
- [ ] #4 A not_generated stage and a failed verification display their status and reason
- [ ] #5 The page was opened in a browser and each step checked against the stored run
- [ ] #6 If an artifact file (for example the 3D scene) is missing, the page shows a clear message for that step instead of failing silently
- [ ] #7 The page lets the user pick Demo A, B or C and replays it step by step, showing each step and its artifacts in pipeline order
- [ ] #8 Demo A is shown as NOT VERIFIED with its NUMERICAL_DISAGREEMENT status, and Demo C shows its not_generated plot stages with reasons
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
- [ ] #3 Project owner has opened the result in a browser, checked it against the acceptance criteria, and approved it before the task is marked Done
<!-- DOD:END -->
