# TJC-18 Visual Review Checklist -- Two-Body Coast Scenario

Scenario: the bounded-two-body-fallback case from
`tests/test_workflow.py::_two_body_ready_case` (`leo_radius_m=6778000.0`,
`offset_m=1000000.0` => `chaser_radius_m=7778000.0`, circular `chaser_speed`
via `src.twobody.vis_viva_speed(MU_EARTH, chaser_radius_m, chaser_radius_m)`
= 7158.712455933824 m/s, `state0=[7778000.0, 0.0, 0.0, 0.0,
7158.712455933824, 0.0]`, `mu_m3_s2=MU_EARTH=398600441800000.0`,
`duration_s=900.0`). This scenario has no spacecraft-to-spacecraft
rendezvous and no impulsive burns -- it is a single-spacecraft bounded coast.

- Generated script: `artifacts/tjc18_verification/two_body_scenario/two_body_coast_gui_preview.script`
  (produced by `src.gmat_verify.generate_two_body_gui_preview_script`, unmodified call
  signature, using the exact fixture values above).
- Execution: `src.gmat_verify.attempt_gmat_gui_screenshot("GMAT-R2026a", <script>, <png>,
  render_wait_s=10.0)` against this exact script, under this worktree's installed
  GMAT R2026a binary and a self-managed Xvfb display (unmodified per TJC-17).
- Screenshot: `artifacts/tjc18_verification/two_body_scenario/trajectory_gmat_gui.png`
  (1024x768 real PNG, `attempted=True`, `captured=True`,
  `validate_gui_screenshot(...).ok == True`, 144807 bytes, 9007 distinct RGB
  values -- non-blank, real render -- including 32 near-cyan pixels matching
  the configured `Sat.OrbitColor = [0 255 255]`).

| # | Question | Result | Evidence |
|---|----------|--------|----------|
| 1 | Does the single generated script contain a global, Earth-centered orbital view? | PASS | `two_body_coast_gui_preview.script` contains `Create OrbitView GlobalView;` with `GlobalView.CoordinateSystem = EarthMJ2000Eq;` and `GlobalView.ViewDirection = Earth;`. |
| 2 | Does the same script contain a close-up view centered on the single spacecraft? | PASS | Same script contains `Create OrbitView CloseUpView;` with `CloseUpView.CoordinateSystem = SatCentered;` (an `ObjectReferenced` CS with `Origin = Sat;`, `Secondary = Sat;`), and `CloseUpView.ViewDirection = Sat;`. |
| 3 | Are both views produced by one generation request / one script (not separate scripts)? | PASS | Both `OrbitView` resources are written by the single `generate_two_body_gui_preview_script` call into the one `.script` file above; no second script file was generated for either view. |
| 4 | Is the spacecraft visually distinguishable (color)? | PASS (script-level and pixel-level) | Script sets `Sat.OrbitColor = [0 255 255];` (cyan). The captured PNG directly contains 32 pixels within tolerance of `[0,255,255]`, consistent with the spacecraft's orbit color appearing on screen -- a stronger pixel-level confirmation than was available for the CW scenario's Chief color. |
| 5 | Is a burn marker placed at the actual maneuvering spacecraft's position at the actual burn epoch? | NOT APPLICABLE | This scenario has no `ImpulsiveBurn`/`Maneuver` commands at all -- it is a single-spacecraft coast with zero maneuvers, so there is no burn to mark. `generate_two_body_gui_preview_script`'s own docstring and this task's brief both confirm maneuver visualization is out of scope here. |
| 6 | Is a delta-v vector shown, with correct direction/frame? | NOT APPLICABLE | No delta-v exists in this scenario (no burns). |
| 7 | Is the delta-v magnitude reported with units? | NOT APPLICABLE | No delta-v exists in this scenario (no burns). |
| 8 | Is the maneuvering spacecraft, burn number, epoch, and coordinate frame identified for each burn? | NOT APPLICABLE | No burns/maneuvers exist in this scenario. |
| 9 | Are pre-burn, transfer, and post-burn trajectory segments visually distinguishable? | NOT APPLICABLE | There is exactly one continuous coast segment (no burns to delimit pre/transfer/post arcs). |
| 10 | Was real GMAT GUI execution and screen capture (not script-parsing alone) performed for this scenario? | PASS | `attempt_gmat_gui_screenshot("GMAT-R2026a", two_body_coast_gui_preview.script, trajectory_gmat_gui.png, render_wait_s=10.0)` actually launched the real `GMAT-R2026a` binary against this exact script under a self-managed Xvfb display and returned `attempted=True`, `captured=True`, with `validate_gui_screenshot(...).ok == True` on the resulting 1024x768, 144807-byte PNG (non-uniform pixel content, 9007 distinct RGB values observed). |

## Summary

- Items 1-4 and 10 (multi-view structure, single-script generation, spacecraft
  color, real GUI execution/capture) all PASS for this scenario, with item 4
  additionally pixel-confirmed here (unlike the CW scenario's Chief color,
  which was not independently pixel-confirmed from its single-window
  capture).
- Items 5-9 (burn markers, delta-v vector, delta-v magnitude, burn
  identification, trajectory segment distinction) are explicitly NOT
  APPLICABLE to this scenario: `generate_two_body_gui_preview_script`
  generates a maneuver-free single-spacecraft coast (confirmed directly from
  its generated script and its own docstring), so there is no maneuver
  content for these items to evaluate. This is a scope statement, not a
  failure -- the CW scenario's checklist is where maneuver visualization
  (items 5-9) is actually exercised and graded.
