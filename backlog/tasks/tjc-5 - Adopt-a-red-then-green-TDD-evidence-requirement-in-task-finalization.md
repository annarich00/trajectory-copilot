---
id: TJC-5
title: Adopt a red-then-green TDD evidence requirement in task finalization
status: Done
assignee:
  - '@pi'
created_date: '2026-10-19 12:16'
updated_date: '2026-11-02 03:09'
labels: []
dependencies: []
priority: high
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A test-suite audit (prompted by the operator, scoped to this repo, read-only) found no textual or process evidence of test-first discipline: every inspected Backlog task implementation plan lists "implement X" before "add tests for X", and no doc anywhere states a TDD expectation. The operator decided on an enforcement approach (Option B from that audit discussion): extend the existing evidence-gated finalization convention (tasks already require exact command/output evidence before Done) to require two recorded pytest runs for any new test added under this policy -- one showing the new test failing for the stated reason before the corresponding implementation code exists (red), and one showing it passing afterward (green) -- rather than restructuring the existing one-task-one-atomic-commit policy, which this approach is explicitly designed not to conflict with.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 docs/task-commit-policy.md (or a new docs/testing-policy.md linked from it and from the task-execution instructions) states the TDD evidence requirement in writing: write the test, run it and record the failing output with the reason it fails, implement the minimal code to pass it, run it again and record the passing output
- [x] #2 The policy explicitly scopes this to new tests added going forward, not retroactively to the existing ~146 tests, and explicitly states it does not require splitting a task's atomic commit into multiple commits
- [x] #3 The policy states where the red/green evidence must be recorded (Backlog task Implementation Notes, consistent with this project's existing evidence-gated finalization convention) and that a task finalizer (human or agent) should treat missing red/green evidence as a reason to withhold the Done status, not as an optional nicety
- [x] #4 The policy explicitly distinguishes this requirement from criterion 3/5 of the prior test-suite audit (minimal-implementation-first delivery order and physical-invariant test balance), which already have strong evidence and need no new policy
- [x] #5 backlog instructions task-execution (or its referenced guide) is updated to point to the new TDD evidence requirement so a future task picks it up without the operator having to repeat it
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-5:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented via subagent (worker) in isolated git worktree/branch tjc-5:
- Created docs/testing-policy.md: states the red-then-green TDD evidence requirement (write test -> run and record failing output with the reason it fails -> implement minimal code -> run and record passing output); explicitly scopes it to new tests only (not retroactive to the existing ~146-test suite) and explicitly states it does not require splitting the existing one-task-one-atomic-commit policy; states the evidence must be recorded in Backlog task Implementation Notes via --append-notes, and that a finalizer must treat missing red/green evidence as a reason to withhold Done status; and distinguishes this narrow requirement from the prior test-suite audit's other criteria (delivery order, physical-invariant balance), which already have strong evidence and are explicitly out of scope here.
- Added a 'Related policy' cross-reference section to docs/task-commit-policy.md pointing to the new doc.
- Added a 'Test-first (TDD) evidence' section to AGENTS.md, modeled on the existing 'Git task commits' section, pointing to docs/testing-policy.md -- resolving AC5: backlog instructions task-execution's text is hardcoded inside the compiled cli.js of the globally-installed backlog.md npm package (confirmed via which backlog -> .../backlog.md/cli.js, a compiled binary, not a plain editable file; no backlog/ config or plain-text source exists for that guide's content in this repo), so it is NOT directly editable -- per the task's own explicit fallback instruction, the pointer was added to AGENTS.md instead (read at the start of every session per its own <CRITICAL_INSTRUCTION> block).
Verification: .venv/bin/python -m pytest tests/ -q -> 152 passed, zero regressions (expected: documentation-only change, no src/scripts/tests content touched).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Adopted a red-then-green TDD evidence requirement for new tests going forward, documented in the new docs/testing-policy.md: write the test, run and record the failing output with its reason, implement the minimal code, run and record the passing output. Explicitly non-retroactive (does not apply to the existing ~146 tests) and does not split the existing one-task-one-atomic-commit policy. Evidence is recorded in Backlog task Implementation Notes; a finalizer must withhold Done status if that evidence is missing. Cross-referenced from docs/task-commit-policy.md and from a new AGENTS.md section (since backlog instructions task-execution's text is compiled into the installed backlog.md CLI binary and is not directly editable). Verified with the full test suite (152/152 passing, documentation-only change).
<!-- SECTION:FINAL_SUMMARY:END -->
