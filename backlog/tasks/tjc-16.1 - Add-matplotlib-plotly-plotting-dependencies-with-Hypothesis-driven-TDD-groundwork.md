---
id: TJC-16.1
title: >-
  Add matplotlib/plotly plotting dependencies with Hypothesis-driven TDD
  groundwork
status: Done
assignee:
  - '@worker'
created_date: '2026-10-30 16:38'
updated_date: '2026-11-03 15:32'
labels: []
dependencies:
  - TJC-6
parent_task_id: TJC-16
priority: medium
type: task
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
None of the visualization subtasks under this parent can start until plotting/property-testing libraries exist in this project. `requirements-dev.txt` currently pins only numpy/pytest/mss/python-xlib (confirmed by inspection); hypothesis is also still absent despite TJC-6 already documenting that gap for the physics core. This task is the shared, one-time dependency and test-scaffolding setup other visualization subtasks depend on, so each of them can add Hypothesis property tests and plotting code immediately instead of repeating setup.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 matplotlib and/or plotly (whichever the chosen 3D-earth and 2D-plot subtasks actually need) are added to requirements-dev.txt with explicit pinned versions, and the documented clean-checkout setup/test commands in README.md still work unchanged
- [x] #2 hypothesis is added to requirements-dev.txt with an explicit pinned version if not already added by TJC-6 by the time this task starts
- [x] #3 A shared test-only helper or fixture module exists for generating valid CW/two-body state histories (reusing src/cw.py::solve_cw_rendezvous and src/twobody.py::propagate_cartesian_state outputs) for use by this task's sibling visualization subtasks' Hypothesis tests, documented in one place rather than duplicated per subtask
- [x] #4 The full existing test suite continues to pass unchanged after the new dependencies are added
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-16.1:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read full task + sibling TJC-16.2/16.3/16.4 ACs to decide which plotting lib(s) each needs (plotly for 16.2's interactive 3D HTML scene; matplotlib for 16.3/16.4's PNG/SVG/annotated 2D-3D static-style trajectory and error-history plots -- existing src/workflow.py::_write_two_body_svg is a hand-rolled SVG writer, not matplotlib-based, so this is a genuinely new dependency, not a duplicate of an existing capability).
2. Confirm hypothesis/scipy already present in requirements-dev.txt from TJC-6 (AC2).
3. Add matplotlib==3.11.2 and plotly==7.1.0 pinned to requirements-dev.txt (AC1); verify by installing in the existing worktree venv AND a separate throwaway clean-checkout venv following README.md's documented setup commands verbatim, then running the full suite in both.
4. Create tests/helpers/cw_state_histories.py exposing Hypothesis strategies (cw_rendezvous_cases, two_body_cases) and plain helper functions (solved_cw_rendezvous, propagated_two_body_state_history) wrapping src/cw.py::solve_cw_rendezvous and src/twobody.py::propagate_cartesian_state, following tests/test_physics_properties.py's established strategy/docstring conventions (AC3).
5. Add a small smoke test (tests/test_cw_state_histories_helpers.py) confirming the helper module produces non-degenerate, finite state histories, applying TDD red-then-green since this is a genuinely new automated test (docs/testing-policy.md).
6. Run the full suite to confirm baseline 167 plus the new smoke tests pass unchanged (AC4).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Library choice: read TJC-16.2/16.3/16.4 ACs directly. TJC-16.2 AC1/AC5 explicitly require an interactive 3D scene saved as standalone HTML -> plotly. TJC-16.3 AC1/AC6 require a 2D/3D LVLH-or-inertial trajectory plot with annotated burn markers/delta-v vectors saved as PNG/SVG/HTML, and TJC-16.4 AC1/AC2/AC6 require overlaid position trajectories plus position/velocity error-history plots with a drawn tolerance reference line, saved to artifact path(s) -- both are static-annotation-heavy demo plots consistent with this project's existing src/workflow.py::_write_two_body_svg hand-rolled-SVG convention (confirmed by inspection: that function is a bespoke polyline/circle SVG writer, not matplotlib-based, so matplotlib is a genuinely new capability, not a duplicate). Chose matplotlib for 16.3/16.4 (richer annotated 2D/3D static-style plotting, native PNG/SVG save, no new runtime JS dependency for a demo artifact that is mostly viewed as an image) and plotly for 16.2 (only plotly satisfies the standalone-interactive-HTML requirement). Added both, pinned, to requirements-dev.txt.

AC1 verification: installed matplotlib==3.11.2 and plotly==7.1.0 (pip index showed these as current latest pinned releases) into the existing .venv via '.venv/bin/python -m pip install --resume-retries 5 matplotlib==3.11.2 plotly==7.1.0' (network required one retry due to a transient download timeout, unrelated to the packages themselves); full suite then ran 167/167 passed. Separately rsynced the whole worktree (excluding .venv/.git/__pycache__/site) to a throwaway /tmp clean checkout and ran README.md's documented clean-checkout commands verbatim: 'python3 -m venv .venv && .venv/bin/python -m pip install -r requirements-dev.txt && .venv/bin/python -m pytest -q' end to end -- install succeeded with the new pins present, and the full suite passed 167/167 on a second run (first run showed 2 unrelated Xvfb/display-timing flakes -- test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window and test_result_record_includes_all_ac5_required_fields -- both passed individually and on a full-suite rerun, confirming they are the known display-timing flakiness called out in the task brief, not caused by this change).

AC2: hypothesis==6.145.1 and scipy==1.17.0 were already present in requirements-dev.txt (landed by TJC-6, confirmed via 'cat requirements-dev.txt' before any edit) -- AC2 was already trivially satisfied by this worktree's branch point; no line was added or duplicated for it.

AC3: created tests/helpers/cw_state_histories.py (new tests/helpers/__init__.py package) exposing two Hypothesis strategies -- cw_rendezvous_cases() (generates (mu, reference_radius_m, state0, t_final, target) over the same domain as tests/test_physics_properties.py's CW targeting property, excluding the documented Phi_rv singularities via the same n*t-mod-pi assume guard) and two_body_cases() (generates (mu, radius_m, state0, dt) over the same domain as that module's two-body conservation property, reusing its exact _random_bound_two_body_state construction) -- plus two plain helper functions that turn a generated case into an actual solved/propagated history ready for a plotting function: solved_cw_rendezvous(...) wraps src/cw.py::solve_cw_rendezvous directly, and propagated_two_body_state_history(...) calls src/twobody.py::propagate_cartesian_state once per sample time (since that function only returns a final state, not a history) to build a sampled (times, states) array analogous to solve_cw_rendezvous's own trajectory_states field. No production src/ code was touched; this is pure test infrastructure for TJC-16.2/16.3/16.4's own future Hypothesis tests to import.

TDD evidence (docs/testing-policy.md) for the new smoke test tests/test_cw_state_histories_helpers.py (genuinely new automated test, so red-then-green applies): RED -- 'pytest -q tests/test_cw_state_histories_helpers.py' before tests/helpers/cw_state_histories.py existed -> ModuleNotFoundError: No module named 'tests.helpers.cw_state_histories' (collection error), confirming the test genuinely exercises the not-yet-created helper module, not an unrelated typo. GREEN -- after implementing tests/helpers/cw_state_histories.py, 'pytest -q tests/test_cw_state_histories_helpers.py' -> 2 passed (first attempt hit a Hypothesis DeadlineExceeded on the two-body history helper at the default RK4 step count of 2000/sample; reduced propagated_two_body_state_history's default steps_per_sample to 200, still far more than enough RK4 accuracy for a test-only history-building helper, and reran -> 2 passed in 6.34s). Full suite after the fix: 169 passed (167 baseline + 2 new), both in the worktree venv and matching the throwaway clean-checkout venv's rerun (AC4).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added matplotlib==3.11.2 (for TJC-16.3/16.4's annotated PNG/SVG trajectory and error-history plots) and plotly==7.1.0 (for TJC-16.2's standalone-interactive-HTML 3D scene requirement) to requirements-dev.txt, chosen by reading the three sibling subtasks' actual acceptance criteria rather than guessing. hypothesis/scipy were already present from TJC-6 (AC2 trivially satisfied). Created tests/helpers/cw_state_histories.py exposing two Hypothesis strategies (cw_rendezvous_cases, two_body_cases) and two plain helper functions (solved_cw_rendezvous, propagated_two_body_state_history) wrapping src/cw.py::solve_cw_rendezvous and src/twobody.py::propagate_cartesian_state, so TJC-16.2/16.3/16.4 can import shared, non-degenerate generated state histories instead of each duplicating setup. A new smoke test (tests/test_cw_state_histories_helpers.py) confirms the helper module itself. Independently verified (not just the worker's self-report): confirmed matplotlib==3.11.2/plotly==7.1.0 are each PyPI's actual latest available version; built a fresh throwaway clean checkout myself (not reusing the worker's) with only git-tracked files plus the new untracked files, ran README.md's documented setup commands verbatim, and got 169/169 passing (167 baseline + 2 new); independently reproduced the smoke test's red evidence myself by hiding tests/helpers/cw_state_histories.py and confirming the exact ModuleNotFoundError, then restoring and reconfirming 2/2 green. No src/ or sibling TJC-16.2/16.3/16.4 plotting functionality was implemented, per this task's scope.
<!-- SECTION:FINAL_SUMMARY:END -->
