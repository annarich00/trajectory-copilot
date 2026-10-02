---
id: TJC-1.2
title: Align the controlled reference and skills to the scoped rendezvous workflow
status: To Do
assignee: []
created_date: '2026-10-01 14:18'
updated_date: '2026-10-02 14:11'
labels: []
dependencies:
  - TJC-1.25
references:
  - /mnt/c/Users/Anna Ford/Downloads/Planning_Trajectory_Copilot.pdf
parent_task_id: TJC-1
priority: high
type: docs
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reconcile the recovered reference and Pi skills with the semester architecture. Keep the knowledge boundary focused on problem formulation, CW rendezvous, two-body fallback, model selection, and GMAT verification; remove claims or guidance that imply unsupported generalized astrodynamics or optimization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The controlled reference defines the CW equations, two-body assumptions, units, state ordering, and LVLH convention used by the recovered code
- [ ] #2 CW applicability guidance evaluates circularity, locality/separation relative to orbital radius, duration/regime, frame definition, and other documented physical assumptions without declaring a universal learned threshold
- [ ] #3 The active skill architecture is limited to problem formulation, CW rendezvous, two-body rendezvous, model selection, and verification, with equivalent naming permitted
- [ ] #4 The verification skill requires GMAT numerical comparison and an accessible trajectory screenshot
- [ ] #5 References clearly identify unsupported semester capabilities and future-work topics
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Before Done, update the educational site with this task’s current outcome, affected code/components, limitations, and objective verification evidence; do not leave stale roadmap or status claims.
- [ ] #2 Synchronize any displayed verbatim source, tests, skills, examples, or `reference/SOURCE.md` affected by the task, while keeping pedagogical browser mirrors clearly non-authoritative.
- [ ] #3 Run the dependency-free site through `./run_site.sh` and smoke-check every changed route/artifact locally without npm install or internet access.
- [ ] #4 Update the site’s controlled-reference guide so each active physics/model-selection claim links to the relevant verbatim `reference/SOURCE.md` section and deterministic implementation.
- [ ] #5 Commit all and only this task’s implementation, tests, documentation/site updates, and Backlog finalization in one atomic Git commit whose subject begins with the exact task ID followed by a colon.
- [ ] #6 If Backlog finalization metadata is added after an initial task commit, amend that same commit rather than creating a separate bookkeeping commit.
- [ ] #7 Verify the recorded tests/checks pass, the final task commit contains no unrelated, generated, credential, or secret files, and the working tree is clean after the commit.
- [ ] #8 Include the task ID and final commit subject in the educational site progress entry so the demonstrated change is traceable through Git history.
<!-- DOD:END -->
