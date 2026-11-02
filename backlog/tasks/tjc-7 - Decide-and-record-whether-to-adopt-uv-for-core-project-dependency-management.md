---
id: TJC-7
title: Decide and record whether to adopt uv for core project/dependency management
status: Done
assignee:
  - '@pi'
created_date: '2026-10-19 12:17'
updated_date: '2026-11-02 03:12'
labels: []
dependencies: []
ordinal: 52000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The same test-suite audit found this project uses plain venv/pip for its core environment (requirements-dev.txt, documented in README.md and docs/baseline-provenance.md), while uv is already used, but only inside the separate, intentionally isolated Poliastro verification environment (docs/poliastro-verification-architecture.md). A sibling project (the Figure 4 reproduction, pushed to the operator's annarich00 dev-log repo under figure4/) already uses uv + pyproject.toml + uv.lock as its convention. This is not a correctness defect -- the current pip/venv setup works and is fully documented -- but it is an undeclared tooling-convention inconsistency across the operator's own projects that was never explicitly decided one way or the other for the core Trajectory CoPilot repo. This task is a decision-and-documentation task first; it does not presume the outcome is to switch.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A documented decision exists (in docs/, e.g. a short docs/uv-adoption-decision.md, or an explicit section added to README.md) stating either: (a) adopt uv for the core project going forward, converting requirements-dev.txt to a pyproject.toml plus uv.lock and updating every documented clean-checkout command in README.md and docs/baseline-provenance.md accordingly; or (b) keep plain venv/pip for the core project intentionally, with the specific reason recorded (for example: keeping the core runtime decoupled from the separate isolated-uv-managed Poliastro environment's tooling, or minimizing churn this late in the semester) rather than leaving the inconsistency unaddressed and undocumented
- [x] #2 If the decision is to adopt uv (option a), every existing documented reproduction command across README.md, docs/baseline-provenance.md, and any Backlog task implementation notes that reference the old .venv/bin/python -m pytest -q style command is updated consistently, and the full existing test suite still passes under the new uv-managed environment with zero regressions
- [x] #3 If the decision is to keep pip/venv (option b), docs/poliastro-verification-architecture.md's existing uv usage for the isolated Poliastro environment is left completely unaffected either way, and the recorded decision explicitly cross-references it so a future reader understands why uv exists in one place in this repo but not the other, rather than appearing accidental
- [x] #4 The decision and its rationale are reachable from README.md's main setup section, not buried only in a Backlog task file, so a new contributor encounters it without searching Backlog history
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-7:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented via subagent (worker) in isolated git worktree/branch tjc-7:
- Decision: keep plain venv/pip for the core project (option b). Confirmed via real evidence: uv is installed in this sandbox but the core .venv's pyvenv.cfg shows it was created with plain venv (no 'uv = <version>' field); requirements-dev.txt is small, flat, and unpinned with no documented pain points; the only in-repo uv precedent (Poliastro verifier) exists to pin a legacy Python 3.10 interpreter for an archived EOL dependency stack, a narrow problem that doesn't apply to the core project's current-runtime setup.
- Created docs/uv-adoption-decision.md: full decision record with evidence consulted, reasoning, and an explicit cross-reference to docs/poliastro-verification-architecture.md (left completely unmodified, confirmed via git diff).
- Added one line to README.md's setup section pointing to the new decision doc, satisfying the 'reachable from README's main setup section, not buried in Backlog' requirement.
Verification: .venv/bin/python -m pytest tests/ -q -> 152 passed, zero regressions (expected: documentation-only decision, no code touched since option (b) was chosen).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Decided to keep plain venv/pip for the core project (not adopt uv), recorded in the new docs/uv-adoption-decision.md with concrete evidence from this repo's current state: the core .venv was created with plain venv (confirmed via pyvenv.cfg), requirements-dev.txt has no documented pain points, and the project's only uv precedent (the isolated Poliastro verifier) solves a narrow legacy-interpreter-pinning problem that does not apply here. docs/poliastro-verification-architecture.md's existing uv usage is left completely unaffected and explicitly cross-referenced. README.md's setup section links to the decision doc. Verified with the full test suite (152/152 passing, documentation-only change).
<!-- SECTION:FINAL_SUMMARY:END -->
