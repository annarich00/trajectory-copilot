---
id: TJC-10
title: >-
  Research and collect open-source GMAT mission-script examples from the
  internet
status: To Do
assignee: []
created_date: '2026-10-28 13:33'
labels: []
dependencies: []
priority: low
type: task
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A classmate brainstorming session proposed a future GMAT-example subagent (see the planned follow-up task) that reviews this project's generated GMAT scripts (src/gmat_verify.py::generate_gmat_script / generate_two_body_coast_script / generate_gmat_gui_preview_script) against real-world open-source GMAT usage, so it can tell the workflow agent whether its formatting/structure matches established practice for the request's mission type. That subagent needs a corpus to draw from. This task is the research step only: search the internet for open-source GMAT script examples (the official GMAT repository's sample missions, GMAT wiki/tutorial scripts, university/lab astrodynamics course repositories, and any other clearly-licensed public GMAT .script examples), across multiple mission types/formatting conventions (not just CW rendezvous), and collect them with enough provenance to reuse later. This task does not build the subagent-readable file itself (that is the next task) and does not change any code in src/ or scripts/.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A written list/log of at least 10 distinct open-source GMAT script examples is produced, spanning more than one mission type (e.g. not all rendezvous) and more than one source repository
- [ ] #2 Each collected example records its source URL, license (or explicit 'license unknown/unclear' when not determinable), and a short description of what the script demonstrates
- [ ] #3 Raw collected script text/files are saved under a clearly labeled research-staging location (e.g. research/gmat_examples_raw/) distinct from this project's own authoritative src/ and examples/ directories, so there is no ambiguity about what is this project's own code versus externally sourced reference material
- [ ] #4 Sources with no discoverable license or an incompatible license are flagged explicitly rather than silently included, so the next task can decide what is safe to redistribute inside this repository
- [ ] #5 No existing src/, scripts/, tests/, or examples/ file is modified by this task
<!-- AC:END -->
