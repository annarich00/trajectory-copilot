---
id: TJC-16.5
title: Display visualization artifacts live as the rendezvous pipeline runs
status: To Do
assignee: []
created_date: '2026-10-30 16:39'
updated_date: '2026-11-02 02:06'
labels: []
dependencies:
  - TJC-16.2
  - TJC-16.3
  - TJC-16.4
parent_task_id: TJC-16
priority: medium
type: feature
ordinal: 66000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The operator wants to demo this live to their advisor and see each visualization pull up progressively as the agent works through the rendezvous pipeline (formalize -> model-select -> solve -> GMAT verify), not just receive a bundle of artifact paths at the very end. This wires the already-produced plots (TJC-16.2 3D relative-position scene, TJC-16.3 trajectory/burns plot, TJC-16.4 verification comparison plot) into the existing .pi/prompts/rendezvous.md pipeline and src/workflow.py::run_rendezvous_workflow so each artifact is generated and surfaced as soon as its underlying stage completes, ending with the already-existing GMAT GUI screenshot/execution step.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 src/workflow.py::run_rendezvous_workflow (or a thin wrapper used by .pi/prompts/rendezvous.md) generates the TJC-16.2 3D relative-position scene immediately after problem formalization/model selection, before the CW/two-body solve runs, using the formalized initial/target relative state
- [ ] #2 The TJC-16.3 trajectory/burns plot is generated immediately after the deterministic CW or two-body solve completes and before GMAT execution begins, not deferred to the end of the run
- [ ] #3 The TJC-16.4 verification comparison plot is generated immediately after GMAT execution and parsing complete, using the same run's GMAT report output
- [ ] #4 .pi/prompts/rendezvous.md is updated so each stage's newly generated artifact path is reported to the operator as soon as it is produced, in pipeline order, rather than only in the final step-4 summary, while preserving every existing required step/order/wording constraint already in that prompt
- [ ] #5 The final stage of the displayed sequence remains the existing GMAT execution and GUI screenshot/preview-script handoff already defined in run_rendezvous_workflow and rendezvous.md step 5, unchanged by this task
- [ ] #6 A test or recorded manual run demonstrates all four artifacts (3D scene, trajectory/burns plot, verification comparison plot, GMAT screenshot) are produced and reported in pipeline order for one real end-to-end case
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed 'TJC-16.5:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->
