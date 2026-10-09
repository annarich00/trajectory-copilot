---
name: orbital-model-selector
description: Select only between the scoped CW local-rendezvous path and bounded inertial two-body coast fallback using recorded physical assumptions.
---

# Orbital Model Selector

## Purpose

Select a scoped model after `orbital-problem-formalizer` has extracted the
case. This is assumption-based reasoning, not a learned or universal numeric
threshold.

The only semester choices are:

- `CW rendezvous`: deterministic, fixed-duration local two-impulse CW
  targeting in `src/cw.py`; or
- `bounded two-body fallback`: deterministic inertial Cartesian point-mass
  **coast propagation** in `src/twobody.py`, not a general rendezvous solver.

If neither contract fits, label the request `UNSUPPORTED` or `NEEDS MORE
INFORMATION`; do not recommend an unimplemented higher-fidelity solver.

## Required assessment

For a CW candidate, explicitly record each item below from the supplied case:

1. **Circularity:** Is the chief/reference orbit circular or near-circular?
2. **Locality:** Is relative separation small relative to reference-orbit
   radius, rather than a global phasing arc?
3. **Duration/regime:** Is the fixed transfer duration compatible with local
   linearization, without long or multi-revolution accumulated error?
4. **Frame:** Is the relative state in the explicit right-handed LVLH/RIC
   convention `x` radial outward, `y` along-track, `z` cross-track, with
   `[x,y,z,x_dot,y_dot,z_dot]` ordering and SI units?
5. **Other physics:** Are central-body dominance, negligible perturbations,
   small relative velocity, and impulsive-burn assumptions appropriate?
6. **Targeting conditioning:** Is the requested CW transfer time outside the
   singular/ill-conditioned `Phi_rv` regime reported by `src/cw.py`?

Do not declare CW valid from a single fixed percentage, orbit count, or
learned threshold. `validate_cw_use()` provides limited deterministic warnings;
it does not replace this documented assessment.

## Selection results

### CW rendezvous

Select only when all required CW assumptions are supported. Refer to
`reference/SOURCE.md` §§A, B, and D and route fixed-duration targeting to the
`cw-rendezvous` skill.

### Bounded two-body fallback

Select only for a declared point-mass coast case with an initial six-element
inertial Cartesian SI state `[x,y,z,vx,vy,vz]`, positive `mu`, finite duration,
and positive fixed RK4 step count. State explicitly that it provides a final
coast state only; it does not target, execute burns, optimize, or accept
unspecified/LVLH-relative frames.

### Unsupported / needs information

Use this result for ambiguous frames, missing essential data, perturbations,
thrust, optimization, variable-duration trade studies, or cases outside both
contracts. State why, without inventing a new model.

## Required output

Return a concise note containing:

- selection (`CW rendezvous`, `bounded two-body fallback`, `UNSUPPORTED`, or
  `NEEDS MORE INFORMATION`);
- evidence for every required assessment item;
- violated or unknown assumptions;
- deterministic implementation handoff; and
- verification handoff.

## Verification handoff

All numerical candidates go to `gmat-rendezvous-verification`. GMAT numerical
comparison and an accessible trajectory screenshot are required before a
result can be called PASS.
