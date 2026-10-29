---
id: TJC-15
title: >-
  Wire the GMAT tool call into the GMAT-example subagent review before reporting
  the final result
status: To Do
assignee: []
created_date: '2026-10-28 13:34'
labels: []
dependencies:
  - TJC-12
  - TJC-14
priority: low
type: feature
ordinal: 59000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fourth of the four classmate-brainstormed workflow additions, and the piece that connects the other three. Once the GMAT execution tool (separate task) and the GMAT-example review subagent (separate task) both exist independently, this task sequences them: after the main workflow agent calls the GMAT execution tool and gets a numerical/screenshot verification result, it hands the generated GMAT script and mission context to the GMAT-example subagent for a formatting/convention review, then incorporates that subagent's verdict into what it reports back to the user -- before declaring the result 'VERIFIED.' This is an additive step in .pi/prompts/rendezvous.md (a new step between the existing steps 3 and 4), not a replacement for the numerical verification contract: a 'divergent formatting' verdict from the subagent must never override or be confused with a PASS/FAIL numerical result from src/gmat_verify.py.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 .pi/prompts/rendezvous.md gains an explicit step (sequenced after the GMAT tool call, before the final outcome report) that hands the generated script and mission type to the GMAT-example subagent and requires reporting its verdict alongside, not instead of, the numerical VERIFIED/FAIL outcome
- [ ] #2 The subagent's formatting verdict is clearly labeled as advisory/stylistic in the final report and cannot change a FAIL to VERIFIED or a VERIFIED to FAIL on its own
- [ ] #3 If the GMAT-example subagent is unavailable or errors, the workflow still completes and reports the numerical verification result, with the formatting review explicitly noted as skipped/unavailable rather than blocking the whole result
- [ ] #4 A worked end-to-end example (one real or recorded run) shows the full chain: natural-language request -> formalizer -> model selector -> GMAT execution tool call -> GMAT-example subagent review -> final combined report
- [ ] #5 No change is made to the numerical PASS/WARNING/FAIL/INCOMPLETE logic already defined in src/gmat_verify.py or src/verification_report.py
<!-- AC:END -->
