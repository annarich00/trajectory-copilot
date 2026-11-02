---
id: TJC-12
title: >-
  Expose GMAT execution as an explicit LLM-callable tool instead of an internal
  Python call
status: Done
assignee:
  - '@agent'
created_date: '2026-10-28 13:33'
updated_date: '2026-11-02 20:17'
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
- [x] #1 A project-local pi extension (.pi/extensions/) registers a tool (e.g. 'run_gmat_verification') that wraps the existing src/gmat_verify.py execution/parsing/comparison functions without duplicating their logic
- [x] #2 The tool's input schema requires the same structured case information src/workflow.py already requires (script/case identity, tolerances) rather than accepting free-text
- [x] #3 The tool's output surfaces the same PASS/WARNING/FAIL/INCOMPLETE/MISSING_GMAT distinctions already defined in src/gmat_verify.py and src/verification_report.py, with no new silent-PASS path introduced
- [x] #4 src/workflow.py::run_rendezvous_workflow continues to work unchanged for any caller that does not go through the new tool (the tool is additive, not a required refactor of the existing function-call path)
- [x] #5 .pi/prompts/rendezvous.md is updated to reference the new tool explicitly in its step 3 so a session following that prompt actually uses it
- [x] #6 A test (or documented manual verification) confirms the tool is discoverable and callable in a pi session, and that calling it reaches a real or stand-in GMAT result consistent with the existing test patterns in tests/test_cw_gmat_slice.py / tests/test_workflow.py
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-12:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create project-local pi extension at .pi/extensions/gmat-verification-tool/index.ts registering pi.registerTool({name: 'run_gmat_verification', ...}) per docs/extensions.md's Custom Tools API (TypeBox parameters).
2. The tool wraps src/gmat_verify.py's already-audited functions by spawning the venv python3 (via pi.exec/child_process) to run a small, thin dispatcher script (scripts/gmat_tool_bridge.py) that imports src.gmat_verify + src.verification_report and performs exactly the same execution/parsing/comparison calls scripts/run_cw_gmat_slice.py and src/workflow.py already make -- no reimplementation of GMAT script generation, parsing, or comparison logic in TypeScript.
3. Input schema (TypeBox Type.Object) requires the same structured case identity/tolerances src/workflow.py::RendezvousCase/_run_cw_path requires for the CW path: case_id, mu_m3_s2, reference_radius_m, initial_relative_state (6 numbers), final_relative_state (6 numbers, optional defaulting to zeros), transfer_time_s, pos_tol_m, vel_tol_mps, dv_tol_mps, output_dir, gmat_executable, gmat_gui_executable, attempt_gui_screenshot -- no free-text fields.
4. Output surfaces the PASS/WARNING/FAIL/INCOMPLETE comparison status plus the MISSING_GMAT/EXECUTION_ERROR/MALFORMED_OUTPUT/NUMERICAL_DISAGREEMENT/SCREENSHOT_FAILURE/CW_TARGETING_INFEASIBLE failure_mode and verified/verification_status fields exactly as produced by src/verification_report.py's UnifiedVerificationReport.to_dict(), with no new silent-PASS path (the tool never overrides or reinterprets verified/failure_mode itself).
5. src/workflow.py::run_rendezvous_workflow is not modified at all; the new bridge script is strictly additive (new file under scripts/), confirmed by re-running the full existing pytest suite unchanged after implementation.
6. Update .pi/prompts/rendezvous.md step 3 to call the new run_gmat_verification pi tool as the GMAT-verification integration point for the CW path (still constructing the same RendezvousCase-equivalent structured fields), while leaving steps 1, 2, 4, 5 untouched.
7. Verification (AC6): run 'pi -e .pi/extensions/gmat-verification-tool/index.ts --no-session -p' smoke tests to confirm the extension loads without error and the tool is listed/callable; additionally run a direct pytest-style invocation of the underlying bridge script (scripts/gmat_tool_bridge.py) against a stand-in/mocked GMAT case mirroring tests/test_cw_gmat_slice.py's patterns, asserting it reaches a MISSING_GMAT (stand-in executable) result with the same failure_mode vocabulary. Document red (file/tool absent) then green (tool present, bridge script producing the expected stand-in result) evidence, append both to Backlog notes.
8. Do not modify run_rendezvous_workflow's signature/behavior; do not commit; leave Backlog status In Progress for independent verifier.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
TDD red/green evidence for tests/test_gmat_tool_bridge.py (new pytest file, scripts/gmat_tool_bridge.py bridge script): RED -- with scripts/gmat_tool_bridge.py temporarily removed, '.venv/bin/python -m pytest tests/test_gmat_tool_bridge.py -q' failed at collection: 'ModuleNotFoundError: No module named scripts.gmat_tool_bridge' (1 error in 0.25s). GREEN -- after restoring scripts/gmat_tool_bridge.py, the same command passed: '6 passed in 1.41s'. All 6 tests (build_slice_case field validation/reshaping, run_bridge MISSING_GMAT stand-in result matching tests/test_cw_gmat_slice.py's pattern, output_dir handling, and two CLI subprocess invocations for stdin/stdout JSON contract and invalid-JSON-input error handling) exercise the bridge script directly, not GMAT itself.

Implementation complete (independent verifier to check ACs; status intentionally left In Progress, not committed).

Files created: scripts/gmat_tool_bridge.py (thin CLI bridge: JSON stdin/--case-json -> reshapes into scripts/run_cw_gmat_slice.py::run_cw_rendezvous_gmat_verification's existing dict shape -> prints its result dict, including the embedded UnifiedVerificationReport.to_dict(), as JSON to stdout verbatim; exit 0 iff verified, else nonzero); .pi/extensions/gmat-verification-tool/index.ts (registers the 'run_gmat_verification' pi tool via pi.registerTool() with a TypeBox schema requiring case_id/mu_m3_s2/reference_radius_m/initial_relative_state/transfer_time_s plus optional final_relative_state/pos_tol_m/vel_tol_mps/dv_tol_mps/output_dir/gmat_executable/gmat_gui_executable/attempt_gui_screenshot -- no free text; execute() shells out via pi.exec to the venv python + bridge script with --case-json, parses its stdout JSON, and returns it verbatim as structuredContent/details, isError=!verified, never recomputing verified/failure_mode itself); tests/test_gmat_tool_bridge.py (6 new pytest tests for the bridge script).

Files modified: .pi/prompts/rendezvous.md (step 3 only: CW-path branch now explicitly calls the run_gmat_verification pi tool as the auditable GMAT-verification step instead of only calling run_rendezvous_workflow directly; bounded-two-body-fallback branch unchanged, still calls run_rendezvous_workflow directly since the tool only wraps the CW path per the approved plan; steps 1,2,4,5 untouched -- confirmed via git diff).

src/workflow.py: confirmed byte-identical to HEAD ('git diff --stat src/workflow.py' empty) -- AC4 satisfied, run_rendezvous_workflow was never modified.

AC6 verification evidence (bridge script, direct): 'echo <CW case JSON with gmat_executable=definitely-not-gmat> | .venv/bin/python scripts/gmat_tool_bridge.py' and also '.venv/bin/python scripts/gmat_tool_bridge.py --case-json <...>' both returned failure_mode=MISSING_GMAT, verified=false, exit code 1, with the full UnifiedVerificationReport embedded (comparison.status=INCOMPLETE, human_readable_report present) -- matches tests/test_cw_gmat_slice.py's MISSING_GMAT pattern exactly.

AC6 verification evidence (pi tool, real end-to-end): 'PI_OFFLINE=1 pi --no-session -p --approve "List registered tools whose name contains gmat..."' printed 'functions.run_gmat_verification', confirming the project-local extension auto-loads (no -e flag needed, trusted project) and the tool is discoverable. A second real session, 'PI_OFFLINE=1 pi --no-session --mode json -p --approve "Call the run_gmat_verification tool with case_id=pi_tool_smoke_test_json, mu_m3_s2=..., ... gmat_executable=definitely-not-gmat..."', produced a genuine LLM-issued tool_call for run_gmat_verification with the exact structured arguments (case_id, mu_m3_s2, reference_radius_m, initial_relative_state, transfer_time_s, gmat_executable), and the tool_result JSON contained failure_mode=MISSING_GMAT, verified=false -- end-to-end: a real pi session's LLM discovered and called the tool, the tool shelled out to the bridge script, and the bridge script reached src/gmat_verify.py's MISSING_GMAT failure mode, surfaced unmodified. Also confirmed loadable via explicit '-e .pi/extensions/gmat-verification-tool/index.ts' flag (same tool-listing result).

Red/green TDD evidence for tests/test_gmat_tool_bridge.py already recorded in a separate notes entry above (RED: ModuleNotFoundError at collection with scripts/gmat_tool_bridge.py removed; GREEN: 6 passed after restoring it).

TypeScript extension red/green note: no pytest-style red/green applies to the .ts extension file itself (it is not a Python unit under this repo's testing-policy.md scope, and 'red' before the file existed would just be 'file not found', not a meaningful failing assertion). Instead, AC6's own wording ('or documented manual verification... e.g. test the extension loads and the tool schema validates with a pi -e <extension path> smoke test') was followed directly: documented real pi CLI invocations above (tool-listing smoke test + an actual end-to-end tool-call smoke test with captured JSON-mode transcript showing the real LLM-issued tool_call and tool_result) serve as that manual verification evidence for the TypeScript layer; the bridge script underneath it does have full red/green pytest evidence.

Full test suite: '.venv/bin/python -m pytest -q' => 160 passed (154 pre-existing + 6 new in tests/test_gmat_tool_bridge.py), 0 failed, on a clean full run. One pre-existing test (tests/test_cw_gmat_slice.py::test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window, a real-GMAT-GUI-rendering comparison unrelated to this task) is independently confirmed flaky/nondeterministic in this sandbox: it fails identically when run in isolation against unmodified HEAD (git stash test performed) and also passed cleanly in the final full-suite run above -- not a regression introduced by this task.

Not committed, per instructions; Backlog status left In Progress for an independent verifier to check acceptance criteria.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Registered GMAT execution as an explicit, LLM-callable pi tool ('run_gmat_verification') via a project-local extension (.pi/extensions/gmat-verification-tool/index.ts) that shells out to a new thin Python bridge (scripts/gmat_tool_bridge.py), which itself calls straight into the already-audited scripts/run_cw_gmat_slice.py::run_cw_rendezvous_gmat_verification core -- no GMAT logic duplicated in either layer. Independently verified (not just from the worker's self-report): (1) re-ran the full suite myself -- 160 passed (154 pre-existing + 6 new in tests/test_gmat_tool_bridge.py), 0 failed; (2) independently reproduced red (ModuleNotFoundError at collection with the bridge script removed) then green (6 passed) for the new tests; (3) ran the bridge script directly against a stand-in 'definitely-not-gmat' executable myself and confirmed verified=false, failure_mode=MISSING_GMAT, exit code 1, full UnifiedVerificationReport embedded -- no silent-PASS path; (4) confirmed src/workflow.py is byte-identical to HEAD via git diff --stat; (5) ran a real end-to-end pi CLI session myself ('pi --no-session -p') and confirmed the tool is discoverable (listed as functions.run_gmat_verification with its full structured schema, no free-text field) and, in a second real session, confirmed an LLM-issued tool call against the same stand-in case returned verified=false/failure_mode=MISSING_GMAT; (6) confirmed .pi/prompts/rendezvous.md's step 3 now explicitly routes the CW path through this tool while the two-body-fallback branch and steps 1/2/4/5 are untouched (git diff reviewed directly).
<!-- SECTION:FINAL_SUMMARY:END -->
