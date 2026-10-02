---
id: doc-1
title: Trajectory CoPilot Semester Scope
type: specification
created_date: '2026-10-01 18:07'
updated_date: '2026-10-02 14:11'
tags:
  - scope
  - semester
  - trajectory-copilot
  - educational-site
  - git-policy
---
# Trajectory CoPilot semester scope

## Research question

Can a workflow that separates rendezvous-problem formulation, dynamics-model selection, deterministic computation, and independent GMAT verification improve the reliability and transparency of LLM-generated orbital rendezvous solutions?

## Required vertical workflow

Natural-language rendezvous request → structured problem → CW applicability assessment → deterministic CW or scoped two-body result → GMAT execution → numerical comparison plus orbit/trajectory screenshot → human-readable explanation.

GMAT verification is not complete unless both numerical evidence and a directly accessible visual artifact are returned. A solver result must not be presented as authoritative when GMAT fails, disagrees outside tolerance, or does not produce the required screenshot.

## Supported problem class

- Two-spacecraft target/chaser rendezvous
- Primarily circular LEO reference orbits
- LVLH/CW relative motion where its documented assumptions hold
- Impulsive maneuvers
- Specified relative state and time of flight or orbital-period count
- A bounded deterministic two-body fallback when CW assumptions do not hold

The formalizer records central body, reference orbit, relative position/velocity, frame convention, timing, maneuver assumptions, requested outputs, missing information, ambiguity, and the provenance of each value as specified, derived, or assumed.

## Model selection

CW applicability is judged from documented physical assumptions, including circularity, locality/separation relative to orbital radius, duration/regime, frame definition, and supported maneuver assumptions. The semester project does not establish a universal empirical or learned CW-validity threshold. Clear violations route to the supported two-body path; missing material information requests clarification.

## Verification contract

For supported solved cases, the workflow automatically generates and executes GMAT input, captures logs and exit status, parses states/trajectory and maneuver results with units, compares them using declared tolerances, captures a non-empty orbit/trajectory screenshot or plot, and returns a structured PASS/WARNING/FAIL report containing the screenshot artifact. Failure modes remain distinguishable and cannot be reported as PASS.

## Experiment

Use a small benchmark with four categories:

1. Straightforward CW cases
2. Boundary cases
3. CW-invalid cases that route to two-body dynamics
4. Ambiguous or incomplete requests that require clarification

Compare a direct natural-language-to-LLM-answer baseline with the complete structured workflow. Evaluate formulation, ambiguity detection, model selection, numerical agreement, GMAT invocation, discrepancy handling, screenshot availability, and explanation quality. Claims are limited to the benchmark and supported regime.

## Explicit non-goals

No semester work on generalized astrodynamics question answering, CR3BP/n-body/cislunar dynamics, high-fidelity perturbations beyond verification needs, broad mission planning, multi-target operations, autonomous or generalized trajectory optimization, transfer-time trade optimization, Pareto fronts, learned CW-validity boundaries, or generalized space-operations decision support.

## Delivery order

1. Preserve the recovered baseline.
2. Prove an early single-case CW-to-GMAT vertical slice, including automated screenshot return.
3. Harden GMAT execution and the numerical/visual verification contract.
4. In parallel, narrow/harden formulation, reference material, model selection, CW, two-body, and frame transformations.
5. Reconnect these components into the complete scoped workflow.
6. Build the four-category benchmark, focused test suite, baseline comparison, and reproducible final report.

Deferred backlog tasks are labeled `deferred-future` or `deferred-non-goal` and are not dependencies of semester deliverables.

## Living educational site

The repository includes a static, dependency-free educational site under `site/`, launched by `./run_site.sh` at `http://127.0.0.1:4173`. It is the project’s living demonstration and progress surface, not a separate final-documentation phase.

Before any in-scope task is marked Done, its worker must:

1. Update the site’s task/progress state and describe the user-visible or scientific outcome.
2. Link the outcome to affected deterministic code, tests, skills, reference sections, GMAT artifacts, and objective evidence.
3. Synchronize verbatim mirrors under `site/data/` for every authoritative file changed by the task.
4. Update affected pedagogical mirrors or derivations while labeling them non-authoritative.
5. Run `./run_site.sh` and smoke-check every changed route and artifact without npm installation or internet access.

Physics pages must be detailed enough to teach the current implementation. Each page should state assumptions and conventions, define symbols, derive the equations step by step, map each derivation to exact `reference/SOURCE.md` and Python implementation sections, identify tests and verification evidence, and state known limitations. Required subjects include CW equations/STM, two-burn targeting and singularity handling, two-body propagation, LVLH/inertial transformations, model selection, and GMAT numerical plus visual verification.

## Atomic Git checkpoint policy

Each post-policy Backlog task must finish as one independently reviewable and revertible Git commit. The final commit subject begins with the exact task ID followed by a colon, for example `TJC-1.20: build CW-to-GMAT vertical slice`. A worker starts from a clean tree, isolates only that task’s code/tests/docs/site/Backlog changes, runs and records required checks, finalizes the task, and leaves a clean tree.

If task-finalization metadata is added after an initial task commit, the worker amends that same commit instead of creating a separate bookkeeping commit. Unrelated work, generated caches, credentials, and secrets must not enter the commit. Parallel tasks use separate branches or worktrees and retain separate commits. The educational site progress entry records the task ID and final commit subject so a demonstration can be mapped back to Git history.

TJC-1.1 was completed before Git history existed. TJC-1.26 creates the initial known-good checkpoint containing that recovered baseline and the approved project plan; every later task follows the atomic-commit rule directly.
