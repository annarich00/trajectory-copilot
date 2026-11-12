---
id: TJC-21.3
title: 'Phase 1: Write the fixed operator-mode templates for each pipeline step'
status: To Do
assignee: []
created_date: '2026-11-10 13:37'
updated_date: '2026-11-12 13:35'
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
- [ ] #1 There is one template per step: formalizer, model selector, 3D scene, trajectory and burns plot, GMAT verification, comparison plots, GMAT screenshot, and final summary
- [ ] #2 A not_generated stage and each GMAT failure mode have a template that shows the status and reason and does not substitute another plot
- [ ] #3 Template wording is reviewed by the project owner before the task is closed
- [ ] #4 Tests render every template from Demo A, B and C and fail on any unfilled placeholder
- [ ] #5 Templates take numbers and statuses only from stored-run data, with no hard-coded values from any one demo case
- [ ] #6 Tests render every template from Demo A, B and C and fail on any unfilled placeholder
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
- [ ] #3 Project owner has read a rendered preview of every template filled from Demo A, B and C (no page exists yet) and approved the wording before the task is marked Done
<!-- DOD:END -->
