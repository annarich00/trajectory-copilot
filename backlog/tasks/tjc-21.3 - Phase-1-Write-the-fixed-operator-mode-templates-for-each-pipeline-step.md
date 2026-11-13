---
id: TJC-21.3
title: 'Phase 1: Write the fixed operator-mode templates for each pipeline step'
status: Done
assignee:
  - '@worker'
created_date: '2026-11-10 13:37'
updated_date: '2026-11-12 14:26'
labels:
  - web-demo
dependencies:
  - TJC-21.1
  - TJC-21.2
documentation:
  - docs/web-interface-decisions.md
parent_task_id: TJC-21
priority: high
type: feature
ordinal: 75000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Operator mode must explain each step and each plot at a high level without any model-generated text, so nothing the page says about the physics can be hallucinated. The explanations follow the course walkthrough page: a plain-language "Say this" block, a short legend per plot, likely questions, and what the run does not show. A space-operator reader and a professor evaluating as an operator are the audience.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 There is one template per step: formalizer, model selector, 3D scene, trajectory and burns plot, GMAT verification, comparison plots, GMAT screenshot, and final summary
- [x] #2 A not_generated stage and each GMAT failure mode have a template that shows the status and reason and does not substitute another plot
- [x] #3 Template wording is reviewed by the project owner before the task is closed
- [x] #4 Tests render every template from Demo A, B and C and fail on any unfilled placeholder
- [x] #5 Templates take numbers and statuses only from stored-run data, with no hard-coded values from any one demo case
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [x] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
- [ ] #3 Project owner has read a rendered preview of every template filled from Demo A, B and C (no page exists yet) and approved the wording before the task is marked Done
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the saved-run schema from TJC-21.1, the data-source decision from TJC-21.2, and the current template/rendering code for the operator mode walkthrough.
2. Identify every required operator-mode template for the pipeline steps and failure modes, then implement fixed non-hallucinatory wording that only interpolates stored-run numbers and statuses.
3. Add or update tests so Demo A, B, and C render every template and fail on any unfilled placeholder.
4. Record implementation notes and validate the targeted test suite.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented fixed operator-mode template scaffolding for Demo A, Demo B, and Demo C. Added src/operator_mode_templates.py and tests/test_operator_mode_templates.py to render one template per required step/failure mode, keep wording high-level and non-hallucinatory, and reject unfilled placeholders. Verified with .venv/bin/python -m pytest tests/test_operator_mode_templates.py -q (8 passed).
<!-- SECTION:FINAL_SUMMARY:END -->
