---
id: TJC-6
title: Add Hypothesis property-based tests for the CW and two-body physics core
status: To Do
assignee: []
created_date: '2026-10-19 12:16'
labels: []
dependencies:
  - TJC-5
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The same test-suite audit found zero use of the hypothesis library anywhere in the repo (requirements-dev.txt lists only numpy/pytest/mss/python-xlib) despite the project explicitly wanting property-based tests "whenever appropriate" and preferring physical invariants over implementation-specific checks. The physics-critical core (src/cw.py, src/twobody.py, src/verify.py) already has strong example-based invariant tests (energy/angular-momentum conservation, STM identity/structure, LVLH orthonormality and round-trip invertibility) but only at a small number of hand-picked points, not swept across the input space. The audit named five concrete candidate properties: (1) CW STM group/composition structure and invertibility across random (n, t); (2) two-body energy/angular-momentum conservation across random valid (state0, mu, duration) triples, not just one fixed circular case; (3) LVLH-to-inertial/inertial-to-LVLH round-trip invertibility across random non-degenerate chief/relative states; (4) CW two-burn targeting terminal-state feasibility across random non-singular (n, t, state0); (5) model-selector qualified/selection monotonicity as relative_separation_m increases past the locality threshold. This task adds Hypothesis-driven tests for these properties without replacing or removing the existing example-based tests, which remain valuable as fixed regression anchors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 hypothesis is added to requirements-dev.txt with an explicit pinned version, and the documented clean-checkout setup/test commands in README.md still work unchanged
- [ ] #2 A Hypothesis property test exists for src.cw.cw_stm covering composition (cw_stm(n, t1+t2) approximately equals cw_stm(n, t2) @ cw_stm(n, t1)) and invertibility (det close to the expected value) across a generated range of physically valid n and t, bounded away from already-known-and-tested singular transfer times
- [ ] #3 A Hypothesis property test exists for src.twobody.propagate_cartesian_state asserting specific_orbital_energy and specific_angular_momentum conservation across a generated range of valid initial states, central-body mu, and propagation durations, not only the single fixed circular LEO case the existing example-based test covers
- [ ] #4 A Hypothesis property test exists for src.verify's LVLH-inertial round-trip functions asserting the round-trip invariant holds across a generated range of non-degenerate chief states and relative states, extending beyond the single fixed example the existing test covers
- [ ] #5 A Hypothesis property test exists for src.cw.two_burn_targeting asserting the returned final relative state matches the requested target within numerical tolerance across a generated range of non-singular (n, t, state0) combinations
- [ ] #6 A Hypothesis property test exists for src.model_selector.select_model asserting that, holding all other required assumption items supported, selection/qualified status changes monotonically (not erratically) as relative_separation_m is swept from clearly-local to clearly-nonlocal
- [ ] #7 Every new property test follows this project's new red-then-green TDD evidence requirement (TJC-5): each one is written and run failing first against a stated reason, then passing, with both outputs recorded
- [ ] #8 The full existing test suite (currently 146 tests) continues to pass unchanged alongside the new property tests, and Hypothesis test run time is bounded (explicit max_examples or deadline settings) so the suite does not become slow or flaky
<!-- AC:END -->
