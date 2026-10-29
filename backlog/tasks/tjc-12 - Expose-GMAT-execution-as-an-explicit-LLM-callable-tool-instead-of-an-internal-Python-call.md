---
id: TJC-12
title: >-
  Expose GMAT execution as an explicit LLM-callable tool instead of an internal
  Python call
status: To Do
assignee: []
created_date: '2026-10-28 13:33'
labels: []
dependencies: []
priority: low
type: feature
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A classmate brainstorming session proposed four workflow additions; this is the first. Today GMAT execution happens entirely inside Python (src/gmat_verify.py::run_gmat_script / attempt_gmat_gui_screenshot, called from src/workflow.py and scripts/run_cw_gmat_slice.py) -- the LLM driving a session never sees or decides to invoke GMAT directly, it only sees the eventual verification_result.json. The operator wants GMAT execution registered as a genuine pi tool (via a project-local extension's pi.registerTool(), see docs/extensions.md) so the agent explicitly calls it as a discrete, auditable step in the transcript, rather than it happening invisibly inside run_rendezvous_workflow. This must not duplicate or fork the existing GMAT execution logic in src/gmat_verify.py -- the tool is a thin wrapper around the already-audited functions there, not a reimplementation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A project-local pi extension (.pi/extensions/) registers a tool (e.g. 'run_gmat_verification') that wraps the existing src/gmat_verify.py execution/parsing/comparison functions without duplicating their logic
- [ ] #2 The tool's input schema requires the same structured case information src/workflow.py already requires (script/case identity, tolerances) rather than accepting free-text
- [ ] #3 The tool's output surfaces the same PASS/WARNING/FAIL/INCOMPLETE/MISSING_GMAT distinctions already defined in src/gmat_verify.py and src/verification_report.py, with no new silent-PASS path introduced
- [ ] #4 src/workflow.py::run_rendezvous_workflow continues to work unchanged for any caller that does not go through the new tool (the tool is additive, not a required refactor of the existing function-call path)
- [ ] #5 .pi/prompts/rendezvous.md is updated to reference the new tool explicitly in its step 3 so a session following that prompt actually uses it
- [ ] #6 A test (or documented manual verification) confirms the tool is discoverable and callable in a pi session, and that calling it reaches a real or stand-in GMAT result consistent with the existing test patterns in tests/test_cw_gmat_slice.py / tests/test_workflow.py
<!-- AC:END -->
