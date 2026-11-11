---
id: TJC-23.6
title: 'Re-express /rendezvous prompt as a skill, then as a tool call'
status: To Do
assignee: []
created_date: '2026-11-11 14:45'
updated_date: '2026-11-11 14:47'
labels: []
dependencies:
  - TJC-23.2
  - TJC-23.3
  - TJC-23.4
  - TJC-23.5
parent_task_id: TJC-23
priority: high
type: feature
ordinal: 91000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The user wants the orchestration currently in .pi/prompts/rendezvous.md turned into a skill first, and then (matching the fate of all other skills in this parent task) that skill retired in favor of a registered pi tool call, so no prompt-template step and no skill-application step remains anywhere in the pipeline -- only explicit tool calls. This depends on TJC-23.2 through TJC-23.5 already existing as callable tools, since the orchestrating tool/skill must call them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The orchestration logic in .pi/prompts/rendezvous.md (step ordering, stop conditions, visualization stage timing, GMAT-example review hookup) is captured in an intermediate skill definition
- [ ] #2 That orchestration is then implemented as a registered pi tool that calls the formalizer/selector/CW/two-body tools from TJC-23.2-23.5 and the existing run_gmat_verification tool in the documented order
- [ ] #3 The stop conditions (NEEDS CLARIFICATION / OUT OF SCOPE halt, single-spacecraft coast exception) and the gmat-example-reviewer subagent handoff are preserved
- [ ] #4 .pi/prompts/rendezvous.md is removed once the tool reproduces its behavior
- [ ] #5 An end-to-end test or manual run demonstrates the new orchestration tool reproduces at least one CW and one bounded-two-body case correctly
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.6: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->
