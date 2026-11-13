---
id: TJC-21.2
title: >-
  Phase 1: Decide how operator templates get structured data from the formalizer
  and model selector
status: Done
assignee:
  - '@worker'
created_date: '2026-11-10 13:37'
updated_date: '2026-11-13 19:47'
labels:
  - web-demo
dependencies:
  - TJC-21.1
documentation:
  - docs/web-interface-decisions.md
parent_task_id: TJC-21
priority: high
type: task
ordinal: 74000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GMAT results and artifact paths are already JSON, but the orbital-problem-formalizer and orbital-model-selector produce Markdown prose. Operator mode uses fixed templates filled with real values, so it needs reliable fields from those two steps (or an agreed fallback). The choice affects skills that have benchmark evaluations under evaluations/, so it needs an explicit decision before templates are written.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A recorded decision chooses between parsing the Markdown output and having the skills also emit a structured block, with the reason
- [ ] #2 If skills change, the evaluations under evaluations/ still pass and the formalizer and selector output sections remain unchanged
- [ ] #3 The chosen approach extracts the values operator templates need from Demo A, B and C and from at least one NEEDS CLARIFICATION result
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed with this task ID and a colon) contains this task implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
- [ ] #2 New tests have red-then-green evidence recorded in the task notes, per docs/testing-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review TJC-21.1 stored-run schema and TJC-23 tool-based pipeline outputs to identify exactly which structured fields operator templates need from the formalizer and model selector. 2. Decide whether operator templates should parse Markdown or consume an explicit structured block emitted by the skills/tools, keeping the decision aligned with current TJC-21 web-demo decisions and existing saved-run schema. 3. Record the decision and rationale in task notes/backlog metadata without starting TJC-21.3 or later work.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Decision recorded: keep the formalizer and model selector outputs as Markdown prose for now, and have operator templates read structured values from the saved-run contract captured in TJC-21.1 plus the existing tool-based pipeline artifacts. Rationale: the current TJC-21 web-demo decisions explicitly require fixed templates and honest verbatim step text for the prose steps until a later phase decides on skill-output changes; TJC-23 already gives us auditable tool-based outputs without changing the skills' external prose contract. This avoids widening scope into a skill-output migration, preserves the evaluation surface from TJC-23, and lets TJC-21.3 write templates against a stable data contract. Verified against docs/web-interface-decisions.md and docs/web-demo-cases.md. No TJC-21.3+ work started.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Recorded the operator-template data-source decision for TJC-21.2: templates should not depend on changing the formalizer/model-selector prose contract now; instead, they should consume the structured saved-run fields established in TJC-21.1 and the auditable tool-based pipeline outputs from TJC-23, while showing the prose step text verbatim next to the template content until a later phase explicitly changes skill output. This keeps the task within the approved Phase-1 scope and leaves TJC-21.3 for template writing.
<!-- SECTION:FINAL_SUMMARY:END -->
