---
id: TJC-14
title: >-
  Define a GMAT-example subagent that reviews generated scripts against the
  open-source corpus
status: To Do
assignee: []
created_date: '2026-10-28 13:34'
labels: []
dependencies:
  - TJC-11
priority: low
type: feature
ordinal: 58000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Third of the four classmate-brainstormed workflow additions. Define a project-local pi subagent (.pi/agents/gmat-example-reviewer.md, discoverable via the subagent tool's agentScope, see docs/extensions.md's subagent example and the 'both'/'project' agentScope setting) whose system prompt establishes it as a GMAT scripting expert. Its job: given (a) a generated GMAT script from this project's own pipeline (src/gmat_verify.py::generate_gmat_script / generate_two_body_coast_script / generate_gmat_gui_preview_script output) and (b) the original user request's mission type, consult the structured corpus file produced by TJC-11 and report whether the generated script's formatting/structure/conventions are satisfactory or how they diverge from established open-source practice for that mission type. This subagent reviews formatting/structure/convention quality only -- it is explicitly not a numerical verifier and must not be confused with or substitute for the existing GMAT numerical/screenshot verification contract in .pi/skills/gmat-rendezvous-verification/SKILL.md, which remains the sole source of PASS/FAIL numerical truth.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A project-local agent definition file exists with a system prompt scoping it strictly to GMAT script formatting/structure/convention review, explicitly stating it does not perform or replace numerical/screenshot verification
- [ ] #2 The agent's instructions require it to load and cite the specific corpus entries (from TJC-11's file) it is comparing against, rather than giving an unsourced opinion
- [ ] #3 The agent's instructions require it to state explicitly when the corpus has no entry for the requested mission type, rather than fabricating a comparison
- [ ] #4 The agent's output format is a short structured verdict (satisfactory / divergent, with the specific divergences named and the corpus entries referenced) usable as text in the main agent's own output or report
- [ ] #5 A documented example run (real or recorded) shows the subagent reviewing at least one of this project's own already-generated GMAT scripts (e.g. examples/cw_gmat_slice_example/generated_cw_rendezvous.script) against the corpus
<!-- AC:END -->
