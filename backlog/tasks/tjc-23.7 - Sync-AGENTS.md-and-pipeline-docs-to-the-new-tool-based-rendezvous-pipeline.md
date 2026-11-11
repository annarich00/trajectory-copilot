---
id: TJC-23.7
title: Sync AGENTS.md and pipeline docs to the new tool-based rendezvous pipeline
status: To Do
assignee: []
created_date: '2026-11-11 14:45'
updated_date: '2026-11-11 14:47'
labels: []
dependencies:
  - TJC-23.1
  - TJC-23.2
  - TJC-23.3
  - TJC-23.4
  - TJC-23.5
parent_task_id: TJC-23
priority: medium
type: docs
ordinal: 92000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once the formalizer, model-selector, CW, two-body, and orchestration steps are all registered pi tools instead of skills/prompts, AGENTS.md's standing rendezvous-routing rule and any other active pipeline documentation that names the old skills/prompt must be updated to name the new tools, and the full test suite must still pass.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AGENTS.md's rendezvous routing rule names the new tools (not the retired skills/prompt) in pipeline order
- [ ] #2 No active pipeline doc (outside historical docs/evaluation artifacts) still instructs applying a retired skill or invoking the retired /rendezvous prompt
- [ ] #3 The existing test suite (including src/workflow.py and run_gmat_verification coverage) passes unchanged
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Work lands as exactly one atomic Git commit per docs/task-commit-policy.md, subject prefixed with the exact task ID (e.g. 'TJC-23.7: <summary>'), containing only this task's implementation/tests/docs and finalized Backlog metadata
<!-- DOD:END -->
