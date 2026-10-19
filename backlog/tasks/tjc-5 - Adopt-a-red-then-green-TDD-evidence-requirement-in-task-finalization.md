---
id: TJC-5
title: Adopt a red-then-green TDD evidence requirement in task finalization
status: To Do
assignee: []
created_date: '2026-10-19 12:16'
labels: []
dependencies: []
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A test-suite audit (prompted by the operator, scoped to this repo, read-only) found no textual or process evidence of test-first discipline: every inspected Backlog task implementation plan lists "implement X" before "add tests for X", and no doc anywhere states a TDD expectation. The operator decided on an enforcement approach (Option B from that audit discussion): extend the existing evidence-gated finalization convention (tasks already require exact command/output evidence before Done) to require two recorded pytest runs for any new test added under this policy -- one showing the new test failing for the stated reason before the corresponding implementation code exists (red), and one showing it passing afterward (green) -- rather than restructuring the existing one-task-one-atomic-commit policy, which this approach is explicitly designed not to conflict with.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 docs/task-commit-policy.md (or a new docs/testing-policy.md linked from it and from the task-execution instructions) states the TDD evidence requirement in writing: write the test, run it and record the failing output with the reason it fails, implement the minimal code to pass it, run it again and record the passing output
- [ ] #2 The policy explicitly scopes this to new tests added going forward, not retroactively to the existing ~146 tests, and explicitly states it does not require splitting a task's atomic commit into multiple commits
- [ ] #3 The policy states where the red/green evidence must be recorded (Backlog task Implementation Notes, consistent with this project's existing evidence-gated finalization convention) and that a task finalizer (human or agent) should treat missing red/green evidence as a reason to withhold the Done status, not as an optional nicety
- [ ] #4 The policy explicitly distinguishes this requirement from criterion 3/5 of the prior test-suite audit (minimal-implementation-first delivery order and physical-invariant test balance), which already have strong evidence and need no new policy
- [ ] #5 backlog instructions task-execution (or its referenced guide) is updated to point to the new TDD evidence requirement so a future task picks it up without the operator having to repeat it
<!-- AC:END -->
