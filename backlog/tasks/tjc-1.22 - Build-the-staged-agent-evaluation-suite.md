---
id: TJC-1.22
title: Evaluate the scoped workflow against a direct-LLM baseline
status: Done
assignee:
  - '@worker'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-14 20:08'
labels: []
dependencies:
  - TJC-1.8
  - TJC-1.9
  - TJC-1.16
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
documentation:
  - >-
    backlog/docs/specifications/semester-scope/doc-1 -
    Trajectory-CoPilot-Semester-Scope.md
parent_task_id: TJC-1
priority: high
type: feature
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the four-category rendezvous benchmark through a direct natural-language-to-LLM-answer baseline and the complete structured workflow. Evaluate which formulation, model-selection, numerical, verification, visual-artifact, and explanation errors the architecture prevents or detects; do not claim universal superiority.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Both the direct-LLM baseline and full workflow run against the same versioned benchmark requests
- [x] #2 Scoring covers structured formulation, ambiguity detection, model selection, numerical agreement, GMAT invocation, discrepancy handling, screenshot availability, and explanation quality
- [x] #3 Results retain prompts, model/tool versions, deterministic inputs/outputs, GMAT artifacts, tolerances, and reproducibility settings
- [x] #4 The report includes aggregate and per-case analysis for all four benchmark categories
- [x] #5 Conclusions identify prevented/detected error types and limitations without asserting broad astrodynamics validity
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
1. Create evaluations/baseline_comparison/ directory with README documenting methodology (direct-LLM baseline = this implementing model, single-shot, no tool access, honestly disclosed; full workflow = src/workflow.py::run_rendezvous_workflow run against evaluations/benchmark/ fixtures a-d, reusing already-committed GMAT evidence in examples/cw_gmat_slice_example, examples/benchmark_case_b_boundary, examples/benchmark_case_c_two_body where correct).
2. For each case a/b/c/d: write the direct-LLM baseline response (produced by me, single-shot, no src/ access) to a per-case markdown/text file; write the full-workflow actual result by running/reusing the existing scripts (run_cw_gmat_slice.py for a, generate_benchmark_gmat_evidence.py-produced evidence for b/c, formalizer-level readiness short-circuit for d) and capturing exact outputs.
3. Score both approaches per AC2 dimensions (structured formulation, ambiguity detection, model selection, numerical agreement, GMAT invocation, discrepancy handling, screenshot availability, explanation quality) in a pass/fail/partial table per case.
4. Write the final report (evaluations/baseline_comparison/REPORT.md) with methodology, exact prompts, model/tool versions (PI_MODEL/PI_PROVIDER env, GMAT R2026a build), deterministic inputs/outputs, GMAT artifact paths, tolerances, reproducibility commands, per-case + aggregate analysis (AC4), and conclusions naming specific prevented/detected error types scoped to this 4-case benchmark (AC5).
5. Add tests/test_baseline_comparison.py checking the report/artifacts exist with required structure (schema-style, no GMAT re-run), following tests/test_benchmark_fixtures.py's pattern.
6. Add a site page (site/js/pages/baseline-comparison.js or similar) modeled on site/js/pages/benchmark.js, update project-progress.js with TJC-1.22 entry, sync any mirrors.
7. Run full repo checks (pytest, compare_upstream --check, sync_site_data --check, run_site.sh smoke test), finalize Backlog (check ACs/DoD, final summary, Done), and make exactly one commit 'TJC-1.22: ...'.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Ran all 4 evaluations/benchmark/ cases through both approaches. Baseline: no live LLM API available in this sandbox, so the implementing model (PI_MODEL=bedrock/claude-sonnet-5, PI_PROVIDER=MIT-parley) produced each case's direct-LLM answer single-shot with no access to src/, .pi/skills/, model selector, or GMAT -- disclosed explicitly in evaluations/baseline_comparison/README.md and REPORT.md. Full workflow: evaluations/baseline_comparison/run_workflow_cases.py builds each RendezvousCase/ModelSelectionCase directly from evaluations/benchmark/*.json field values and calls src/workflow.py::run_rendezvous_workflow for real; ran against a real GmatConsole-R2026a install (Build Date Mar 30 2026) for cases a/b/c (all reached verified=True, comparison.status=PASS, matching the already-committed examples/cw_gmat_slice_example, examples/benchmark_case_b_boundary, examples/benchmark_case_c_two_body evidence exactly); case d correctly short-circuited at NEEDS_CLARIFICATION with model_selection=None and artifacts={}. Scoring table (AC2) and per-case + aggregate analysis (AC4) in REPORT.md. Named prevented/detected error types (AC5): case d - baseline silently invented 5 unauthorized assumptions (altitude, LVLH sign convention, initial relative velocity, terminal condition, maneuver count) vs. workflow's hard stop before any physics; case b - baseline missed the documented singular-but-reachable CW targeting-conditioning boundary vs. workflow's explicit qualified=True + named concerns; cases a/b/c - baseline's correct-looking numbers backed only by an informal unverified disclaimer vs. workflow's real GMAT comparison + validated screenshot artifact in every solvable case. Report explicitly scopes conclusions to these 4 cases and the narrow supported rendezvous class; states this is not a cross-model or general-astrodynamics capability claim. Added tests/test_baseline_comparison.py (17 tests, schema/structure checks, no GMAT re-run) and site/js/pages/baseline-comparison.js (#/baseline-comparison route) plus site/data/project-progress.js TJC-1.22 entry. Verification commands/output: '.venv/bin/python -m pytest -q' -> 146 passed (129 pre-existing + 17 new, zero regressions); 'python3 tools/compare_upstream.py --check' -> content-different unaccounted: none (exit 0); 'python3 tools/sync_site_data.py --check' -> site data mirrors match (62 mappings) (exit 0); './run_site.sh 4199' smoke-tested with curl: /, /index.html, /js/pages/baseline-comparison.js, /data/evaluations/baseline_comparison/README.md, /REPORT.md, /case_a_baseline_llm_response.md, /case_a_workflow_result.json all returned 200, and the fetched JSON parsed with outcome=VERIFIED.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the TJC-1.22 baseline-vs-structured-workflow evaluation under evaluations/baseline_comparison/: a direct-LLM baseline response (produced single-shot by the implementing model, with no live external LLM API available in this sandbox and no access to this project's src/, skills, model selector, or GMAT -- explicitly disclosed as the realistic baseline design for this environment) and a real run of src/workflow.py::run_rendezvous_workflow for each of the four versioned evaluations/benchmark/ cases (a/b/c run against a real GmatConsole-R2026a install, reaching VERIFIED/PASS and matching the already-committed TJC-1.9 GMAT evidence exactly; case d correctly short-circuits at NEEDS_CLARIFICATION with zero physics/GMAT calls). REPORT.md scores both approaches across all 8 AC2 dimensions per case, gives per-case plus aggregate analysis across all four categories (AC4), and names specific prevented/detected error types (silently invented assumptions in the ambiguous case; a missed CW targeting-conditioning boundary in the boundary case; unverified-vs-GMAT-verified numeric claims across the solvable cases) while explicitly scoping every conclusion to this 4-case benchmark and the project's narrow supported rendezvous class, with no claim of general astrodynamics or cross-model superiority (AC5). Added tests/test_baseline_comparison.py (17 passing tests) and a new #/baseline-comparison site page/progress entry. Verified: 146/146 tests pass (zero regressions), tools/compare_upstream.py --check and tools/sync_site_data.py --check both pass, and ./run_site.sh was smoke-tested for the new route and its fetched artifacts.
<!-- SECTION:FINAL_SUMMARY:END -->
