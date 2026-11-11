---
id: TJC-21.1
title: >-
  Phase 1: Define the saved-run format and capture Demo A, B and C as stored
  runs
status: To Do
assignee: []
created_date: '2026-11-10 13:37'
updated_date: '2026-11-10 13:52'
labels:
  - web-demo
dependencies: []
documentation:
  - docs/web-demo-cases.md
parent_task_id: TJC-21
priority: high
type: feature
ordinal: 73000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Both the static Pages replay and the later live backend must render the same data, so the format has to be fixed first. The first stored runs are three owner-supplied demo cases in docs/web-demo-cases.md: Demo A (one period, expected NUMERICAL_DISAGREEMENT), Demo B (quarter period, expected VERIFIED) and Demo C (single-spacecraft two-body coast, expected VERIFIED). Together they cover a failure shown honestly, a pass, and the two-body path where the plot stages are not_generated. Developer mode needs raw agent events, so they must be stored, but keys and machine-specific paths must not leak into saved files that get published.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented schema covers ordered steps, per-step status, artifact paths and metadata, structured results, raw agent events and tool calls, and an optional stop state with an optional continuation
- [ ] #2 The schema reuses the existing statuses and failure modes from src/gmat_verify.py and src/verification_report.py and adds no new vocabulary
- [ ] #3 A not_generated stage is representable with its reason
- [ ] #4 A redaction step removes API keys and absolute machine paths from stored runs, with a test that fails if either appears
- [ ] #5 Demo A, B and C are each captured as a stored run from a real pipeline run using the exact request text in docs/web-demo-cases.md; the stored outcome is what the pipeline actually returned
- [ ] #6 Demo A and B include the 3D scene, trajectory plot, comparison plots and GMAT screenshot; Demo C records its not_generated plot stages with their reasons
- [ ] #7 Any difference between an expected outcome in docs/web-demo-cases.md and the actual result is recorded in the task notes
- [ ] #8 Tests validate all three stored runs against the schema
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
- [ ] #3 Project owner has opened the stored-run files for Demo A, B and C and confirmed the plots and values are correct before the task is marked Done
<!-- DOD:END -->
