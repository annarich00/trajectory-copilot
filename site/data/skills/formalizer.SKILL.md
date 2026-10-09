---
name: orbital-problem-formalizer
description: Formalize only a two-spacecraft, primarily circular-LEO, impulsive LVLH rendezvous request into a provenance-labeled specification before any solver is used.
---

# Scoped Rendezvous Problem Formalizer

## Purpose and supported class

Convert a natural-language request into a structured specification **without solving it**. This formalizer supports only:

- exactly two spacecraft: a target/chief and chaser/deputy;
- primarily circular low-Earth reference orbits;
- impulsive maneuvers;
- a relative state expressed in a defined LVLH/Hill frame; and
- a specified time of flight or an explicitly stated period count.

It is not a general astrodynamics, GEO/phasing, multi-spacecraft, finite-burn, or terminal-guidance formalizer. If the request is outside this class, label it `out of scope` and ask the operator to restate it within the supported class; do not choose another model or manufacture a usable specification.

## Provenance rules

Every field, including unknown fields, must use exactly one provenance label:

- `specified` — stated unambiguously by the operator.
- `derived` — mechanically computable from specified values; show the source values and formula, but do not calculate a numerical result.
- `assumed` — an explicit, non-material working assumption. Assumptions never satisfy required inputs and never make a problem ready to solve.
- `missing` — required information was not supplied.
- `ambiguous` — supplied wording has more than one material interpretation.
- `contradictory` — supplied statements cannot both be true.
- `unit-inconsistent` — values or units cannot be reconciled without an operator correction.
- `out of scope` — outside the supported rendezvous class.

Do not relabel inferred terminal conditions as specified. Do not invent altitude, gravitational parameter, circularity, LVLH convention, coordinate signs, units, terminal state, maneuver details, or a physical constant. A conventional Earth parameter, a conventional LVLH axis direction, and “rendezvous means zero terminal velocity” remain unsupplied unless the operator explicitly provides them.

## Required output schema

Return **only** this Markdown structure. Preserve all field names. Each field must be `<value or unknown> — <provenance label>`; units must be included with every numeric physical value.

### Scope
- Classification: <supported | out of scope> — <provenance label>
- Reason: <concise reason> — <provenance label>

### Participants
- Central body: <name or unknown> — <provenance label>
- Target/chief: <identifier or unknown> — <provenance label>
- Chaser/deputy: <identifier or unknown> — <provenance label>

### Reference Orbit
- Circularity: <circular | non-circular | unknown> — <provenance label>
- Altitude: <value or unknown> — <provenance label>
- Radius or orbital elements: <value or unknown> — <provenance label>
- Gravitational parameter: <value or unknown> — <provenance label>
- Mean motion or period: <value or unknown> — <provenance label>

### Relative Frame and State
- Frame: <LVLH/Hill or unknown> — <provenance label>
- LVLH convention: <x/y/z directions and signs or unknown> — <provenance label>
- Initial relative position: <[x, y, z] with units or unknown> — <provenance label>
- Initial relative velocity: <[xdot, ydot, zdot] with units or unknown> — <provenance label>

### Terminal Conditions
- Relative position: <[x, y, z] with units or unknown> — <provenance label>
- Relative velocity: <[xdot, ydot, zdot] with units or unknown> — <provenance label>
- Requested outputs: <e.g., burn vectors, final state, or unknown> — <provenance label>

### Timing and Maneuvers
- Time of flight: <value or unknown> — <provenance label>
- Period count: <value or unknown> — <provenance label>
- Maneuver assumptions: <impulsive burn count, timing, and constraints or unknown> — <provenance label>

### Blocking Issues
- <one issue per missing, ambiguous, contradictory, unit-inconsistent, or out-of-scope required field; `None` only when there are none>

### Clarification Questions
- <one focused question per blocking issue; `None` only when there are none>

### Readiness
<READY TO SOLVE | NEEDS CLARIFICATION | OUT OF SCOPE>

### Formalization Summary
<at most two sentences; do not solve or calculate values>

## Evaluation and readiness rules

A request is `READY TO SOLVE` only when it is in scope and has all of the following unambiguous, unit-consistent, and explicitly supplied: central body; circular reference orbit through altitude, radius, or complete elements plus gravitational parameter; LVLH convention; complete initial relative position and velocity; one or more complete terminal conditions; a time of flight or period count; impulsive maneuver assumptions; and requested outputs.

- If altitude plus central-body radius is supplied, orbital radius may be `derived`; if radius plus gravitational parameter is supplied, mean motion/period may be `derived`.
- A period count is usable only when the reference orbit provides enough specified information to derive its period. Do not silently turn “one orbit” into a duration.
- If both time of flight and period count are supplied, preserve both. Mark them `contradictory` when the stated duration does not match the specified/derived period count.
- Mark physical values `unit-inconsistent` when units are absent, dimensions disagree, vector components use unresolved mixed units, or values claim incompatible units. Ask for corrected values; do not convert by guessing.
- “Behind,” “ahead,” “near,” or “rendezvous” does not establish an LVLH axis/sign, a complete state, or terminal position/velocity. Preserve it as `ambiguous` or `missing` and ask a focused question.
- A requested model is not a substitute for the required physical inputs. Do not evaluate CW applicability beyond recording whether the scoped preconditions are supplied; model selection remains separate work.
- Never solve, derive a numerical value, select a model, or prescribe burns.
