---
id: TJC-4
title: >-
  Refresh the committed GMAT vertical-slice example with a real GMAT GUI
  screenshot
status: To Do
assignee: []
created_date: '2026-10-14 14:07'
labels: []
dependencies: []
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TJC-3 just made src/gmat_verify.py::attempt_gmat_gui_screenshot actually succeed end-to-end in this environment: a live run of scripts/run_cw_gmat_slice.py now produces a real, non-blank, correctly-textured GMAT GUI (OrbitView/OpenFrames) PNG screenshot (screenshot_source == 'gmat_gui', GMAT comparison status PASS), not the deterministic SVG fallback. The one committed, always-available example directory (examples/cw_gmat_slice_example/, tracked in git per artifacts/cw_gmat_slice/README.md's convention) and the educational site's #/cw-gmat-slice demo page still show/link only the older trajectory.svg fallback artifact and its matching verification_result.json, predating this fix. A reader following the site's own example cannot currently see evidence of the real GMAT GUI capture this project now actually supports.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 examples/cw_gmat_slice_example/ is regenerated from a real run of scripts/run_cw_gmat_slice.py in this environment and now includes the real GMAT GUI PNG screenshot (trajectory_gmat_gui.png or equivalent) alongside its matching verification_result.json showing screenshot_source == 'gmat_gui' and comparison status PASS
- [ ] #2 The committed example's verification_result.json and any README/caption text accurately describe the real GMAT GUI capture (not the SVG fallback) as the example's actual screenshot_source
- [ ] #3 The educational site's #/cw-gmat-slice page displays or links the real GMAT GUI PNG as the example trajectory image, replacing or supplementing the prior SVG-only presentation, and is checked locally via ./run_site.sh
- [ ] #4 If the real GMAT GUI capture is not reproducible in a given environment (e.g. CI without Xvfb/GMAT installed), the committed example still documents how it was produced and under what conditions it is expected to reproduce, rather than silently reverting to the SVG fallback without explanation
- [ ] #5 tools/compare_upstream.py --check and tools/sync_site_data.py --check both pass after the refresh
<!-- AC:END -->
