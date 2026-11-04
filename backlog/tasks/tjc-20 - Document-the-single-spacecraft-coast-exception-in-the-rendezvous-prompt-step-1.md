---
id: TJC-20
title: >-
  Document the single-spacecraft coast exception in the /rendezvous prompt step
  1
status: Done
assignee:
  - '@anna'
created_date: '2026-11-04 20:03'
updated_date: '2026-11-04 20:04'
labels:
  - docs
dependencies: []
priority: low
type: task
ordinal: 71000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The formalizer correctly returns OUT OF SCOPE for a single-spacecraft inertial-Cartesian coast request, but step 1 of .pi/prompts/rendezvous.md said to halt on anything not READY TO SOLVE. That contradicted the committed case_c_two_body precedent and reference/SOURCE.md Sec C, which route such a request straight to the bounded two-body coast skill. This was an uncommitted edit in the working tree; this task records it as its own atomic commit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Step 1 of .pi/prompts/rendezvous.md states that a single-spacecraft inertial-Cartesian coast request proceeds to the orbital-two-body-rendezvous skill via step 2 despite the formalizer returning OUT OF SCOPE
- [x] #2 Every other NEEDS CLARIFICATION or out-of-scope case still stops at step 1
- [x] #3 Only .pi/prompts/rendezvous.md and this task file are in the commit
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Commit the existing step-1 edit in .pi/prompts/rendezvous.md as-is. 2. Verify it against case_c_two_body.json and reference/SOURCE.md Sec C. 3. Stage only the prompt and this task file.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Doc-only change to prompt text; no code or tests touched, so no new pytest (testing policy N/A). AC1/AC2 verified by reading the diff against case_c_two_body.json _comment and reference/SOURCE.md Sec C. Not changed: AGENTS.md standing rule still says to halt on any non-READY TO SOLVE result; it should be reconciled in a follow-up if desired. Staged only this prompt and task file; SESSION_SUMMARY and TJC-19 files left untouched.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Committed the existing step-1 edit to .pi/prompts/rendezvous.md: single-spacecraft inertial coast requests proceed to the two-body skill despite the formalizer returning OUT OF SCOPE; all other non-READY cases still stop. Verified by diff review against the case_c precedent and SOURCE.md Sec C.
<!-- SECTION:FINAL_SUMMARY:END -->
