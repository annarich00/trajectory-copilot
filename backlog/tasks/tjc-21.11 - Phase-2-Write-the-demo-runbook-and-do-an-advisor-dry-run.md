---
id: TJC-21.11
title: 'Phase 2: Write the demo runbook and do an advisor dry run'
status: To Do
assignee: []
created_date: '2026-11-10 13:37'
updated_date: '2026-11-10 13:43'
labels:
  - web-demo
dependencies:
  - TJC-21.6
  - TJC-21.9
  - TJC-21.10
documentation:
  - docs/web-interface-decisions.md
parent_task_id: TJC-21
priority: medium
type: docs
ordinal: 83000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The goal is a smooth live demo for the advisor. A short runbook captures how to start the backend, which cases to show, expected timings (GMAT start-up is slow), what to say, and what to do when something fails. A dry run catches problems before the real demo.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A runbook describes starting the local backend, choosing a model, running a stored case and a new problem
- [ ] #2 It lists expected run time, known failure modes and the recovery for each
- [ ] #3 It states the one variable cost, which is the user own LLM usage, and tells the user to check one live run in the provider dashboard
- [ ] #4 A full dry run is done on the demo machine and the outcome is recorded in task notes
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 Project owner ran the dry run on the demo machine and approved the runbook before the task is marked Done
<!-- DOD:END -->
