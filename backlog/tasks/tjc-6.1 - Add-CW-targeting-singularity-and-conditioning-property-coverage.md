---
id: TJC-6.1
title: Add CW targeting singularity and conditioning property coverage
status: To Do
assignee: []
created_date: '2026-10-30 17:52'
updated_date: '2026-11-02 02:12'
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
- [ ] #1 A property/example test derives and documents the factored det(Phi_rv) for the actual submatrix in cw_stm as a function of theta = n*t, identifies each distinct root family (the general sin(theta) = 0 cross-track-loss family at every theta = k*pi; the more severe whole-period theta = 2*pi*k case where the in-plane block also collapses; and the separate non-periodic in-plane-only root family defined by the transcendental condition 3*theta*sin(theta) + 8*cos(theta) - 8 = 0, treated as a condition to solve/sample numerically within a bounded test domain, not a single hard-coded root value), and states the resulting rank and which physical direction(s) remain or lose controllability at each family -- derived from the block structure and confirmed numerically, not assumed from the operator's single worked example
- [ ] #2 A property test, over a bounded local interval around one specific known-singular theta at a time (not swept across arbitrary/unrelated transfer times), confirms condition_number(Phi_rv) increases as theta approaches that singular point and decreases moving away within that local window, with the local-only scope and its justification stated explicitly (condition number blow-up near an isolated singularity is a local statement, and AC1's derivation already shows singular points are not evenly spaced or of uniform severity, so global monotonicity across arbitrary transfer times is not asserted or tested); mean motion n is constrained to physically valid positive finite values throughout
- [ ] #3 A property test confirms the full CW STM (cw_stm / propagate_relative_state) remains finite and correctly propagates a state at exactly a singular theta identified in AC1, demonstrating singularity is a targeting-solvability property of Phi_rv alone, not a general STM-evaluation failure
- [ ] #4 A property test inspects two_burn_targeting's actual documented return contract first, then asserts: at a singular theta where the derived reachability residual exceeds svd_residual_tolerance, the function returns feasible=False / status="singular-infeasible" with no fabricated burn; where the boundary condition is genuinely within the reachable SVD column space, it returns the documented "singular-reachable" / non-unique result -- using the labels and fields two_burn_targeting actually returns, not assumed ones
- [ ] #5 A property test sweeps alternative transfer durations near (but strictly not at) a known singular theta, within a bounded interval, and confirms targeting becomes well-conditioned/feasible moving away from that singular point -- consistent with the operator's own worked example (0.99/1.01 period offsets) -- without adding any automatic retiming/recovery logic to source code
- [ ] #6 Each property test follows TJC-5's documentation policy in full, including explicitly recording the distinction between mathematical singularity (exact rank loss, AC1) and the separate numerical CW_CONDITION_NUMBER_LIMIT routing heuristic as a stated assumption/limitation
- [ ] #7 Full existing test suite passes unchanged; new tests' runtime is bounded (explicit max_examples/deadline settings)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed 'TJC-6.1:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->
