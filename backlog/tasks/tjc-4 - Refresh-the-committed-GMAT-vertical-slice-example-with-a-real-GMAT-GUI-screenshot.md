---
id: TJC-4
title: >-
  Refresh the committed GMAT vertical-slice example with a real GMAT GUI
  screenshot
status: Done
assignee:
  - '@worker'
created_date: '2026-10-14 14:07'
updated_date: '2026-10-14 14:29'
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
- [x] #1 examples/cw_gmat_slice_example/ is regenerated from a real run of scripts/run_cw_gmat_slice.py in this environment and now includes the real GMAT GUI PNG screenshot (trajectory_gmat_gui.png or equivalent) alongside its matching verification_result.json showing screenshot_source == 'gmat_gui' and comparison status PASS
- [x] #2 The committed example's verification_result.json and any README/caption text accurately describe the real GMAT GUI capture (not the SVG fallback) as the example's actual screenshot_source
- [x] #3 The educational site's #/cw-gmat-slice page displays or links the real GMAT GUI PNG as the example trajectory image, replacing or supplementing the prior SVG-only presentation, and is checked locally via ./run_site.sh
- [x] #4 If the real GMAT GUI capture is not reproducible in a given environment (e.g. CI without Xvfb/GMAT installed), the committed example still documents how it was produced and under what conditions it is expected to reproduce, rather than silently reverting to the SVG fallback without explanation
- [x] #5 tools/compare_upstream.py --check and tools/sync_site_data.py --check both pass after the refresh
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Set up venv + requirements-dev.txt in this worktree.
2. Run scripts/run_cw_gmat_slice.py with --gmat GmatConsole-R2026a --gmat-gui GMAT-R2026a --output-dir examples/cw_gmat_slice_example to regenerate the committed example with a real GMAT GUI PNG screenshot.
3. Verify verification_result.json shows screenshot_source=gmat_gui and comparison PASS; git add the new PNG, remove old trajectory.svg if superseded, confirm file sizes reasonable.
4. Update examples/cw_gmat_slice_example/README.md to describe the real GMAT GUI capture, reproduction command, and conditions needed (Xvfb+GMAT-R2026a+GmatConsole-R2026a) vs SVG fallback.
5. Update site/js/pages/cw-gmat-slice.js to display/link the real GMAT GUI PNG; check tools/sync_site_data.py MAPPINGS for an examples mirror under site/data and sync it.
6. Update site/data/project-progress.js with a TJC-4 entry.
7. Run pytest, tools/compare_upstream.py --check, tools/sync_site_data.py --check, and ./run_site.sh smoke test of #/cw-gmat-slice route.
8. Finalize backlog (check ACs, notes, final summary, Done) and make exactly one git commit 'TJC-4: ...' amending to include finalization metadata.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Regenerated examples/cw_gmat_slice_example/ with a real run of scripts/run_cw_gmat_slice.py (--gmat GmatConsole-R2026a --gmat-gui GMAT-R2026a, absolute --output-dir required since GMAT writes ReportFile output relative to its own bin/ working dir). Result: screenshot_source='gmat_gui', verified=true, comparison.status='PASS', position_error_m=0.007941212332207074, velocity_error_mps=1.1675120387351017e-05. Replaced trajectory.svg (deleted) with trajectory_gmat_gui.png (199193 bytes, non-blank, correctly-textured Earth/OrbitView render -- visually inspected). Relativized only the top-level input/trajectory_artifact/verification_report_path/artifact_storage_convention path fields in verification_result.json back to repo-relative paths (same convention as TJC-2's original commit); raw GMAT stdout/log text left verbatim. Updated README.md documenting exactly how/when this reproduces (reachable X display + GMAT-R2026a + GmatConsole-R2026a) vs the honest svg_fallback outcome otherwise. Updated site/js/pages/cw-gmat-slice.js to render the PNG via <img> (not TC.fetchText, which is for text mirrors) and describe TJC-3's asset-loading fix. Added '.png':'image/png' to site/server.js MIME map (previously missing -> PNG served as text/plain) and added site/server.js to tools/compare_upstream.py's APPROVED_LOCAL_SITE_ALIGNMENT set. Found and fixed in-scope fixture drift: evaluations/benchmark/case_a_straightforward_cw.json's reproducible_evidence block referenced the stale trajectory.svg/svg_fallback for this same reused example; updated to trajectory_gmat_gui.png/gmat_gui, confirmed by tests/test_benchmark_fixtures.py::test_committed_gmat_evidence_matches_fixture_references. Updated tools/sync_site_data.py MAPPINGS (trajectory.svg -> trajectory_gmat_gui.png) and ran python3 tools/sync_site_data.py to regenerate every affected site/data/ mirror. Verification: .venv/bin/python -m pytest -q -> 129 passed (zero regressions vs 129-passed baseline); python3 tools/compare_upstream.py --check -> exit 0 (content-different unaccounted: none); python3 tools/sync_site_data.py --check -> exit 0 (site data mirrors match, 50 mappings); ./run_site.sh / node site/server.js smoke test on port 4322 -> curl 200 for /, /js/pages/cw-gmat-slice.js, /data/examples/cw_gmat_slice_example/verification_result.json (screenshot_source=gmat_gui, verified=True), /data/examples/cw_gmat_slice_example/trajectory_gmat_gui.png (Content-Type: image/png confirmed), /data/evaluations/benchmark/case_a_straightforward_cw.json; server stopped cleanly after. Updated site/data/project-progress.js with a new TJC-4 'Completed' entry (own entry only) and bumped the top-level commitSubject/updated fields to match the new most-recent commit, consistent with every prior task's pattern in that file's git history.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Regenerated examples/cw_gmat_slice_example/ from a real run of scripts/run_cw_gmat_slice.py against GmatConsole-R2026a/GMAT-R2026a in this environment: verification_result.json now shows screenshot_source='gmat_gui', verified=true, comparison.status='PASS' (position_error_m=0.00794, velocity_error_mps=1.17e-05), with the real 199,193-byte trajectory_gmat_gui.png replacing the stale trajectory.svg fallback. Updated the example's README.md to accurately describe the real GMAT GUI capture and document exactly how/when it reproduces (reachable X display + GMAT-R2026a + GmatConsole-R2026a) versus the honest svg_fallback alternative otherwise. Updated site/js/pages/cw-gmat-slice.js to display the real PNG via an <img> tag and describe TJC-3's fix instead of the stale always-SVG-fallback narrative; added the missing '.png' MIME mapping to site/server.js and the matching compare_upstream.py allow-list entry. Found and fixed one in-scope fixture drift (evaluations/benchmark/case_a_straightforward_cw.json still referenced the old SVG/svg_fallback for this reused example) and resynced site/data/ mirrors via tools/sync_site_data.py. Verified with: pytest -q -> 129 passed (zero regressions); tools/compare_upstream.py --check -> pass; tools/sync_site_data.py --check -> pass; a local ./run_site.sh/node server.js smoke test confirming 200s and correct Content-Type: image/png for the new PNG, correct JSON fields, and the updated fixture. Added a TJC-4 entry to site/data/project-progress.js and bumped its top-level commitSubject/updated fields per the file's established pattern.
<!-- SECTION:FINAL_SUMMARY:END -->
