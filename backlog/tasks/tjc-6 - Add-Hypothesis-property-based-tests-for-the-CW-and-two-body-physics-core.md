---
id: TJC-6
title: Add Hypothesis property-based tests for the CW and two-body physics core
status: To Do
assignee: []
created_date: '2026-10-19 12:16'
updated_date: '2026-11-02 02:12'
labels: []
dependencies:
  - TJC-5
priority: high
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The same test-suite audit found zero use of the hypothesis library anywhere in the repo (requirements-dev.txt lists only numpy/pytest/mss/python-xlib) despite the project explicitly wanting property-based tests "whenever appropriate" and preferring physical invariants over implementation-specific checks. The physics-critical core (src/cw.py, src/twobody.py, src/verify.py) already has strong example-based invariant tests (energy/angular-momentum conservation, STM identity/structure, LVLH orthonormality and round-trip invertibility) but only at a small number of hand-picked points, not swept across the input space. Properties 2 (CW STM), 4 (two-body conservation), and 8 (RK4 convergence) below are grounded in specific MIT 16.346 Astrodynamics lectures (cited by number and equation in each test), with generated inputs constrained to each property's own documented physical validity domain (circular/near-circular reference, finite non-degenerate states, positive mean motion, etc., per the governing module's existing assumptions) rather than swept over arbitrary ranges. The symplectic property test (criterion 3) must derive its canonical-momentum transform from the CW rotating-frame Lagrangian using this repository's own state ordering ([x, y, z, xdot, ydot, zdot], x radial outward / y along-track / z cross-track) and must use the same mean motion n consistently when constructing T, evaluating Phi(n, t), and inverting T -- it verifies the transformed STM's symplectic property, not the raw position/velocity STM against the standard canonical J directly. CW-targeting singularity and near-singular conditioning behavior is tracked separately in the linked TJC-6.1 subtask so it is neither substituted by nor folded into these STM/targeting-feasibility properties, which are restricted to non-singular, well-conditioned generated cases. A Lagrange-coefficient closed-form two-body oracle (Lecture 4 F/G/Ft/Gt) was evaluated as an alternative independent reference and explicitly deferred: GMAT already independently compares both position and velocity for scoped benchmark/workflow cases (src/gmat_verify.py::compare_gmat_final_state), but the Hypothesis sweep itself currently relies on conservation invariants (criterion 4), which do not independently establish phase/timing accuracy for every generated case -- this is recorded here as a known limitation, not silently closed, and is not addressed by this task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 hypothesis is added to requirements-dev.txt with an explicit pinned version, and the documented clean-checkout setup/test commands in README.md still work unchanged
- [ ] #2 A Hypothesis property test exists for src.cw.cw_stm covering (a) composition (cw_stm(n, t1+t2) approximately equals cw_stm(n, t2) @ cw_stm(n, t1)) across a generated range of physically valid n and t, bounded away from already-known-and-tested singular transfer times, and (b) the STM inverse-partition identity Phi(t0, t) = Phi(t, t0)^-1, checked against the documented closed-form partition inverse derived independently from the block structure (not np.linalg.inv alone, and not two calls to the same cw_stm implementation compared only to each other); cites MIT 16.346 Lectures 19 and 26 as governing source
- [ ] #3 A dedicated symplectic property test exists that: (a) states the CW rotating-frame Lagrangian and derives the canonical momentum transform p_x = xdot - n*y, p_y = ydot + n*x, p_z = zdot via Euler-Lagrange, explicitly confirmed against this repository's [x, y, z, xdot, ydot, zdot] state ordering and radial/along-track/cross-track axis convention with no unexplained sign flips; (b) builds the transform matrix T and T^-1 using the same mean motion n used to build Phi(n, t) in the same generated test case; (c) asserts Phi_w^T * J * Phi_w = J for Phi_w = T * Phi * T^-1 across a generated range of valid (n, t), with n constrained to physically valid positive values; (d) documents, as prose/comment, why the untransformed position/velocity STM is not expected to satisfy canonical J directly (Coriolis coupling is not canonical in position/velocity coordinates); cites MIT 16.346 Lecture 19
- [ ] #4 A Hypothesis property test exists for src.twobody.propagate_cartesian_state asserting specific_orbital_energy and specific_angular_momentum conservation across a generated range of valid initial states, central-body mu, and propagation durations, not only the single fixed circular LEO case the existing example-based test covers; cites MIT 16.346 Lectures 1 and 2
- [ ] #5 A Hypothesis property test exists for src.verify's LVLH-inertial round-trip functions asserting the round-trip invariant holds across a generated range of non-degenerate chief states and relative states, extending beyond the single fixed example the existing test covers
- [ ] #6 A Hypothesis property test exists for src.cw.two_burn_targeting asserting the returned final relative state matches the requested target within numerical tolerance across a generated range of non-singular (n, t, state0) combinations; this property explicitly excludes singular/near-singular cases, which are covered by the linked TJC-6.1 subtask instead
- [ ] #7 A Hypothesis property test exists for src.model_selector.select_model asserting that, holding all other required assumption items supported, selection/qualified status changes monotonically (not erratically) as relative_separation_m is swept from clearly-local to clearly-nonlocal
- [ ] #8 A Hypothesis property test exists for src.twobody.propagate_cartesian_state (or kepler_propagate_state) asserting RK4 global-error convergence order: for generated valid two-body cases, the propagated final state at a fixed propagation time is compared at step counts h and h/2 against an independently established high-accuracy reference -- preferring scipy.integrate.solve_ivp (adaptive RK45/DOP853, confirmed installable in the core .venv independent of the isolated Poliastro environment) over a merely-finer run of the same RK4 implementation -- and the observed global error ratio is asserted consistent with 4th-order convergence within a documented, justified tolerance band; cites MIT 16.346 Lecture 33
- [ ] #9 Every property test above records, per TJC-5's policy: physical rationale, governing equation/lecture citation, initial conditions and units, expected result with tolerance and its justification, actual result, pass/fail, and assumptions/limitations -- including this task's deferred-Lagrange-oracle limitation and its generated-input-domain constraints
- [ ] #10 Every new property test follows this project's red-then-green TDD evidence requirement (TJC-5): each one is written and run failing first against a stated reason, then passing, with both outputs recorded
- [ ] #11 The full existing test suite (currently 146 tests) continues to pass unchanged alongside the new property tests, and Hypothesis test run time is bounded (explicit max_examples or deadline settings) so the suite does not become slow or flaky
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A single atomic Git commit (subject prefixed 'TJC-6:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->
