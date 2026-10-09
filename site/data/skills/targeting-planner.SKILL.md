---
name: cw-rendezvous
description: Solve only a fully specified, assumption-qualified local rendezvous with the deterministic two-impulse Clohessy-Wiltshire implementation.
---

# CW Rendezvous

## Purpose

Use the deterministic CW two-impulse targeting path only after problem
formalization and assumption-based model selection have established that the
case is a local circular-chief relative-motion problem.

This skill is not a general trajectory optimizer. It does not choose a
transfer time, trade delta-v against time, create Pareto fronts, or substitute
higher-fidelity dynamics.

## Required inputs

Require all of the following before calling the deterministic implementation:

- reference radius or mean motion and positive gravitational parameter;
- explicitly stated LVLH/RIC convention: x radial outward, y along-track in
  the chief direction of motion, z cross-track/orbit-normal;
- initial and terminal relative states ordered
  `[x, y, z, x_dot, y_dot, z_dot]` in SI units (m and m/s);
- a fixed positive transfer duration in seconds; and
- an assumption-based model-selection note that addresses circularity,
  locality/separation relative to reference radius, duration/regime, frame,
  negligible perturbations, and impulsive-burn suitability.

Do not invent any missing input or coordinate convention.

## Deterministic path

1. Consult `reference/SOURCE.md` §§A–D.
2. Use `src/cw.py::mean_motion` and `two_burn_targeting` for a fixed-duration
   CW candidate only.
3. Preserve the input/output units and state ordering above.
4. Treat `CWSingularTransferError` as a rejected transfer time, not a reason
   to approximate with a least-squares solution.
5. Report the two impulses and final state only as a CW result under the
   recorded assumptions.

## Boundary handling

If assumptions are missing, return the formalizer's missing-information or
model-validity concern; do not solve. If CW is rejected, hand the case to the
bounded two-body rendezvous skill only when its inertial coast contract fits.
Requests for optimization, variable-duration design, continuous thrust,
perturbations, or generalized mission design are unsupported semester
capabilities and must be labeled as such.

## Verification handoff

Every candidate must be handed to `gmat-rendezvous-verification`. A result is
not PASS without GMAT numerical comparison against the same declared case and
an accessible trajectory screenshot.
