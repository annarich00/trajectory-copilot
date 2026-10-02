---
name: orbital-model-selector
description: Select an appropriate orbital dynamics model for rendezvous and proximity operations, choosing between Clohessy-Wiltshire, two-body propagation, or higher-fidelity propagation.
---

# Orbital Model Selector

## Purpose

Select the most appropriate dynamics model for a rendezvous or relative-motion problem.

The LLM should not solve orbital mechanics from memory. It should:
- inspect the formalized problem,
- identify violated assumptions,
- select the dynamics model,
- explain why the model is selected,
- recommend verification methods.

## Model choices

### Clohessy-Wiltshire (CW)
Use only when the problem satisfies the linearized proximity-operations assumptions.

### Two-body propagation
Use when the geometry is too large, too nonlinear, or too long-duration for CW, but the motion is still reasonably described by point-mass gravity.

### Higher-fidelity propagation
Use when perturbations, non-Keplerian effects, or mission accuracy requirements make the two-body model insufficient.

## CW rejection checks

Reject CW or flag it as invalid if any of the following are true:
- reference orbit is not near-circular,
- reference orbit radius or mean motion is unknown,
- relative separation is not small compared with orbital radius,
- transfer duration is long enough that linearization error can accumulate materially,
- the scenario is clearly beyond local proximity operations,
- multi-revolution phasing makes the linearization unreliable,
- the configuration is GEO-scale or other large-arc geometry,
- the target/chaser separation suggests a global-orbit phasing problem rather than relative motion.

## Required output fields

Return a concise model-selection note with:
- Selected model
- Assumption checks
- Violated assumptions
- Why this model
- Recommended verification method(s)

## Verification guidance

- CW candidates should be checked against two-body propagation when possible.
- Large separations, GEO-scale phasing, or long transfer times should be verified with a non-linear model.
- If the result is sensitive to model choice, recommend higher-fidelity propagation.

## Style

Be explicit about why CW is valid or invalid.
Do not overstate confidence when the geometry is outside CW assumptions.
