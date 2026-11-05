---
id: TJC-14
title: >-
  Define a GMAT-example subagent that reviews generated scripts against the
  open-source corpus
status: Done
assignee:
  - '@worker'
created_date: '2026-10-28 13:34'
updated_date: '2026-11-05 17:06'
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
- [x] #1 A project-local agent definition file exists with a system prompt scoping it strictly to GMAT script formatting/structure/convention review, explicitly stating it does not perform or replace numerical/screenshot verification
- [x] #2 The agent's instructions require it to load and cite the specific corpus entries (from TJC-11's file) it is comparing against, rather than giving an unsourced opinion
- [x] #3 The agent's instructions require it to state explicitly when the corpus has no entry for the requested mission type, rather than fabricating a comparison
- [x] #4 The agent's output format is a short structured verdict (satisfactory / divergent, with the specific divergences named and the corpus entries referenced) usable as text in the main agent's own output or report
- [x] #5 A documented example run (real or recorded) shows the subagent reviewing at least one of this project's own already-generated GMAT scripts (e.g. examples/cw_gmat_slice_example/generated_cw_rendezvous.script) against the corpus
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-14:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Write tests/test_gmat_example_reviewer_agent.py (static checks of .pi/agents/gmat-example-reviewer.md: frontmatter parses, read-only tools, scope/non-verification, corpus path + must-cite, no-entry statement, verdict format) and record RED (agent file absent).
2. Create .pi/agents/gmat-example-reviewer.md (project-local pi-subagents agent; read-only tools read/grep/find/ls; references research/gmat_example_corpus/corpus.json; scoped to format/structure/convention review; never quotes non-redistributable entries) and record GREEN.
3. Regenerate a generated_cw_rendezvous.script via src/gmat_verify.py::generate_gmat_script (same inputs as examples/cw_gmat_vertical_slice.yaml), run the agent against it (real subagent run if possible, else clearly labelled manual/recorded), and save the result in docs/gmat-example-reviewer-example-run.md with honest provenance.
4. Run full pytest; finalize Backlog (AC/DoD, notes, summary, Done); single commit 'TJC-14: ...' via amend.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
RED (before agent file existed): .venv/bin/python -m pytest tests/test_gmat_example_reviewer_agent.py -q -> 9 errors in 0.10s; every test errors in the 'agent' fixture with AssertionError: missing project-local agent definition: .pi/agents/gmat-example-reviewer.md (the intended behaviour is absent, not an import/syntax error).

GREEN (after creating .pi/agents/gmat-example-reviewer.md): .venv/bin/python -m pytest tests/test_gmat_example_reviewer_agent.py -q -> 9 passed in 0.05s. With tests/test_gmat_example_corpus.py and tests/test_skill_authority_boundaries.py: 42 passed in 0.13s.

Full suite (shared venv from main checkout lacks hypothesis/plotly): pytest -q --continue-on-collection-errors -> 173 passed, 1 failed, 9 collection errors. The 9 collection errors (ModuleNotFoundError hypothesis/plotly) are identical with my changes stashed, so pre-existing/environmental. The 1 failure (tests/test_cw_gmat_slice.py::test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window) is a load-flaky real-Xvfb GUI test: it passes alone both with my changes (1 passed in 18.07s) and with them stashed (1 passed in 18.14s).

Design: agent is read-only (tools: read, grep, find, ls), systemPromptMode replace, inheritProjectContext/Skills false; references research/gmat_example_corpus/corpus.json + SCHEMA.md, refers PASS/FAIL authority to .pi/skills/gmat-rendezvous-verification/SKILL.md, forbids quoting non-redistributable entries, verdict block SATISFACTORY|DIVERGENT|NO CORPUS ENTRY. Not wired into workflow/rendezvous prompt (TJC-15).

AC5 example run: docs/gmat-example-reviewer-example-run.md. Reviewed script examples/cw_gmat_slice_example/generated_cw_rendezvous.script from a real scripts/run_cw_gmat_slice.py run (GMAT verified: pos err 7.94e-3 m). Reviewer outputs are REAL model runs (openai/gpt-5.4-mini) via 'pi -p' with the agent body as --system-prompt and its tool allowlist, NOT via the subagent tool (headless pi -p exposed no subagent tool: model answered 'NO SUBAGENT TOOL'); frontmatter-driven discovery not exercised. Run A (mission type CW rendezvous) -> NO CORPUS ENTRY; Run B (orbit_transfer) -> DIVERGENT citing nasa-ex_hohmanntransfer, nasa-tut_simpleorbittransfer.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the project-local read-only subagent .pi/agents/gmat-example-reviewer.md (format/structure/convention review only; defers PASS/FAIL numerical truth to the gmat-rendezvous-verification skill; must load and cite corpus.json entry ids; must answer NO CORPUS ENTRY rather than fabricate; short SATISFACTORY/DIVERGENT verdict block), tests/test_gmat_example_reviewer_agent.py (9 static tests, red-then-green recorded), docs/gmat-example-reviewer-example-run.md with an honestly labelled example run (real model runs with the agent prompt via pi -p, not the subagent tool) against examples/cw_gmat_slice_example/generated_cw_rendezvous.script. Verified: new tests 9 passed; wider suite 173 passed with only pre-existing env collection errors and one load-flaky GUI test that passes alone.
<!-- SECTION:FINAL_SUMMARY:END -->
