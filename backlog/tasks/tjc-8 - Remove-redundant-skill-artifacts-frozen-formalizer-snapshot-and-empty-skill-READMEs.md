---
id: TJC-8
title: >-
  Remove redundant skill artifacts: frozen formalizer snapshot and empty skill
  READMEs
status: Done
assignee:
  - '@pi'
created_date: '2026-10-19 12:56'
updated_date: '2026-10-19 13:00'
labels: []
dependencies: []
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A repository redundancy review found two leftover artifacts: (1) skills/orbital-problem-formalizer/SKILL.md is an untouched, frozen copy of the original pre-TJC-1.12 baseline import (checksum-identical to the recorded baseline manifest); the live, active formalizer skill actually loaded by Pi and used by all code/tests/site is .pi/skills/orbital-problem-formalizer/SKILL.md, which has since diverged (hardened under TJC-1.12). The top-level skills/ copy is not referenced by any code, test, or site page and only serves as a provenance snapshot that git history and docs/baseline-checksums.md already preserve, so it is safe to delete without losing provenance. (2) .pi/skills/orbital-model-selector/README.md and .pi/skills/orbital-targeting-planner/README.md are both 13-byte stub files containing only the text 'See SKILL.md.'; they carry no information beyond their SKILL.md siblings and are referenced only by docs/baseline-checksums.md's own manifest lines, so removing them (and the three obsolete checksum lines that referenced skills/orbital-problem-formalizer/SKILL.md and the two README stubs) requires no other code or doc updates.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 skills/orbital-problem-formalizer/SKILL.md and its now-empty skills/orbital-problem-formalizer/ and skills/ directories are removed
- [x] #2 .pi/skills/orbital-model-selector/README.md and .pi/skills/orbital-targeting-planner/README.md are removed
- [x] #3 docs/baseline-checksums.md no longer lists checksum lines for the three removed files
- [x] #4 tools/compare_upstream.py --check and the full pytest suite still pass after the removal
- [x] #5 No other file (code, test, docs, or site mirror) references any of the three removed files
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove skills/orbital-problem-formalizer/SKILL.md and the now-empty skills/orbital-problem-formalizer/ and skills/ directories.
2. Remove .pi/skills/orbital-model-selector/README.md and .pi/skills/orbital-targeting-planner/README.md (both empty 'See SKILL.md.' stubs).
3. Edit docs/baseline-checksums.md to drop the three checksum lines for the removed files.
4. Grep the repository for any remaining reference to the three removed paths and confirm none exist (already verified none do besides the checksum manifest).
5. Run tools/compare_upstream.py --check and the full pytest suite; record results.
6. Finalize Backlog (check ACs, add notes/summary, mark Done) and make one atomic TJC-8 commit, then push to origin/master.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Removed skills/orbital-problem-formalizer/SKILL.md (frozen, checksum-identical duplicate of the pre-TJC-1.12 baseline import; verified byte-identical to docs/baseline-checksums.md's recorded hash before deletion) and its now-empty skills/orbital-problem-formalizer/ and skills/ directories. Removed .pi/skills/orbital-model-selector/README.md and .pi/skills/orbital-targeting-planner/README.md (both 13-byte 'See SKILL.md.' stubs). Dropped the three corresponding lines from docs/baseline-checksums.md. Added the three paths to tools/compare_upstream.py's APPROVED_TASK_OWNED_DIFFERENCES (with a comment) so the upstream-diff check records this as a deliberate, provenance-preserved removal rather than an unaccounted drift. Verified: tools/compare_upstream.py --check passes (0 unaccounted differences); tools/sync_site_data.py --check passes (62 mappings, site unaffected since none of the removed files were site-mirrored); full pytest suite passes (146 passed); git diff --check passes; grep across all tracked code/test/docs/site files confirms zero remaining references to the three removed paths outside this task's own description/plan and compare_upstream.py's intentional provenance comment.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Deleted the frozen, unused duplicate formalizer skill (skills/orbital-problem-formalizer/SKILL.md, superseded by the actively-loaded and since-hardened .pi/skills/orbital-problem-formalizer/SKILL.md) and two empty 'See SKILL.md.' README stubs under .pi/skills/orbital-model-selector/ and .pi/skills/orbital-targeting-planner/. Updated docs/baseline-checksums.md and tools/compare_upstream.py to reflect the intentional removal while preserving provenance via Git history. Verified with tools/compare_upstream.py --check, tools/sync_site_data.py --check, and the full pytest suite (146 passed) — all green, no unrelated references left dangling.
<!-- SECTION:FINAL_SUMMARY:END -->
