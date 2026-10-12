---
id: TJC-1.9
title: Create the four-category rendezvous benchmark
status: Done
assignee:
  - '@worker'
created_date: '2026-10-01 14:18'
updated_date: '2026-10-12 17:21'
labels: []
dependencies:
  - TJC-1.12
  - TJC-1.14
  - TJC-1.21
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: medium
type: task
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a small, reviewable benchmark for the semester experiment. It must cover straightforward CW, boundary, CW-invalid/two-body, and ambiguous or incomplete natural-language cases without expanding into broad astrodynamics coverage.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The benchmark contains at least one case in each of the four required categories: straightforward CW, boundary, CW-invalid, and ambiguous/incomplete
- [x] #2 Each case records the request, expected structured problem, expected model, reference numerical result or expected clarification, GMAT tolerance, and expected explanation behavior
- [x] #3 Solvable cases include a reproducible GMAT script/result and required trajectory screenshot reference
- [x] #4 Boundary cases test documented CW assumptions without asserting a universal validity threshold
- [x] #5 Fixtures are schema-validated and versioned with units, frames, assumptions, and provenance
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
1. Create evaluations/benchmark/ directory with one versioned YAML fixture per required category (straightforward CW, boundary, CW-invalid/two-body, ambiguous/incomplete), each recording: request, expected structured problem (per orbital-problem-formalizer schema), expected model (per model_selector contract), reference numerical result or expected clarification questions, GMAT tolerances, expected explanation behavior, units/frames/assumptions, and a version/provenance marker.
2. For the straightforward-CW case, reuse scripts/run_cw_gmat_slice.py's existing default case (circular_leo_quarter_orbit_rendezvous) as the fixture's reference, pointing at examples/cw_gmat_vertical_slice.yaml and examples/cw_gmat_slice_example/ as the already-committed reproducible GMAT script/result/screenshot evidence (AC3).
3. For the CW-invalid/two-body case, construct a declared point-mass coast case (1,000 km radial offset LEO chaser) that: (a) src/model_selector.py routes to 'bounded two-body fallback'; (b) has a deterministic src/twobody.py reference result; and (c) has a reproducible GMAT numerical cross-check run via GmatConsole-R2026a (black-box call, not modifying gmat_verify.py) plus a trajectory screenshot artifact, committed under examples/benchmark_two_body_case/.
4. For the boundary case, use the same CW case at a half-orbital-period transfer time (Phi_rv singular-reachable per src/cw.py), confirm src/model_selector.py returns qualified=True with concerns documenting the specific borderline assumption (targeting conditioning), and generate a real GMAT run via scripts/run_cw_gmat_slice.py-equivalent black-box reuse of src/gmat_verify.py, committed under examples/benchmark_boundary_case/.
5. For the ambiguous/incomplete case, write a .txt fixture in the evaluations/formalizer/ style (reusing test_01_underspecified.txt's structure) with expected clarification questions and NEEDS CLARIFICATION / NEEDS MORE INFORMATION readiness; no model is expected.
6. Add tests/test_benchmark_fixtures.py validating every fixture file: required fields present, correct types/units, exactly one case per category, schema version present.
7. Run full pytest suite; fix any regressions.
8. Add site/js/pages/benchmark.js documenting the four-category benchmark and linking fixtures; register route in site/index.html; sync site/data/ mirrors via tools/sync_site_data.py; add new project-progress.js entry at top (preserve existing entries).
9. Smoke-check ./run_site.sh on an unused port; curl new/changed routes for HTTP 200.
10. Run tools/sync_site_data.py --check and tools/compare_upstream.py --check.
11. Backlog finalization: check AC1-5 and DoD1-7 with evidence, append notes, final summary, status Done.
12. Single atomic commit TJC-1.9: ...
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented evaluations/benchmark/ with exactly one fixture per required category: (a) case_a_straightforward_cw.json reuses the already-committed, already-GMAT-verified examples/cw_gmat_slice_example/ evidence (CW rendezvous, unqualified, GMAT VERIFIED/PASS, pos err 0.0079 m, vel err 1.17e-5 m/s); (b) case_b_boundary_cw.json uses the same geometry at an exact half-orbital-period transfer, where src/cw.py reports Phi_rv singular-but-reachable, so src/model_selector.py returns qualified=True with surfaced concerns (not a flat pass/fail, no invented universal threshold) -- real GMAT run via new scripts/generate_benchmark_gmat_evidence.py reaches VERIFIED/PASS (pos err 0.046 m, vel err 3.07e-5 m/s), committed under examples/benchmark_case_b_boundary/; (c) case_c_two_body.json is a declared coast-only point-mass case (LEO chaser offset radially 1,000 km) that src/model_selector.py routes to the bounded two-body fallback (locality, other_physics violated) -- real GMAT cross-check (GMAT's own EarthMJ2000Eq point-mass propagator vs src/twobody.py::propagate_cartesian_state) reaches VERIFIED/PASS (pos err 0.0022 m, vel err 5.25e-6 m/s), committed under examples/benchmark_case_c_two_body/; (d) case_d_ambiguous.txt reuses evaluations/formalizer/test_01_underspecified.txt's own request text in that directory's text-block style, expecting NEEDS CLARIFICATION / NEEDS MORE INFORMATION with no model selected. scripts/generate_benchmark_gmat_evidence.py calls src/cw.py, src/twobody.py, and src/gmat_verify.py as a black box only -- none of those modules nor scripts/run_cw_gmat_slice.py were modified; generated GMAT .script/report files are written to a per-run temp directory and are not committed, matching examples/cw_gmat_slice_example/'s existing committed-artifact convention. Added tests/test_benchmark_fixtures.py (11 tests): schema validation of all required AC2 fields/types across fixtures, exactly-one-case-per-category, boundary-case qualified/no-universal-threshold assertions, two-body routing assertions, ambiguous-case clarification assertions, a live cross-check of cases (b)/(c) against a real src.model_selector.select_model call built from each fixture's own recorded assumptions, and existence/non-emptiness/VERIFIED checks of the referenced committed GMAT evidence. Added site/js/pages/benchmark.js (route 'benchmark', linked from site/index.html's Worked Example nav section) rendering all four fixtures plus the committed GMAT evidence/screenshots; added evaluations/benchmark/ and new examples/benchmark_case_b_boundary//examples/benchmark_case_c_two_body/ mappings to tools/sync_site_data.py and ran it (python3 tools/sync_site_data.py --check reports mirrors match, 45 mappings). Added a new TJC-1.9 entry at the top of site/data/project-progress.js without disturbing the existing TJC-2 (and later) entries already present. Verification: .venv/bin/python -m pytest -q -> 79 passed (was 68 before this task, net +11 new tests, 0 regressions). python3 tools/compare_upstream.py --check -> exit 0, 'content-different unaccounted: none'. ./run_site.sh 4294 smoke-tested; curl of / , js/pages/benchmark.js, all new data/evaluations/benchmark/* and data/examples/benchmark_case_*/* routes, and data/project-progress.js all returned HTTP 200.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added a four-category rendezvous benchmark under evaluations/benchmark/ (straightforward CW, boundary, CW-invalid/two-body, ambiguous/incomplete), each case recording the request, expected formalizer-schema structured problem, expected model_selector outcome, a GMAT-verified reference numerical result (or expected clarification questions for the ambiguous case), GMAT tolerances, and expected explanation behavior, with explicit schema_version/case_version/provenance. Solvable cases (a, b, c) ship real, reproducible GMAT numerical evidence and required trajectory screenshots: (a) reuses the existing examples/cw_gmat_slice_example/ evidence; (b)/(c) are generated by a new scripts/generate_benchmark_gmat_evidence.py, which calls the existing src/cw.py/src/twobody.py/src/gmat_verify.py as a black box (none modified) and reaches real GmatConsole-R2026a VERIFIED/PASS results. The boundary case exercises src/model_selector.py's documented targeting-conditioning signal (singular-but-reachable Phi_rv) to produce qualified=True with surfaced concerns, without inventing a new universal numeric validity threshold. tests/test_benchmark_fixtures.py schema-validates every fixture and cross-checks cases (b)/(c) against a live select_model() call. Updated the educational site (new benchmark.js page/route, site data mirrors synced, project-progress.js entry added at top without disturbing existing entries). Verified with: .venv/bin/python -m pytest -q -> 79 passed, 0 regressions; python3 tools/sync_site_data.py --check -> match; python3 tools/compare_upstream.py --check -> exit 0, no unaccounted drift; ./run_site.sh smoke-tested with curl 200s on all new/changed routes.
<!-- SECTION:FINAL_SUMMARY:END -->
