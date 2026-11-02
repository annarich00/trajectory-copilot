# TJC-18 Visual Review Checklist -- CW Rendezvous Scenario

Scenario: `circular_leo_quarter_orbit_rendezvous` (the same case used by
`scripts/run_cw_gmat_slice.py`'s default `--case examples/cw_gmat_vertical_slice.yaml`:
`radius_m=6728000.0`, `state0=[15.0, -200.0, 0.0, -0.14, 0.0, 0.0]`,
`transfer_fraction=0.25`).

- Generated script: `artifacts/tjc18_verification/cw_scenario/cw_rendezvous_gui_preview.script`
  (produced by `src.gmat_verify.generate_gmat_gui_preview_script`, unmodified call
  signature, real solved `dv0_mps`/`dv1_mps` from `src.cw.solve_cw_rendezvous`).
- Execution: `src.gmat_verify.attempt_gmat_gui_screenshot("GMAT-R2026a", <script>, <png>,
  render_wait_s=10.0)` against this exact script, under this worktree's installed
  GMAT R2026a binary and a self-managed Xvfb display (unmodified per TJC-17).
- Screenshot: `artifacts/tjc18_verification/cw_scenario/trajectory_gmat_gui.png`
  (1024x768 real PNG, `attempted=True`, `captured=True`,
  `validate_gui_screenshot(...).ok == True`, 73011 bytes, non-uniform pixel content
  confirmed directly -- not a blank/placeholder image).

**Note on source of the "ten questions":** no standalone document containing the
operator's exact ten-question wording was found in this worktree (not in
`backlog/`, not elsewhere in the repo); only the condensed description in the
TJC-18 task body (AC1/AC3/AC4) was available. The ten items below are derived
directly from that AC text's enumerated visualization requirements. Each item is
graded strictly from the actual script content and the actual captured
screenshot/pixel evidence above -- no claim is made beyond what was directly
observed.

| # | Question | Result | Evidence |
|---|----------|--------|----------|
| 1 | Does the single generated script contain a global, Earth-centered orbital view? | PASS | `cw_rendezvous_gui_preview.script` contains `Create OrbitView GlobalView;` with `GlobalView.CoordinateSystem = EarthMJ2000Eq;` and `GlobalView.ViewDirection = Earth;`. |
| 2 | Does the same script contain a Chief-centered close-up view? | PASS | Same script contains `Create OrbitView CloseUpView;` with `CloseUpView.CoordinateSystem = ChiefCentered;` (an `ObjectReferenced` CS with `Origin = Chief;`, `Secondary = Chief;`), and `CloseUpView.ViewDirection = Chief;`. |
| 3 | Are both views produced by one generation request / one script (not separate scripts)? | PASS | Both `OrbitView` resources are written by the single `generate_gmat_gui_preview_script` call into the one `.script` file above; no second script file was generated for either view. |
| 4 | Are Chief and Deputy visually distinguishable (color)? | PASS (script-level); NOT CONFIRMED (pixel-level) | Script sets `Chief.OrbitColor = [0 255 255];` (cyan) and `Deputy.OrbitColor = [255 0 0];` (red) -- confirmed real, documented GMAT properties. The captured PNG does contain pixels matching near-red (528 px within tolerance of `[255,0,0]`), consistent with the Deputy's orbit color appearing on screen, but no near-cyan pixels were found in this particular single-window capture, so Chief's color is not independently pixel-confirmed from this screenshot alone. |
| 5 | Is a burn marker placed at the actual maneuvering spacecraft's position at the actual burn epoch, for both burns? | PASS (script-level); NOT INDEPENDENTLY PIXEL-CONFIRMED | Script places `MarkPoint BurnMarkers;` immediately after each `Maneuver Burn1(Deputy);` and `Maneuver Burn2(Deputy);` command, so each marker fires at the true burn epoch in the Mission Sequence's execution order (t=0 and t=transfer_s respectively). The screenshot captures the main GMAT application window at one point in time; it was not decomposed frame-by-frame to visually isolate each marker event, so this remains script/sequence-level evidence rather than an isolated per-marker pixel check. |
| 6 | Is a delta-v vector (not just a marker) shown, with correct direction/frame? | NOT SUPPORTED NATIVELY (documented fallback) | No native GMAT R2026a OrbitView primitive for an arbitrary 3D delta-v arrow/vector glyph was found or used; `MarkPoint` only places a point marker on an `XYPlot`, not a direction vector in the 3D OrbitView. As a companion, the script documents the actual delta-v vector components and frame in a `%`-comment block directly above `BeginMissionSequence;` (see item 8) and in `BurnMarkers`'s `Deputy.LVLH.X` series, which is at least frame-correct (LVLH) even though it is not a rendered 3D arrow. This limitation is explicit, not claimed as complete. |
| 7 | Is the delta-v magnitude reported with units? | PASS | The `%` comment block reports, e.g., `Burn 1 ... magnitude: 0.000049928 km/s.` and `Burn 2 ... magnitude: 0.000163798 km/s.`, computed via `math.sqrt(dv0_1**2+dv0_2**2+dv0_3**2)` from the same `dv0_mps`/`dv1_mps` already used to build `Burn1`/`Burn2`, with explicit `km/s` units. |
| 8 | Is the maneuvering spacecraft, burn number, epoch, and coordinate frame identified for each burn? | PASS | Comment block identifies `spacecraft: Deputy`, `Burn 1`/`Burn 2`, `epoch: t = 0.000000000 s` / `t = 1373.029800507 s`, and `LVLH ObjectReferenced frame` explicitly for both burns. |
| 9 | Are pre-burn, transfer, and post-burn trajectory segments visually distinguishable? | NOT SUPPORTED (documented limitation) | No per-segment trajectory coloring/style was added; `Chief`/`Deputy` keep one `OrbitColor` each for their entire propagated arc in both `OrbitView` resources, so the three segments are not rendered as distinct colors/styles in this script. This is an explicit, undone gap, not claimed complete. |
| 10 | Was real GMAT GUI execution and screen capture (not script-parsing alone) performed for this scenario? | PASS | `attempt_gmat_gui_screenshot("GMAT-R2026a", cw_rendezvous_gui_preview.script, trajectory_gmat_gui.png, render_wait_s=10.0)` actually launched the real `GMAT-R2026a` binary against this exact script under a self-managed Xvfb display and returned `attempted=True`, `captured=True`, with `validate_gui_screenshot(...).ok == True` on the resulting 1024x768, 73011-byte PNG (non-uniform pixel content, 3384 distinct RGB values observed). |

## Summary of unresolved/partial items (for AC3/AC7(f) transparency)

- **Delta-v vectors (item 6):** not natively available as a 3D arrow glyph in
  GMAT R2026a's `OrbitView`; the companion fallback is the documented
  comment-block + `BurnMarkers` `XYPlot` series, not a rendered vector. A true
  3D vector overlay would require either a custom OpenFrames plugin or an
  external post-processing visualization, both out of this task's scope
  (no new rendering framework, per AC6).
- **Segment distinction (item 9):** not implemented; would require either
  per-arc spacecraft duplication (e.g. separate `Spacecraft` resources per
  segment) or a scripted color-change mid-sequence, which was judged beyond
  this task's "upgrade the two existing GUI generators" scope without
  explicit approval, so it is left as a documented gap rather than
  guessed at.
- **Per-window/per-view pixel isolation (items 4-5):** this task's single
  `attempt_gmat_gui_screenshot` call (per the brief's explicit instruction to
  use it "as-is, do not modify it") captures GMAT's one located main
  application window at a single point in time; it does not independently
  isolate and re-capture the `GlobalView` vs. `CloseUpView` OrbitView
  sub-windows or each `MarkPoint` event separately. The *script-level*
  evidence (both `OrbitView` resources present, correct `OrbitColor`
  assignments, `MarkPoint` placed at both burns) is solid; the *pixel-level*
  evidence is partial, as stated per-item above.
