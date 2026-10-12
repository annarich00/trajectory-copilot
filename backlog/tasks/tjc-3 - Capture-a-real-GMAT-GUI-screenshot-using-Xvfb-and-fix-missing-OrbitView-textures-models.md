---
id: TJC-3
title: >-
  Capture a real GMAT GUI screenshot using Xvfb and fix missing OrbitView
  textures/models
status: To Do
assignee: []
created_date: '2026-10-12 15:14'
labels: []
dependencies:
  - TJC-2
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TJC-2 documented that GMAT-R2026a (GUI binary) genuinely launches and maps real windows under this environment's default WSLg-backed DISPLAY=:0, but every external screen-capture attempt against that display returns a byte-identical blank image, because WSLg's compositor does not expose its rendered buffer to standard X11 capture tools. The operator has now installed xvfb (plus x11-apps and imagemagick) system-wide via apt. A manual investigation (outside the normal implementation workflow) confirmed Xvfb resolves the core blocker: launching GMAT-R2026a against a manually started 'Xvfb :99 -screen 0 1920x1080x24 -nolisten unix -listen tcp' display (TCP listener used because /tmp/.X11-unix is mounted read-only in this environment, blocking Xvfb's default Unix-domain socket) and capturing via mss produced a real, non-blank screenshot: 68834 bytes with 256 unique pixel values (vs. ~3708 bytes with 1-2 unique values for every prior WSLg attempt), stable across repeated captures at 3s-20s waits. An Xlib window-tree walk located the real GMAT main window (0x20011e, 1024x768 at offset 32,32, titled 'General Mission Analysis Tool (GMAT)') and confirmed capturing that exact window region also works. However, the OrbitView 3D trajectory panel itself (a child widget at a sub-region of that window) rendered mostly black (only 14 unique pixel values) rather than showing the actual trajectory, and GmatLog.txt shows 'OpenFrames cannot find or cannot load the model ../data/vehicle/models/aura.3ds' and the same for the ModifiedBlueMarble Earth texture files -- so the capture mechanism itself now works, but the rendered content is currently missing its Earth texture and spacecraft model assets. This task productizes that manual investigation into src/gmat_verify.py's real implementation (replacing or supplementing the existing WSLg-only attempt_gmat_gui_screenshot path), and investigates/fixes the missing-asset rendering gap so the captured screenshot shows an actual visible orbit/trajectory, not just window chrome.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 attempt_gmat_gui_screenshot (or a clearly superseding function) launches and manages its own Xvfb virtual display (not relying on inheriting a pre-existing DISPLAY) so the real-screenshot attempt is self-contained and does not depend on manual setup
- [ ] #2 The Xvfb launch correctly handles this environment's read-only /tmp/.X11-unix (e.g. via -nolisten unix -listen tcp or an equivalent documented workaround) and is verified to actually start, not just assumed to start
- [ ] #3 The captured screenshot targets the real GMAT application window region (located via a window-tree walk, as manually verified) rather than the full virtual screen, and is validated to be non-blank using a real pixel-variance check, not merely non-empty-file
- [ ] #4 The missing OrbitView texture/spacecraft-model asset-loading issue (ModifiedBlueMarble.jpg, aura.3ds, and any other reported missing assets) is investigated and fixed or worked around so the captured screenshot's OrbitView panel shows actual visible orbit/trajectory content, with before/after evidence (pixel-variance or visual description) demonstrating the improvement; if a specific asset genuinely cannot be resolved, that exact blocker is documented as reproducible evidence rather than asserted
- [ ] #5 screenshot_source correctly reports 'gmat_gui' (not 'svg_fallback') for a real successful capture under this fixed pipeline, and tests cover the Xvfb-launch success path, the read-only-socket-directory workaround, and the asset-loading fix, in addition to the existing fallback/failure-mode tests
<!-- AC:END -->
