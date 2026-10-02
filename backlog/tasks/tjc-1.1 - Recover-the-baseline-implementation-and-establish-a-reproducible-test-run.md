---
id: TJC-1.1
title: Recover the baseline implementation and establish a reproducible test run
status: Done
assignee:
  - '@annarich00'
created_date: '2026-10-01 14:17'
updated_date: '2026-10-01 16:37'
labels: []
dependencies: []
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
modified_files:
  - .gitignore
  - README.md
  - requirements-dev.txt
  - docs/baseline-provenance.md
  - docs/baseline-checksums.md
  - .pi
  - skills
  - reference
  - src
  - tests
  - examples
  - evaluations
  - baseline_comparison.md
parent_task_id: TJC-1
priority: high
type: chore
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The planning document describes an existing Python package, Pi skills, examples, and passing tests, but this repository currently contains only Backlog configuration. Locate the authoritative implementation or obtain it from the project owner before any physics audit; preserve provenance and avoid recreating claimed work from memory.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The repository contains the documented source, tests, skills, reference material, and example cases, or a checked-in note explicitly identifies every unavailable artifact and its owner/location
- [x] #2 A documented setup command creates the supported environment from a clean checkout
- [x] #3 The complete baseline test command runs and its pass/fail result is recorded without hiding failures
- [x] #4 The recovered revision or source location is recorded for traceability
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Search local Linux and Windows user storage, archives, and Git metadata for the authoritative implementation described by the planning PDF.
2. If found, verify provenance and copy/import it without overwriting Backlog metadata; if not found, document the unavailable artifacts and searched locations.
3. Establish a clean-checkout environment/setup command and run the complete available baseline test suite without suppressing failures.
4. Record provenance, commands, results, and modified files; then verify each acceptance criterion before finalizing.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Recovered the matching baseline from `/home/anna_ford/trajectory-copilot`. The source has no Git metadata, revision, or remote, but its paths, file names, timestamps, and six-test result match the planning PDF. Inspected `/home/anna_ford/projects/trajectory-copilot` separately; it contains generated GMAT artifacts rather than the documented baseline and was intentionally not merged.

Imported `.pi/skills`, `skills`, `reference`, `src`, `tests`, `examples`, `evaluations`, and `baseline_comparison.md`, excluding virtual environments, caches, and bytecode. Added setup documentation, pinned baseline dependencies, ignore rules, provenance, and source-file checksums.

Source environment check: Python 3.12.14, NumPy 2.5.3, pytest 9.1.1; baseline command returned `6 passed in 0.52s`. Clean-export verification used Python 3.14.4 with `python3 -m venv .venv`, installed `requirements-dev.txt`, and returned `6 passed in 0.43s` without suppressed failures.

Final verification: all 21 imported files passed `sha256sum --check`; required module/test/reference/example/skill artifact checks passed; imported repository suite returned `6 passed in 0.84s`. The documented clean-export setup had independently returned `6 passed in 0.43s`.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Recovered the authoritative local Trajectory CoPilot baseline from `/home/anna_ford/trajectory-copilot` without recreating physics code. Imported the documented modules, tests, skills, reference, examples, and evaluation artifacts; added reproducible setup instructions, pinned baseline dependencies, provenance, and a SHA-256 manifest. Verified all imported checksums, required artifacts, the original baseline (`6 passed in 0.52s`), the imported suite (`6 passed in 0.84s`), and a clean environment setup (`6 passed in 0.43s`).
<!-- SECTION:FINAL_SUMMARY:END -->
