---
id: TJC-7
title: Decide and record whether to adopt uv for core project/dependency management
status: To Do
assignee: []
created_date: '2026-10-19 12:17'
labels: []
dependencies: []
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The same test-suite audit found this project uses plain venv/pip for its core environment (requirements-dev.txt, documented in README.md and docs/baseline-provenance.md), while uv is already used, but only inside the separate, intentionally isolated Poliastro verification environment (docs/poliastro-verification-architecture.md). A sibling project (the Figure 4 reproduction, pushed to the operator's annarich00 dev-log repo under figure4/) already uses uv + pyproject.toml + uv.lock as its convention. This is not a correctness defect -- the current pip/venv setup works and is fully documented -- but it is an undeclared tooling-convention inconsistency across the operator's own projects that was never explicitly decided one way or the other for the core Trajectory CoPilot repo. This task is a decision-and-documentation task first; it does not presume the outcome is to switch.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented decision exists (in docs/, e.g. a short docs/uv-adoption-decision.md, or an explicit section added to README.md) stating either: (a) adopt uv for the core project going forward, converting requirements-dev.txt to a pyproject.toml plus uv.lock and updating every documented clean-checkout command in README.md and docs/baseline-provenance.md accordingly; or (b) keep plain venv/pip for the core project intentionally, with the specific reason recorded (for example: keeping the core runtime decoupled from the separate isolated-uv-managed Poliastro environment's tooling, or minimizing churn this late in the semester) rather than leaving the inconsistency unaddressed and undocumented
- [ ] #2 If the decision is to adopt uv (option a), every existing documented reproduction command across README.md, docs/baseline-provenance.md, and any Backlog task implementation notes that reference the old .venv/bin/python -m pytest -q style command is updated consistently, and the full existing test suite still passes under the new uv-managed environment with zero regressions
- [ ] #3 If the decision is to keep pip/venv (option b), docs/poliastro-verification-architecture.md's existing uv usage for the isolated Poliastro environment is left completely unaffected either way, and the recorded decision explicitly cross-references it so a future reader understands why uv exists in one place in this repo but not the other, rather than appearing accidental
- [ ] #4 The decision and its rationale are reachable from README.md's main setup section, not buried only in a Backlog task file, so a new contributor encounters it without searching Backlog history
<!-- AC:END -->
