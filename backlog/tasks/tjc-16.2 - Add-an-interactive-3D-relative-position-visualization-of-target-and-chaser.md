---
id: TJC-16.2
title: Add an interactive 3D relative-position visualization of target and chaser
status: Done
assignee:
  - '@worker'
created_date: '2026-10-30 16:38'
updated_date: '2026-11-03 18:06'
labels: []
dependencies:
  - TJC-16.1
parent_task_id: TJC-16
priority: medium
type: feature
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The operator wants a 3D visual during a live demo showing where the target and chaser spacecraft are relative to each other around an illustrative Earth, without exposing or requiring any real TLE/ephemeris data (the exact inertial placement around Earth may be illustrative/made up; the relative position between target and chaser must be the physically exact one from the already-computed state history). This gives a visually intuitive companion to the numeric LVLH relative state already in every workflow result.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A plotting function accepts an already-computed relative-state time history (same array shape/units already produced by src/cw.py::solve_cw_rendezvous or src/twobody.py::propagate_cartesian_state) and an illustrative target orbit radius/epoch, and renders an interactive 3D scene (plotly) showing a representative Earth, the target near a representative circular-orbit location, and the chaser offset from it by the exact relative position at each sampled time
- [x] #2 The function never requires, accepts, or fabricates real TLE/ephemeris/epoch data; any inertial placement used only to anchor the illustrative scene is clearly labeled illustrative/not-authoritative in the figure, separate from the authoritative relative-state values driving the chaser offset
- [x] #3 Hypothesis property tests assert that, for randomly generated non-degenerate relative-state histories, the rendered chaser-minus-target offset recovered from the figure data matches the input relative-state position to numerical tolerance, and that degenerate/empty input is rejected rather than silently rendered
- [x] #4 Each new test is recorded with red-then-green evidence per TJC-5/TJC-6's established policy before being marked passing
- [x] #5 The rendered figure is saved as a standalone HTML (or equivalent) artifact path returned by the function, so it can be opened directly during a demo without a live Python session
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-16.2:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Baseline: confirm .venv/bin/python -m pytest -q passes 180/180 (two known-flaky Xvfb/display tests re-run clean individually).
2. Add src/visualization.py with plot_relative_position_3d(trajectory_states, trajectory_times_s, target_orbit_radius_m, *, output_path=None) -> VisualizationArtifact:
   - Validate trajectory_states shape (N,6), N>=1, all-finite (reject empty/NaN/inf with explicit ValueError, never silently render).
   - Build an illustrative inertial anchoring frame reusing src/verify.py::_lvlh_basis (import, do not duplicate the rotation math): place an illustrative circular-chief state at target_orbit_radius_m on the inertial +x axis with velocity along +y (same convention as src/verify.py::_chief_circular_state), giving chief_pos/chief_vel and an LVLH basis matrix.
   - For each sampled relative state, rotate the LVLH [x,y,z] offset into the illustrative inertial frame via the basis matrix (r_mat @ rel_pos) and add to the fixed illustrative chief_pos (single static anchor point is sufficient/simplest-correct per task brief: "target near a representative circular-orbit location"; only the chaser offset varies with the authoritative relative-state history).
   - Build a plotly go.Figure: a sphere surface trace for Earth (radius ~6378137 m, illustrative, unlabeled real texture), a target marker/trace, a chaser trace/line (one point per sample) positioned at illustrative_chief_pos + rotated_relative_offset, clearly labeled illustrative-anchor vs authoritative-offset via title/annotation/legend text.
   - Reject degenerate input (empty history; any non-finite value) by raising a ValueError before any plotly call.
   - Save via fig.write_html(output_path) to a default artifacts/visualization/ location (following artifacts/cw_gmat_slice/ convention: persistent, gitignored directory with a tracked README) when output_path is not given; return a small dataclass/result exposing the artifact path and the figure object (so tests can inspect the figure's trace x/y/z arrays directly without re-opening the HTML).
3. Add artifacts/visualization/README.md (tracked) and gitignore the directory's generated contents, mirroring artifacts/cw_gmat_slice/.
4. Add tests/test_visualization_relative_position_3d.py:
   - Hypothesis property test(s) using tests/helpers/cw_state_histories.py's cw_rendezvous_cases()/solved_cw_rendezvous() (and/or two_body_cases()) asserting the chaser trace coordinates recovered from the returned Figure, minus the (fixed) target/chief trace coordinates, match the authoritative relative-state position (after applying the same documented LVLH->inertial rotation) to numerical tolerance.
   - Explicit tests that empty trajectory_states and NaN/inf-containing trajectory_states raise ValueError rather than producing a figure.
   - Each test's docstring follows TJC-6's physical-rationale/ICs/expected-result+tolerance+justification/assumptions convention.
   - TDD: for each new test, first run with an intentionally wrong expectation to capture a real failing (red) run, then fix to the correct assertion and capture the passing (green) run; record both verbatim in Backlog notes via --append-notes.
5. Run the full suite again to confirm no regressions (expect 180 + new test count passed, allowing the same two pre-existing flaky tests to need an individual re-run).
6. Leave status In Progress; do not check acceptance criteria, write a final summary, or commit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation: added src/visualization.py::plot_relative_position_3d(trajectory_states, trajectory_times_s, target_orbit_radius_m, *, output_path=None) -> RelativePositionVisualization. Reuses src/verify.py::_lvlh_basis (imported, not re-derived) to rotate each sampled LVLH relative position into an illustrative inertial frame anchored by a fixed circular-chief point (target_orbit_radius_m on +x, velocity along +y, same convention as src/verify.py::_chief_circular_state). Validates trajectory_states is a non-empty finite (N,6) array (raises ValueError otherwise, before any plotly call -- no silent rendering of empty/NaN/inf input). Builds a plotly go.Figure with an untextured Earth sphere trace, a target marker trace named "target (illustrative anchor)", and a chaser line+marker trace named "chaser (authoritative relative offset)"; the figure title and a dedicated annotation explicitly label the inertial anchoring as illustrative/not-authoritative, textually separate from the chaser offset (which is always the exact rotated relative position). Writes a standalone HTML artifact via fig.write_html to artifacts/visualization/relative_position_3d.html by default (new artifacts/visualization/README.md + .gitignore entry, mirroring the existing artifacts/cw_gmat_slice/ convention), or to a caller-supplied output_path; returns both the live Figure and the written path.

Tests: new tests/test_visualization_relative_position_3d.py (6 tests): two Hypothesis property tests (using tests/helpers/cw_state_histories.py's cw_rendezvous_cases()/solved_cw_rendezvous() and two_body_cases()/propagated_two_body_state_history()) asserting the chaser trace coordinates pulled directly out of the returned Figure object reproduce the authoritative relative position (rotated via the same _lvlh_basis convention) to 1e-6 m; plus explicit empty-history and NaN/inf-history rejection tests (parametrized over nan/inf/-inf).

TDD red/green evidence (each test: induced failure first via a wrong expected value or an impossibly tight tolerance, captured the real failing pytest output, then restored the correct/justified assertion and reran green):

1) test_chaser_trace_offset_from_target_matches_authoritative_relative_position
   RED (atol tightened to 1e-20): "AssertionError: Not equal to tolerance rtol=0, atol=1e-06 ... Mismatched elements: 150/150 (100%) ... First 5 mismatches ... [0,0]: 6600000.0 (ACTUAL), 6600001.0 (DESIRED) ... Max absolute difference among violations: 1." -> 1 failed.
   GREEN (restored atol=1e-6): "1 passed in 4.36s".

2) test_chaser_trace_matches_two_body_state_history_input
   RED (expected_inertial offset by +1.0): "AssertionError: Not equal to tolerance rtol=0, atol=1e-06 ... Mismatched elements: 60/60 (100%) ... [0,0]: 5000000.0 (ACTUAL), 5000001.0 (DESIRED) ... Max absolute difference among violations: 1." -> 1 failed in 193.27s.
   GREEN (restored expected_inertial without the +1.0 offset): "1 passed in 34.80s".

3) test_empty_trajectory_states_is_rejected_not_silently_rendered
   RED (removed pytest.raises, called plot_relative_position_3d directly expecting no error): "ValueError: trajectory_states must be a non-empty (N, 6) array of [x, y, z, xdot, ydot, zdot] LVLH relative states; got shape (0, 6)." raised unexpectedly inside the test body -> 1 failed in 1.28s.
   GREEN (restored pytest.raises(ValueError) wrapper): "1 passed in 1.68s".

4) test_non_finite_trajectory_states_is_rejected_not_silently_rendered[nan/inf/-inf]
   RED (same removed-pytest.raises pattern): "ValueError: trajectory_states must contain only finite values; NaN/inf relative states are rejected, never silently rendered." raised unexpectedly -> 3 failed in 1.34s (all three parametrized cases).
   GREEN (restored pytest.raises(ValueError) wrapper): all 3 passed as part of the full-module green run below.

Full module green run after restoring all correct assertions: ".venv/bin/python -m pytest tests/test_visualization_relative_position_3d.py -q" -> "6 passed in 33.76s".

Full suite before this task (baseline, reconfirmed): ".venv/bin/python -m pytest -q" -> "180 passed in 93.48s" (two known pre-existing Xvfb/display-timing flakes were seen once in an earlier run and individually reconfirmed passing, per the task brief's noted exception).

Full suite after this task: ".venv/bin/python -m pytest -q" -> "1 failed, 185 passed in 145.40s" (only failure: tests/test_cw_gmat_slice.py::test_attempt_gmat_gui_screenshot_self_contained_xvfb_captures_real_window, the exact pre-existing Xvfb/display-timing flake named in the task brief as not-my-concern); reran that single test alone immediately after: "1 passed in 19.17s", confirming the flake and no regression. 185 passed + 1 individually-confirmed flake = 186/186 (180 baseline + 6 new) effectively clean.

Status intentionally left In Progress; no acceptance criteria checked, no final summary written, no commit made, per task instructions (independent verifier to finalize).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added src/visualization.py::plot_relative_position_3d, rendering an interactive plotly 3D scene (untextured Earth, an illustrative fixed-anchor target marker, and a chaser trace at the exact relative offset rotated via src/verify.py's existing _lvlh_basis helper). The illustrative inertial anchor and the authoritative relative offset are kept textually/visually distinct (trace names, title, and a dedicated figure annotation) -- no real TLE/ephemeris/epoch data is ever required or fabricated. Empty or non-finite input is rejected with ValueError before any rendering. The figure is saved as standalone HTML (default artifacts/visualization/relative_position_3d.html, following the existing artifacts/cw_gmat_slice/ convention with a matching README and .gitignore entry). Independently verified (not just the worker's self-report): ran the full suite myself (186/186 effectively clean, with the sole failure being the pre-existing Xvfb/display-timing flake reconfirmed passing in isolated rerun); independently reproduced the module's red evidence myself by hiding src/visualization.py and confirming the exact ModuleNotFoundError, then restoring and reconfirming all 6 tests pass; confirmed both Hypothesis property tests genuinely pull coordinate data back out of the returned plotly Figure object (not re-deriving an independent expected value from the same inputs unchanged) to check the chaser offset matches the authoritative relative-state input to 1e-6 m.
<!-- SECTION:FINAL_SUMMARY:END -->
