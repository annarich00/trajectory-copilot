---
id: TJC-1.26
title: Establish the initial Git checkpoint and atomic task-commit policy
status: Done
assignee:
  - '@annarich00'
created_date: '2026-10-02 14:10'
updated_date: '2026-10-02 14:33'
labels: []
dependencies:
  - TJC-1.1
modified_files:
  - AGENTS.md
  - docs/task-commit-policy.md
  - >-
    backlog/tasks/tjc-1.26 -
    Establish-the-initial-Git-checkpoint-and-atomic-task-commit-policy.md
parent_task_id: TJC-1
priority: high
type: chore
ordinal: 2050
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
This repository currently has no commits: the recovered baseline, completed TJC-1.1 record, scoped backlog, and project documentation are all untracked. Create the initial known-good checkpoint before further work, then document a policy that every subsequent task finishes as one discoverable atomic commit. TJC-1.1 predates this policy and is represented by this initial checkpoint rather than rewritten retroactively.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 An initial Git commit contains the recovered baseline, Backlog task structure, scope documents, setup files, and no caches, virtual environments, generated process artifacts, or secrets
- [x] #2 The initial commit subject begins `TJC-1.26:` and the working tree is clean immediately afterward
- [x] #3 Repository guidance documents the per-task sequence: start from a clean tree, isolate task changes, run tests and site checks, finalize Backlog metadata, create or amend to one task commit, and finish clean
- [x] #4 The policy requires commit subjects to begin with the exact task ID so each completed task is discoverable through Git history
- [x] #5 The policy explains that task-finalization metadata must be amended into the same task commit rather than added as a separate bookkeeping commit
- [x] #6 Parallel work is required to use isolated branches/worktrees so each task commit remains independently reviewable and revertible
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #2 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #3 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #4 Record this pre-site checkpoint in repository policy/documentation; TJC-1.25 must backfill its task/commit entry when the living progress page is established.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Audit the recovered untracked baseline and ignore rules for caches, generated artifacts, credentials, and secrets.
2. Add narrowly scoped repository guidance documenting the atomic per-task commit workflow and this pre-site checkpoint.
3. Run the recovered baseline tests and repository hygiene checks.
4. Create the initial TJC-1.26 task commit, finalize Backlog acceptance criteria/DoD and summary with objective evidence, then amend those metadata updates into the same commit.
5. Verify the final history contains one task commit and the working tree is clean.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added docs/task-commit-policy.md and linked it from AGENTS.md. The policy requires clean starts and finishes, one task per atomic commit, exact `<task-id>:` subject prefixes, relevant tests and site checks, finalized Backlog metadata in the task commit, amend rather than bookkeeping commits, and isolated branches/worktrees for parallel tasks. It records this as the pre-site checkpoint representing TJC-1.1 and assigns living-progress backfill to TJC-1.25.

Baseline validation: the initial `python3 -m pytest -q` attempt could not run because system Python lacked pytest (`No module named pytest`). With supervisor approval, created ignored `.venv`, installed exactly `requirements-dev.txt`, and ran `.venv/bin/python -m pytest -q`: 6 passed in 0.22s on final pre-finalization rerun (initial isolated run: 6 passed in 0.25s). `git diff --check` passed. Secret-pattern and forbidden tracked-artifact scans passed. `.venv/`, `.pytest_cache/`, `__pycache__/`, and bytecode remain ignored and untracked. The initial commit contained 57 intended recovered-baseline, Backlog, scope, setup, source, test, evaluation, example, reference, and policy files; no educational site was imported.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Established the initial known-good repository checkpoint and atomic task-commit policy. Preserved the recovered baseline and Backlog planning, documented exact task-ID commit subjects, same-commit Backlog finalization by amend, clean-tree verification, tests/site checks, and branch/worktree isolation. Verified 6 baseline tests pass, repository whitespace and hygiene checks pass, generated environments/caches remain excluded, and the single commit subject begins `TJC-1.26:`. TJC-1.25 remains responsible for backfilling this checkpoint into the future living progress page.
<!-- SECTION:FINAL_SUMMARY:END -->
