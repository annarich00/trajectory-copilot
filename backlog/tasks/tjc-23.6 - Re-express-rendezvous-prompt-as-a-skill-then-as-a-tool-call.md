---
id: TJC-23.6
title: Re-express /rendezvous prompt as a skill
status: To Do
assignee: []
created_date: '2026-11-11 14:45'
updated_date: '2026-11-11 16:16'
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
The user wants the orchestration currently in .pi/prompts/rendezvous.md turned into a skill: step ordering, stop conditions, visualization stage timing, and the GMAT-example review hookup, re-expressed as a .pi/skills/*/SKILL.md the agent applies the same way the other rendezvous skills were applied before their own tool conversions. Scope is limited to the prompt-to-skill re-expression only -- this task does not convert that new skill into a registered pi tool call; it depends on TJC-23.2 through TJC-23.5 only because the new skill must instruct the agent to call those already-converted tools (and the existing run_gmat_verification tool) in the documented order, not because this task itself produces another tool.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The orchestration logic in .pi/prompts/rendezvous.md (step ordering, stop conditions, visualization stage timing, GMAT-example review hookup) is captured in an intermediate skill definition
- [ ] #2 The stop conditions (NEEDS CLARIFICATION / OUT OF SCOPE halt, single-spacecraft coast exception) and the gmat-example-reviewer subagent handoff are preserved
- [ ] #3 The new skill reproduces the prompt's documented behavior (confirmed by an end-to-end test or manual run covering at least one CW and one bounded-two-body case) and .pi/prompts/rendezvous.md is then removed, so the orchestration lives only in the skill, not duplicated in both places
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.6: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->
