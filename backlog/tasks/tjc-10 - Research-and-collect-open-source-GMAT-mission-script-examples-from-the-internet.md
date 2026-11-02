---
id: TJC-10
title: >-
  Research and collect open-source GMAT mission-script examples from the
  internet
status: Done
assignee:
  - '@agent'
created_date: '2026-10-28 13:33'
updated_date: '2026-11-02 19:25'
labels: []
dependencies: []
priority: low
type: task
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A classmate brainstorming session proposed a future GMAT-example subagent (see the planned follow-up task) that reviews this project's generated GMAT scripts (src/gmat_verify.py::generate_gmat_script / generate_two_body_coast_script / generate_gmat_gui_preview_script) against real-world open-source GMAT usage, so it can tell the workflow agent whether its formatting/structure matches established practice for the request's mission type. That subagent needs a corpus to draw from. This task is the research step only: search the internet for open-source GMAT script examples (the official GMAT repository's sample missions, GMAT wiki/tutorial scripts, university/lab astrodynamics course repositories, and any other clearly-licensed public GMAT .script examples), across multiple mission types/formatting conventions (not just CW rendezvous), and collect them with enough provenance to reuse later. This task does not build the subagent-readable file itself (that is the next task) and does not change any code in src/ or scripts/.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A written list/log of at least 10 distinct open-source GMAT script examples is produced, spanning more than one mission type (e.g. not all rendezvous) and more than one source repository
- [x] #2 Each collected example records its source URL, license (or explicit 'license unknown/unclear' when not determinable), and a short description of what the script demonstrates
- [x] #3 Raw collected script text/files are saved under a clearly labeled research-staging location (e.g. research/gmat_examples_raw/) distinct from this project's own authoritative src/ and examples/ directories, so there is no ambiguity about what is this project's own code versus externally sourced reference material
- [x] #4 Sources with no discoverable license or an incompatible license are flagged explicitly rather than silently included, so the next task can decide what is safe to redistribute inside this repository
- [x] #5 No existing src/, scripts/, tests/, or examples/ file is modified by this task
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 A single atomic Git commit (subject prefixed 'TJC-10:') contains this task's implementation, tests, and finalized Backlog metadata, per docs/task-commit-policy.md
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Test internet access (curl github.com, api.github.com, raw.githubusercontent.com) before collecting anything.
2. Identify official nasa/GMAT repo and confirm its license (Apache-2.0) via GitHub API.
3. List application/samples directory in nasa/GMAT and select a diverse set of .script examples spanning multiple mission types (orbit transfer, lunar transfer/swingby, finite/electric propulsion, attitude pointing, Mars orbit, station-keeping).
4. Search GitHub repository search for other independent GMAT-script repos (university/lab/personal astrodynamics projects) and check each candidate repo's license via the GitHub API license endpoint before fetching.
5. Fetch raw script files via raw.githubusercontent.com into research/gmat_examples_raw/<source>/, verifying content looks like real GMAT script text (not an error page) by inspecting headers.
6. Write research/gmat_examples_log.md recording >=10 examples spanning >1 mission type and >1 source repo, with source URL, license status (explicitly flagging unknown/unclear licenses), and a short description for each.
7. Verify no src/, scripts/, tests/, or examples/ files were modified (git status check) before finishing.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Confirmed internet access works from this sandbox (curl to github.com, api.github.com, raw.githubusercontent.com all succeeded; gmat.atlassian.net wiki returned HTTP 200 but is a JS-rendered SPA with no extractable static script text, so it was not used as a source).

Collected 18 real GMAT .script examples from 4 distinct source repositories (exceeds the >=10 / >1 mission type / >1 source repo requirement):
- nasa/GMAT (official repo, application/samples/) - Apache-2.0 licensed (confirmed via GitHub API license endpoint). 12 scripts covering Hohmann transfer, lunar transfer, lunar-capture targeting, LCROSS lunar-impact reproduction, finite burn, electric propulsion, nadir-pointing attitude, spinner attitude, Mars orbit constellation, lunar swingby (MMS), LEO station-keeping, and the official 'Simple Orbit Transfer' tutorial.
- TridibeshChattoraj/GMAT_Mission_Portfolio - NO license file found (GitHub API license=null); flagged license unknown/unclear. 4 scripts: LEO/ISS propagation+visualization, ESOC ground-station contact analysis, elliptical-orbit propagation, SSO/inclination study.
- hannxmarie/impulsive_manoeuvres_interplanetary - NO license file found; flagged unknown/unclear. 1 script: Earth-Mars interplanetary transfer with B-plane targeting.
- iamxanadu/GMAT-SaturnIcyMoonExplorer - NO license file found; flagged unknown/unclear. 1 script: Saturn-system (Enceladus/Titan) mission with user-defined bodies and SPICE kernels.

All raw files saved under research/gmat_examples_raw/<source>/ (verified to contain real fetched script text, not error pages, by inspecting headers of each file). Full index with URLs, license status (including explicit unknown/unclear flags for 3 of 4 sources), and descriptions written to research/gmat_examples_log.md. Also noted repos investigated but not used because they had no .script file (VeluRagavendraS formation-flying repo) or were unreachable statically (GMAT wiki).

Verified via git status that no src/, scripts/, tests/, or examples/ file was modified - only backlog/tasks/TJC-10's own metadata file (status/plan/notes) and the new research/ directory changed. Left task In Progress; not checking acceptance criteria or writing a final summary per instructions, deferring to independent verifier.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Collected 18 real open-source GMAT .script examples (exceeds the required 10) from 4 distinct GitHub repositories, spanning 9 distinct mission types (Hohmann/orbit transfer, lunar transfer/swingby/impact, finite/electric propulsion, nadir/spinner attitude pointing, Mars orbit constellation, LEO station-keeping, LEO/elliptical/SSO propagation, ground-station contact analysis, Earth-Mars interplanetary B-plane targeting, Saturn/Enceladus outer-planet exploration). Verified: internet access confirmed live (curl to github.com/api.github.com/raw.githubusercontent.com); each of the 18 raw .script files fetched and saved under research/gmat_examples_raw/<source>/ (252K total, confirmed non-error-page content); research/gmat_examples_log.md records source URL, license status, and description for every example. Only nasa/GMAT (12 scripts) has a confirmed compatible license (Apache-2.0, verified via GitHub API); the other 3 repos (6 scripts) are explicitly flagged 'license unknown/unclear' per AC4 since GitHub reports license:null and no LICENSE file exists in any of them. Confirmed via 'git diff --name-only -- src/ scripts/ tests/ examples/' that this task modified none of those directories -- only the new research/ directory and this task's own Backlog metadata changed.
<!-- SECTION:FINAL_SUMMARY:END -->
