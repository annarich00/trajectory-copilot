# Test-first (TDD) evidence policy

This policy extends the project's existing evidence-gated task-finalization
convention (see `backlog instructions task-finalization`: acceptance
criteria are checked only after objective verification evidence proves the
behavior, not from code presence or intent alone). It adds a specific
evidence requirement for test-first development.

## The requirement

For every **new** automated test added under this policy, record two pytest
runs as evidence:

1. **Red.** Write the test first. Run it before the corresponding
   implementation code exists, and record the failing output together with
   the reason it fails (e.g. `AttributeError: module has no attribute ...`,
   assertion mismatch, missing function). The failure must demonstrate the
   test actually exercises the intended behavior, not an unrelated error
   (import typo, syntax error, etc.).
2. **Green.** Implement the minimal code needed to make the test pass. Run
   the test again and record the passing output.

Both runs must be recorded before the task that introduces the test can be
finalized.

## Scope

- This requirement applies **only to new tests added going forward** from
  the adoption of this policy. It is **not retroactive**: the ~146 tests
  already in this repository's test suite are not required to be
  re-derived, re-justified, or backfilled with red/green evidence.
- This requirement **does not change** the one-task-one-atomic-commit
  policy. See `docs/task-commit-policy.md` for that policy, which remains
  unchanged: a task that adds a new test and its implementation still ends
  as a single atomic commit. Running the test twice (red, then green) is an
  evidence-gathering step during implementation, not a commit boundary.

## Where to record the evidence

Record the red and green run output in the Backlog task's **Implementation
Notes**, using the project's standard append-notes workflow, e.g.:

```bash
backlog task edit <task-id> --append-notes "Red: pytest tests/test_x.py::test_new_behavior -> FAILED (AttributeError: ...). Green: pytest tests/test_x.py::test_new_behavior -> PASSED."
```

This is consistent with this project's existing evidence-gated
finalization convention: Implementation Notes are for progress, decisions,
and validation details, and acceptance criteria/Definition of Done items
are checked only after objective verification evidence proves the
behavior. A task finalizer (human or agent) checking acceptance criteria or
Definition of Done items that involve a new test must treat **missing
red/green evidence in the Implementation Notes as a reason to withhold the
Done status**, not as an optional nicety to skip under time pressure.

## Relationship to the prior test-suite audit

TJC-5's own description references a prior test-suite audit with multiple
criteria, including delivery order (implementing minimally before adding
tests) and physical-invariant test balance. Those two concerns already have
strong evidence in this repo and are **not** addressed by this document;
no new policy is needed for them here. This document is narrowly scoped to
one specific gap the audit found: the absence of any recorded red-then-green
evidence for new tests. It does not attempt to codify or re-litigate the
other audit criteria, and should not be read as expanding beyond the
red/green recording cycle described above.
