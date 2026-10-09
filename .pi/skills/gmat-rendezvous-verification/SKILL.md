---
name: gmat-rendezvous-verification
description: Verify a scoped CW or bounded two-body candidate with GMAT numerical comparison and an accessible trajectory screenshot.
---

# GMAT Rendezvous Verification

## Purpose

Apply the required end-to-end verification contract to a candidate produced by
`cw-rendezvous` or `orbital-two-body-rendezvous`. This skill defines the
required evidence; it does not claim that GMAT is integrated in the recovered
repository.

## Required input record

Require a reproducible candidate record containing:

- selected model and documented assumptions;
- initial conditions, frame/axis convention, state ordering, units, `mu`, and
  duration;
- deterministic implementation output; and
- comparison tolerances and an identification of the same case in GMAT.

Do not compare states in mismatched frames, epochs, state orderings, units, or
dynamics assumptions.

## Required GMAT evidence

For a verification result to be `PASS`, provide both:

1. **GMAT numerical comparison:** GMAT output for the same declared case,
   compared numerically to the candidate at documented tolerances, with
   position and velocity discrepancies recorded; and
2. **Accessible trajectory screenshot:** a non-empty returned GMAT
   orbit/trajectory screenshot with a stable accessible path or link.

GMAT execution failure, unavailable GMAT, missing/mismatched comparison data,
a tolerance exceedance, or a missing/inaccessible screenshot cannot be
reported as PASS. Preserve a distinct status such as `FAIL`, `UNAVAILABLE`,
or `INCOMPLETE` and state the missing evidence.

## Output

Return:

- verification status;
- candidate and GMAT identifiers;
- numerical position/velocity comparison and tolerances;
- screenshot path/link and accessibility result;
- discrepancies, assumptions, and limitations; and
- the evidence needed for reproduction.

## Scope boundary

This is not verification of generalized optimization, Pareto fronts,
perturbed/high-fidelity dynamics, CR3BP/cislunar trajectories, or broad
mission planning. The current repository has no GMAT execution integration;
that implementation is planned separately. The bounded internal two-body or
Poliastro checks do not replace this GMAT numerical-plus-screenshot contract.
