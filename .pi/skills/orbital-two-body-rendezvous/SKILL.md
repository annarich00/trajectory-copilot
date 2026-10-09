---
name: orbital-two-body-rendezvous
description: Run only the bounded deterministic inertial Cartesian point-mass two-body coast fallback for a declared rendezvous case.
---

# Bounded Two-Body Rendezvous Fallback

## Purpose

Provide the semester's nonlinear fallback when CW is not selected and the
case fits the implemented point-mass coast contract. Despite this skill's
rendezvous workflow role, the implementation is **not** a general rendezvous
solver: it propagates one supplied inertial Cartesian state through a coast
arc and returns the final state.

## Required inputs

Require:

- initial inertial Cartesian state `[x, y, z, vx, vy, vz]`;
- SI units: position in metres and velocity in metres per second;
- positive gravitational parameter `mu` in m^3/s^2;
- finite coast duration in seconds; and
- positive fixed RK4 step count.

The supported stable metadata is
`frame="inertial-cartesian"`, `central_body="Earth"`,
`dynamics="point-mass-two-body"`, and `integrator="fixed-step-rk4"`.
An optional epoch can accompany the case for external verification.

## Deterministic path

1. Confirm the model-selector note rejects or does not select CW for stated
   assumptions.
2. Consult `reference/SOURCE.md §C`.
3. Use `src/twobody.py::TwoBodyCase` and
   `propagate_cartesian_state` / `kepler_propagate_state` without changing
   frame or units.
4. Report the final state in the same SI inertial Cartesian frame and preserve
   the metadata.
5. Reject non-finite inputs, non-positive `mu` or steps, and the zero-radius
   point-mass singularity; do not improvise a result.

## Explicit exclusions

Do not claim burn targeting, maneuver execution, optimization, thrust,
perturbations, J2, drag, third bodies, solar radiation pressure, LVLH-relative
input, or a solved rendezvous. Those requests are unsupported semester
capabilities. Use `unsupported_request()` behavior as the code-facing
boundary.

## Verification handoff

Send every candidate to `gmat-rendezvous-verification`. The external evidence
must include GMAT numerical comparison of the same declared case and an
accessible trajectory screenshot. Without both, report the result as not
verified, never PASS.
