---
id: TJC-1.8
title: Add focused tests for the scoped end-to-end workflow
status: Done
assignee:
  - '@worker'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-12 21:33'
labels: []
dependencies:
  - TJC-1.16
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: task
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add only the unit, physical-property, routing, failure, and integration tests needed to protect the narrowed rendezvous workflow. Tests should exercise deterministic physics, model selection, GMAT result handling, screenshot inclusion, and refusal/clarification behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Tests cover CW propagation/targeting, two-body propagation, and LVLH/inertial transformation properties used by the supported workflow
- [x] #2 Tests cover ambiguous input, CW-applicable routing, CW-invalid routing, singular targeting, GMAT disagreement, and unavailable-GMAT behavior
- [x] #3 A verification result cannot pass when numerical output or the required screenshot artifact is missing
- [x] #4 Tests confirm the LLM-facing layer never supplies authoritative orbital states or delta-v without deterministic tool output
- [x] #5 The full focused suite runs from the documented clean-checkout command
- [x] #6 Tests enforce that supported two-body outputs invoke or retain pinned Poliastro evidence, while UNAVAILABLE, UNSUPPORTED, and disagreement outcomes cannot be represented as verified
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [x] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [x] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [x] #4 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [x] #5 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [x] #6 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [x] #7 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Survey existing 116 tests (test_cw.py, test_twobody.py, test_validation.py, test_model_selector.py, test_cw_gmat_slice.py, test_workflow.py, test_poliastro_verify.py, test_verification_report.py) against the 6 ACs to find real gaps rather than duplicate coverage.
2. Identify two genuine gaps: (a) no workflow-level test driving a model-selector-qualified singular/unreachable CW targeting case through src/workflow.py to its CW_TARGETING_INFEASIBLE outcome before any GMAT call; (b) AC4's 'LLM-facing layer never supplies authoritative state/delta-v without deterministic tool output' had no test of the actual LLM-facing .pi/skills/*/SKILL.md instruction files themselves, only of the Python code beneath them.
3. Add test_singular_infeasible_cw_targeting_is_distinct_outcome_before_any_gmat_call to tests/test_workflow.py.
4. Add tests/test_skill_authority_boundaries.py (9 tests) asserting every .pi/skills/*/SKILL.md file delegates numeric computation to a named src/ deterministic implementation, refuses to invent/improvise/solve a result itself, and requires GMAT numerical comparison + accessible screenshot before any PASS claim.
5. Do NOT touch src/gmat_verify.py's attempt_gmat_gui_screenshot (TJC-3's exclusive territory).
6. Sync site/data mirrors (tools/sync_site_data.py), add a new TJC-1.8 project-progress.js entry at the top without touching other entries, run full pytest + compare_upstream --check + sync_site_data --check + run_site.sh smoke test.
7. Finalize Backlog and make one atomic commit 'TJC-1.8: ...'.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Surveyed existing 116-test suite against TJC-1.8's 6 ACs; found 4/6 already fully satisfied by pre-existing tests, 2 real gaps closed:
AC1 (CW/two-body/LVLH properties): satisfied by test_cw.py (test_cw_stm_identity_at_zero_time, test_cw_stm_blocks_match_cited_quarter_orbit_terms_and_units, test_cw_rendezvous_benchmark, test_solve_cw_rendezvous_reproduces_audited_leo_benchmark), test_twobody.py (test_circular_orbit_matches_analytical_state_after_one_period, test_energy_and_angular_momentum_are_conserved_over_supported_duration), test_validation.py (test_lvlh_basis_is_orthonormal_and_right_handed, test_lvlh_inertial_round_trips_preserve_state_and_deputy_subtraction_direction, test_nonzero_relative_velocity_includes_rotating_frame_transport_term).
AC2 (ambiguous/CW-applicable/CW-invalid/singular-targeting/GMAT-disagreement/unavailable-GMAT routing): satisfied by test_model_selector.py (test_clearly_suitable_case_selects_cw_rendezvous, test_clearly_unsuitable_geo_case_routes_to_two_body_fallback, test_near_singular_targeting_conditioning_qualifies_the_decision, test_missing_information_yields_clarification_not_a_model_choice) and test_workflow.py (test_needs_clarification_short_circuits..., test_cw_invalid_case_routes_to_two_body_fallback..., test_numerical_disagreement_is_distinct_outcome, test_missing_gmat_is_distinct_outcome). GAP CLOSED: added test_singular_infeasible_cw_targeting_is_distinct_outcome_before_any_gmat_call to tests/test_workflow.py -- no prior test drove a model-selector-qualified singular/unreachable (CWTargetingResult status='singular-infeasible') CW case through the FULL connected src/workflow.py pipeline to CW_TARGETING_INFEASIBLE before any GMAT call; test_cw.py and test_cw_gmat_slice.py each covered this at a lower layer (direct two_burn_targeting call, or scripts/run_cw_gmat_slice.py's helper with a stubbed SimpleNamespace solution) but not through run_rendezvous_workflow end to end.
AC3 (never-false-PASS invariant): satisfied by src/verification_report.py::assemble_verification_report's constructor-time ValueError enforcement (raises if verified=True requested without GMAT attempted+exit 0+parsed final state+PASS comparison+valid screenshot all true), regression-tested directly in test_verification_report.py::test_verified_true_without_gmat_attempted_raises / test_verified_true_with_nonzero_exit_status_raises / test_verified_true_without_parsed_gmat_final_state_raises / test_verified_true_with_non_pass_comparison_raises / test_verified_true_without_comparison_raises / test_verified_true_with_invalid_screenshot_raises, plus test_missing_screenshot_refuses_verified_true / test_corrupt_screenshot_refuses_verified_true.
AC4 (LLM-facing layer never supplies authoritative state/delta-v without deterministic tool output): the Python code paths (model_selector.py, workflow.py, verification_report.py) already enforce this and were already tested, but the actual LLM-facing layer -- the 5 .pi/skills/*/SKILL.md prompt-driven instruction files that src/workflow.py's own docstring calls 'prompt-driven, not Python code' -- had zero test coverage of this invariant. GAP CLOSED: added tests/test_skill_authority_boundaries.py (9 new tests) asserting every skill (orbital-problem-formalizer, orbital-model-selector, orbital-targeting-planner/cw-rendezvous, orbital-two-body-rendezvous, gmat-rendezvous-verification) explicitly names its required src/ deterministic implementation handoff, explicitly refuses to invent/improvise/solve a numeric result itself, and that both solver-calling skills explicitly require the separate gmat-rendezvous-verification handoff (GMAT numerical comparison AND accessible screenshot together) before any PASS claim.
AC5 (documented clean-checkout command): already satisfied -- README.md's 'Reproducible setup' section documents the exact 3-line clean-checkout command (python3 -m venv .venv && .venv/bin/python -m pip install -r requirements-dev.txt && .venv/bin/python -m pytest -q). No new documentation needed.
AC6 (pinned-Poliastro evidence retained for two-body outputs; UNAVAILABLE/UNSUPPORTED/disagreement never verified): satisfied by test_poliastro_verify.py (test_absent_environment_is_unavailable, test_broken_subprocess_is_unavailable, test_unsupported_frame_never_passes, test_deliberate_candidate_perturbation_fails, test_three_supported_cases_retained_as_machine_readable_evidence -- which writes evidence/poliastro/contract-test-evidence.json as retained machine-readable evidence). Note: src/workflow.py's two-body path does not currently call src/poliastro_verify.py directly (it uses src/gmat_verify.py's independent GMAT comparison as its required verification layer, consistent with docs/poliastro-verification-architecture.md's stated architecture that Poliastro is a code-level two-body cross-check ALONGSIDE, not instead of, GMAT, and GMAT remains the required end-to-end verifier). This is accurately described by the existing architecture doc and is not a gap in TJC-1.8's own scope (connecting src/workflow.py to the Poliastro adapter directly was not part of TJC-1.16's connected-workflow implementation plan and would be a new architecture decision outside this test-only task's scope).

Verification commands run from a fresh worktree after python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt:
- .venv/bin/python -m pytest -q -> '126 passed' (116 pre-existing + 1 new tests/test_workflow.py case + 9 new tests/test_skill_authority_boundaries.py tests, zero regressions)
- python3 tools/compare_upstream.py --check -> 'content-different unaccounted: none'
- python3 tools/sync_site_data.py --check -> 'site data mirrors match (50 mappings)' (after adding tests/test_skill_authority_boundaries.py to MAPPINGS and running the sync once)
- ./run_site.sh 4321 then curl-smoke: / (200), /index.html (200), /data/project-progress.js (200, contains 4x 'TJC-1.8'), /data/tests/test_workflow.py (200), /data/tests/test_skill_authority_boundaries.py (200), /js/pages/progress.js (200); server then stopped and confirmed unreachable.
- Did NOT modify src/gmat_verify.py (TJC-3's exclusive territory per task instructions).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Surveyed the existing 116-test suite against TJC-1.8's six acceptance criteria. Four of six (AC1, AC2, AC3, AC5, AC6) were already fully satisfied by pre-existing tests (test_cw.py, test_twobody.py, test_validation.py, test_model_selector.py, test_cw_gmat_slice.py, test_workflow.py, test_poliastro_verify.py, test_verification_report.py, and README.md's documented clean-checkout pytest command) -- cited by exact file:test_name in implementation notes. Closed two real gaps: (1) added test_singular_infeasible_cw_targeting_is_distinct_outcome_before_any_gmat_call to tests/test_workflow.py, driving a model-selector-qualified singular/unreachable CW targeting case through the FULL connected src/workflow.py pipeline to CW_TARGETING_INFEASIBLE before any GMAT call, which no prior test did at that integration level; (2) added tests/test_skill_authority_boundaries.py (9 new tests) covering AC4's requirement that the LLM-facing layer never supplies authoritative state/delta-v without deterministic tool output -- previously untested at the actual LLM-facing layer (the 5 .pi/skills/*/SKILL.md prompt-driven instruction files), only at the Python code layer beneath them. Did not modify src/gmat_verify.py's attempt_gmat_gui_screenshot or any Xvfb/screenshot internals (TJC-3's exclusive parallel territory). Added a new TJC-1.8 project-progress.js entry at the top of the Completed list without touching any other task's entry. Verified: .venv/bin/python -m pytest -q -> 126 passed (116 pre-existing + 10 new, zero regressions); tools/compare_upstream.py --check -> no unaccounted drift; tools/sync_site_data.py --check -> 50 mappings match; ./run_site.sh smoke-tested on port 4321 with all changed/added routes returning 200, server stopped and confirmed unreachable afterward.
<!-- SECTION:FINAL_SUMMARY:END -->
