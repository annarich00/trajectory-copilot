---
id: TJC-6.1
title: Add CW targeting singularity and conditioning property coverage
status: Done
assignee:
  - '@annarich00'
created_date: '2026-10-30 17:52'
updated_date: '2026-11-03 15:28'
labels: []
dependencies:
  - TJC-6
parent_task_id: TJC-6
priority: medium
type: task
ordinal: 67000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TJC-6's STM and targeting-feasibility properties are deliberately restricted to non-singular, well-conditioned generated cases, so the singularity/conditioning behavior already investigated for the operator's one-period rendezvous case (the exact-period CW_TARGETING_INFEASIBLE result) needs its own dedicated, independently derived test coverage rather than being assumed covered by the STM tests or silently left untested. Before writing any test, derive the exact rank-loss condition for the real 3x3 Phi_rv submatrix actually used by src.cw.two_burn_targeting (not an assumed shorthand): compute and factor the symbolic determinant of Phi_rv(n, t), and identify every distinct root family and which rows/columns/physical directions become dependent or vanish at each -- including checking whether whole-period multiples are a distinct, more severe case than general half-period multiples, and whether any additional non-periodic root family exists from the in-plane factor alone (do not hard-code any single numerically located root, such as one found near theta is approximately 8.8387, as the only additional root; the derivation and generated test domain must account for the full transcendental in-plane root condition, i.e. 3*theta*sin(theta) + 8*cos(theta) - 8 = 0, as a condition, not a fixed numeric value). Retain nt = k*pi-type language only for the specific sub-case the derivation actually confirms it describes. Keep the mathematical singularity (exact rank loss) explicitly distinct from the numerical CW_CONDITION_NUMBER_LIMIT routing threshold already in src/cw.py, which is a separate, configurable near-singular-detection heuristic, not the same condition. Inspect two_burn_targeting's actual return contract (status, feasible, singular, non_unique, reachability_residual_m, svd_rank_tolerance, svd_residual_tolerance) before writing any expected-result assertion, and test that documented reachability criterion (SVD column-space residual versus tolerance) as it actually exists, not an assumed label scheme. This task produces test evidence only; it does not implement a new recovery or automatic-retiming algorithm.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A property/example test derives and documents the factored det(Phi_rv) for the actual submatrix in cw_stm as a function of theta = n*t, identifies each distinct root family (the general sin(theta) = 0 cross-track-loss family at every theta = k*pi; the more severe whole-period theta = 2*pi*k case where the in-plane block also collapses; and the separate non-periodic in-plane-only root family defined by the transcendental condition 3*theta*sin(theta) + 8*cos(theta) - 8 = 0, treated as a condition to solve/sample numerically within a bounded test domain, not a single hard-coded root value), and states the resulting rank and which physical direction(s) remain or lose controllability at each family -- derived from the block structure and confirmed numerically, not assumed from the operator's single worked example
- [x] #2 A property test, over a bounded local interval around one specific known-singular theta at a time (not swept across arbitrary/unrelated transfer times), confirms condition_number(Phi_rv) increases as theta approaches that singular point and decreases moving away within that local window, with the local-only scope and its justification stated explicitly (condition number blow-up near an isolated singularity is a local statement, and AC1's derivation already shows singular points are not evenly spaced or of uniform severity, so global monotonicity across arbitrary transfer times is not asserted or tested); mean motion n is constrained to physically valid positive finite values throughout
- [x] #3 A property test confirms the full CW STM (cw_stm / propagate_relative_state) remains finite and correctly propagates a state at exactly a singular theta identified in AC1, demonstrating singularity is a targeting-solvability property of Phi_rv alone, not a general STM-evaluation failure
- [x] #4 A property test inspects two_burn_targeting's actual documented return contract first, then asserts: at a singular theta where the derived reachability residual exceeds svd_residual_tolerance, the function returns feasible=False / status="singular-infeasible" with no fabricated burn; where the boundary condition is genuinely within the reachable SVD column space, it returns the documented "singular-reachable" / non-unique result -- using the labels and fields two_burn_targeting actually returns, not assumed ones
- [x] #5 A property test sweeps alternative transfer durations near (but strictly not at) a known singular theta, within a bounded interval, and confirms targeting becomes well-conditioned/feasible moving away from that singular point -- consistent with the operator's own worked example (0.99/1.01 period offsets) -- without adding any automatic retiming/recovery logic to source code
- [x] #6 Each property test follows TJC-5's documentation policy in full, including explicitly recording the distinction between mathematical singularity (exact rank loss, AC1) and the separate numerical CW_CONDITION_NUMBER_LIMIT routing heuristic as a stated assumption/limitation
- [x] #7 Full existing test suite passes unchanged; new tests' runtime is bounded (explicit max_examples/deadline settings)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-6.1:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Derive det(Phi_rv(n,t)) symbolically as function of theta=n*t from src/cw.py's actual phi_rv block; confirm numerically (not just trust prior art) that det(Phi_rv) = -(sin(theta)/n^3) * (3*theta*sin(theta) + 8*cos(theta) - 8), i.e. factors as -sin(theta)/n^3 times the in-plane transcendental term g(theta)=3*theta*sin(theta)+8*cos(theta)-8.
2. Numerically classify root families of theta in (0, 10*pi]: (a) sin(theta)=0 at theta=k*pi -- confirm rank drops to 2 (cross-track row/col 3 vanishes, in-plane block stays rank 2) at odd-k*pi; (b) theta=2*pi*k (even k*pi) is distinct/more severe: confirm numerically rank drops to 1 (in-plane block ALSO becomes rank-1/collapses, not just cross-track); (c) separately find roots of g(theta)=0 that do NOT coincide with sin(theta)=0 (in-plane-only root family, e.g. near theta~8.8387, confirmed via bounded numerical root search in [0,4*pi] or similar, not hard-coded) -- confirm rank there is 2 (cross-track row/col stays full rank, in-plane block alone collapses).
3. Document derivation explicitly as module-level docstring/comments in new tests/test_cw_targeting_singularities.py, with actual numerical assertions (not just prose) confirming the determinant factorization and each root family's rank, before any other test is written. Explicitly state the mathematical-singularity (exact Phi_rv rank loss) vs. CW_CONDITION_NUMBER_LIMIT (numerical routing heuristic) distinction as a documented limitation repeated in every test's docstring per TJC-5 policy.
4. Write AC2: bounded local-interval property test around one singular theta at a time confirming cond(Phi_rv) increases approaching and decreases moving away, locally only (state why no global monotonicity claim).
5. Write AC3: property test that cw_stm/propagate_relative_state stays finite and propagates correctly at exactly a singular theta from AC1 (STM itself is fine; only Phi_rv targeting-inversion is affected).
6. Write AC4: inspect CWTargetingResult's actual fields/two_burn_targeting contract (already read in src/cw.py), then test singular-infeasible (residual > tolerance, feasible=False, no fabricated burn) and singular-reachable (residual within tolerance, non_unique=True) outcomes using exact field/status names from the code.
7. Write AC5: bounded sweep of transfer durations near (not at) a singular theta showing targeting becomes well-conditioned/feasible moving away (e.g. period*0.99/1.01-style offsets) -- test evidence only, NO src/cw.py changes.
8. For every new test: follow red-then-green TDD -- deliberately break the assertion (wrong expected status/value or absurdly tight tolerance) first, run pytest, record genuine failure in Backlog notes via --append-notes, then fix to the correct/justified assertion, run pytest, record the passing output via --append-notes.
9. Run full suite (.venv/bin/python -m pytest -q) to confirm 167 baseline tests + new tests all pass (167/167 baseline unaffected, ignoring the known-flaky Xvfb screenshot test).
10. Leave status as In Progress; do not check ACs, do not write final summary, do not commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC1 derivation (done before any test-writing): Phi_rv(n,t) (src/cw.py's phi[:3,3:] block) is block-diagonal: a 2x2 in-plane (radial/along-track) submatrix direct-summed with a 1x1 cross-track scalar s/n. Hand-derived det(Phi_rv) = -(sin(theta)/n**3) * g(theta), theta=n*t, g(theta)=3*theta*sin(theta)+8*cos(theta)-8, by expanding the in-plane 2x2 determinant and simplifying with sin^2+cos^2=1. Confirmed numerically against np.linalg.det over 2000+ random (n,theta) pairs (max rel err ~2.4e-12 away from roots; later scaled-guard check over 1M samples found max scaled err ~1.1e-12). Three distinct root families identified and numerically confirmed:
(1) sin(theta)=0 at theta=k*pi (any integer k): cross-track row/col (index 2) vanishes; g(k*pi)=8*cos(k*pi)-8=-16 for odd k (nonzero), so in-plane block stays full rank -> rank(Phi_rv)=2. Confirmed at k=1,3,5 (n=0.0013): Phi_rv[2,2] and row/col 2 all < 1e-9, rank==2, in-plane det comfortably nonzero (~1e7 scale).
(2) theta=2*pi*k (even k, whole period) is STRICTLY MORE SEVERE: here additionally cos(theta)=1 so g(2*pi*k)=0 too -> BOTH factors vanish. Confirmed at k=1,2,3 (n=0.0013): rank(Phi_rv)==1 (not 2), only the along-track self-term Phi_rv[1,1] survives nonzero; radial and cross-track directions both lost. This matches/explains the operator's one-period CW_TARGETING_INFEASIBLE case being worse than a generic half-period multiple.
(3) Separate non-periodic in-plane-only family: roots of g(theta)=0 where sin(theta)!=0. Found via bounded numerical scan+brentq bisection over theta in (0,10*pi] (200,001-sample grid): 8 total roots of g, 4 coincide with family (1)/(2) (sin~0) and 4 are genuinely non-periodic: theta ~= 8.8387, 15.3643, 21.7471, 28.0850 rad (NOT hard-coded as a single value -- found by the scan itself; test asserts >=4 found, not an exact fixed list). At the first of these (n=0.0012): rank(Phi_rv)==2, cross-track Phi_rv[2,2] stays >1e-3 (full rank), but in-plane 2x2 det ~1e-6 (collapsed to rank 1) -- the complementary pattern to family (1): in-plane loses a dimension, cross-track does not.
Mathematical-vs-numerical distinction (AC6): all three families above are EXACT det(Phi_rv)=0 conditions on theta alone, independent of any tolerance. CW_CONDITION_NUMBER_LIMIT=1e6 is a separate, configurable NUMERICAL routing heuristic in two_burn_targeting/check_phi_rv_conditioning that ALSO routes merely-ill-conditioned (finite but large cond(Phi_rv), det!=0 exactly) transfer times through the same SVD path -- not the same property, documented explicitly in every new test's docstring and the new test module's header docstring.

TDD red/green evidence, test by test (new file tests/test_cw_targeting_singularities.py, 11 tests total):

1. test_det_phi_rv_factorization_matches_independent_hand_derivation (AC1): RED -- flipped sign of predicted_det (dropped leading minus). Failure: 'assert 1.9999999999999984 <= 1e-08' (relative_error=2.0, i.e. predicted was exactly the negative of actual) at n=0.0078125, theta=1.0. GREEN -- restored -(sin(theta)/n**3)*g(theta); passed. (Initial tolerance was absolute |det|>1e-20 guard + 1e-8 rel tol; full-module run surfaced an edge case at theta~=12*pi, n=0.0078125 with rel err 8.3e-5 because the ABSOLUTE guard was wrong -- det(Phi_rv) scales as 1/n**3 so a fixed absolute floor is inconsistently tight/loose across the generated n range. Fixed by scaling the floor to 1e-9/n**3 and loosening to 1e-6 rel tol, re-confirmed via 1M-sample numerical exploration (max scaled err ~1.1e-12); this is a tolerance-design correction, not a new red/green cycle on the core math claim, which was already confirmed above.)

2. test_odd_k_pi_family_loses_only_cross_track_rank (AC1): RED -- asserted matrix_rank==3. Failure: 'assert np.int64(2) == 3' at k=1 (n=0.0013). GREEN -- restored ==2; passed.

3. test_even_k_pi_whole_period_family_is_strictly_more_severe (AC1): RED -- asserted matrix_rank==2 (should be 1). Failure: 'assert np.int64(1) == 2' at k=1. GREEN -- restored ==1; passed.

4. test_inplane_only_root_family_exists_and_is_distinct_from_periodic_family (AC1): RED -- asserted len(non_periodic_roots)>=10. Failure: 'assert 4 >= 10' (actual list: [8.8387,15.3643,21.7471,28.0850]). GREEN -- restored >=4; passed.

5. test_inplane_only_root_family_loses_only_inplane_rank (AC1): RED -- asserted matrix_rank==3. Failure: 'assert np.int64(2) == 3'. GREEN -- restored ==2; passed.

TDD red/green evidence continued:

6. test_condition_number_increases_approaching_a_single_singular_theta_locally (AC2): RED -- inverted inequality to cond_near < cond_far. Failure: 'assert np.float64(81.30...) < np.float64(73.66...)' at singular_theta=pi, n=0.0078125, offset_near=0.125, offset_far=0.137, sign=-1.0 (i.e. near-point condition number 81.3 is actually >= far-point's 73.7, confirming the correct direction). GREEN -- restored cond_near >= cond_far; passed.

7. test_cw_stm_and_propagation_stay_finite_and_invertible_at_a_singular_theta (AC3): RED -- tightened round-trip tolerance to atol=1e-15 (impossibly tight). Failure: actual round-trip residual ~9.09e-13 at theta=pi, n=0.00819874018154963 -- genuinely exceeds 1e-15 but is well within a realistic floating-point margin. GREEN -- restored atol=1e-6; passed.

8. test_two_burn_targeting_whole_period_singularity_is_infeasible_for_unreachable_boundary (AC4): RED -- asserted status=='singular-reachable' (should be 'singular-infeasible'). Failure: "AssertionError: assert 'singular-infeasible' == 'singular-reachable'" (actual result genuinely infeasible, pure-radial target unreachable from theta=2*pi's rank-1 Phi_rv). GREEN -- restored 'singular-infeasible'; passed.

9. test_two_burn_targeting_whole_period_singularity_is_reachable_for_column_space_boundary (AC4): first RED attempt (tightened final_state tolerance to atol=1e-30) did not fail -- residual was exactly 0.0 by construction of the minimum-norm SVD solve, so this assertion alone could not be falsified; replaced with a genuine red: asserted non_unique is False (should be True). Failure: 'AssertionError: assert True is False ... non_unique' -- actual CWTargetingResult has non_unique=True (rank=1<3) as documented. GREEN -- restored non_unique is True; passed.

10. test_two_burn_targeting_inplane_only_singularity_distinguishes_reachable_and_infeasible (AC4): RED -- asserted infeasible_result.status=='singular-reachable' (should be 'singular-infeasible'). Failure: "AssertionError: assert 'singular-infeasible' == 'singular-reachable'" (the null-space-constructed target is genuinely unreachable at this in-plane-only singular theta). GREEN -- restored 'singular-infeasible'; passed.

11. test_targeting_becomes_well_conditioned_and_feasible_moving_away_from_singular_theta (AC5): RED -- tightened condition_number bound to <100.0 (should be < CW_CONDITION_NUMBER_LIMIT=1e6). Failure: 'assert 105.07450204864166 < 100.0' at singular_theta=pi, n=0.0078125, period_offset_fraction=0.03125, sign=-1.0 (a genuinely well-conditioned but >100 case Hypothesis found, confirming the chosen bound of 100 was too strict for the generated domain). GREEN -- restored < CW_CONDITION_NUMBER_LIMIT; passed.

All 11 tests pass together (tests/test_cw_targeting_singularities.py: 11 passed, re-run 5x for stability, all green, 2.5-5.3s total each run). Full suite after adding this module: 178 collected (167 baseline + 11 new); 178/178 passed on a clean re-run (one run hit the pre-documented known-flaky Xvfb/display-timing test test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window, which passed immediately on re-run in isolation -- confirmed pre-existing flake, not caused by this task's changes, per task brief's explicit guidance).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Derived and numerically confirmed det(Phi_rv(n,t)) = -(sin(theta)/n**3) * (3*theta*sin(theta)+8*cos(theta)-8), theta=n*t, identifying three distinct root families: the general sin(theta)=0 cross-track-loss family at theta=k*pi (rank 2); the strictly more severe whole-period theta=2*pi*k family where the in-plane block also collapses (rank 1); and a separate non-periodic in-plane-only family found by a bounded numerical search of the transcendental condition g(theta)=0 (4 roots found in (0,10*pi], not a single hard-coded value). Added tests/test_cw_targeting_singularities.py (11 new Hypothesis/example tests) covering all 7 ACs. Independently verified myself (not just the worker's self-report): re-derived and checked the determinant factorization from scratch against 2000 fresh random (n,theta) samples via np.linalg.det on the actual cw_stm output (max relative error 1.4e-11, confirming the formula is correct, not merely asserted); ran the full new test file myself (11/11 passed); re-ran the full suite twice (178/178 clean, with the one pre-existing Xvfb-timing flake reproducing and clearing on rerun, consistent with prior tasks); deliberately re-broke one AC4 assertion (singular-infeasible -> singular-reachable) myself and confirmed it fails for the documented genuine reason, then restored it and reconfirmed all 11 pass. Backlog implementation notes record genuine red-then-green TDD evidence for all 11 tests, including one transparently-reported tolerance-design correction (an absolute-vs-scaled error floor) distinguished from the three genuine red-reason failures. The mathematical-singularity-vs-CW_CONDITION_NUMBER_LIMIT distinction is documented explicitly in the module docstring and every individual test's docstring (AC6). No new recovery/retiming logic was added to src/cw.py (AC5 is test evidence only).
<!-- SECTION:FINAL_SUMMARY:END -->
