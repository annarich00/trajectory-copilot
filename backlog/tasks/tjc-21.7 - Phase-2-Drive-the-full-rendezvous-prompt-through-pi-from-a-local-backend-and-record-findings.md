---
id: TJC-21.7
title: >-
  Phase 2: Drive the full /rendezvous prompt through pi from a local backend and
  record findings
status: To Do
assignee: []
created_date: '2026-11-10 13:37'
updated_date: '2026-11-10 13:52'
labels:
  - web-demo
dependencies:
  - TJC-21.1
documentation:
  - docs/web-demo-cases.md
parent_task_id: TJC-21
priority: high
type: feature
ordinal: 79000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TJC-16.5 tested the prompt CLI commands and run_rendezvous_workflow directly, but its notes say a full interactive /rendezvous session in pi was never driven end to end. A local web backend has to do exactly that, so this task proves it works before UI work depends on it. Restricting the agent to workflow tools matters even for a local demo, because a browser user types the prompts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Events from the run (messages, tool calls, artifact paths) are received and logged in order
- [ ] #2 The live agent can only use workflow tools, and general shell access is not exposed through the web interface
- [ ] #3 Any difference between this run and the TJC-16.5 recorded run is written down in the task notes
- [ ] #4 A local server starts pi with this project as its working directory using pi RPC mode or the SDK, and runs the Demo B request from docs/web-demo-cases.md through the /rendezvous prompt
- [ ] #5 The run reaches the run_gmat_verification tool and the three stage artifacts, and the outcome is compared with the stored Demo B run
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
<!-- DOD:END -->
