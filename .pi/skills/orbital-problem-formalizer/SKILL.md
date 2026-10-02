---
name: orbital-problem-formalizer
description: Convert natural-language astrodynamics problems into concise structured specifications before solving. Use for orbital mechanics, spacecraft rendezvous, relative motion, trajectory design, and especially Clohessy-Wiltshire problems.
---

# Orbital Problem Formalizer

## Purpose

Convert an astrodynamics question into a structured problem specification before attempting a solution.

Do NOT solve the problem.

The goal is to determine:
1. what is known,
2. what is missing,
3. what dynamical model is appropriate,
4. whether the problem is ready to solve.

## Scope

Initially focus on:
- Two-body orbital mechanics
- Clohessy-Wiltshire (CW) relative motion
- Proximity operations
- Orbital rendezvous

Do not assume CW is appropriate merely because the problem involves rendezvous.

## Required extraction

Extract:

- Mission objective
- Reference orbit
- Coordinate frame
- Initial relative position
- Initial relative velocity
- Terminal position
- Terminal velocity
- Transfer time
- Maneuver/burn constraints
- Gravitational parameter
- Units
- Requested dynamics model

Use `unknown` when information is absent.

Do not invent values or silently assume conventions.

## CW validity checks

If CW is requested or considered, check:

- Circular reference orbit
- Known reference radius or mean motion
- Small relative separation
- Defined LVLH/Hill coordinate convention
- Initial relative state
- Terminal conditions
- Transfer time
- Maneuver constraints

Flag CW as a model-validity concern if the geometry or assumptions are inconsistent with linearized relative motion.

## Output format

Return ONLY the following structure:

### Problem Type
<type>

### Objective
<one sentence>

### Reference Orbit
- Orbit: <value or unknown>
- Radius/altitude: <value or unknown>
- Mean motion/period: <value or unknown>
- Gravitational parameter: <value or unknown>

### Coordinate Frame
<frame and axis convention, or unknown>

### Initial Relative State
- Position: [x, y, z]
- Velocity: [xdot, ydot, zdot]

### Terminal Conditions
- Position: [x, y, z] or unknown
- Velocity: [xdot, ydot, zdot] or unknown
- Interpretation: state any terminal conditions inferred from the objective separately from explicitly provided conditions.

### Timing
<transfer duration or unknown>

### Maneuver Constraints
<burn number/type/timing or unknown>

### Dynamics Model
<requested or proposed model>

### Missing Information
- <item>
- <item>

### Model Validity Concerns
- <concern>
- <concern>
Use `None` if there are no identified concerns.

### Readiness
<READY TO SOLVE | NEEDS MORE INFORMATION | MODEL VALIDITY CONCERN | NEEDS MORE INFORMATION + MODEL VALIDITY CONCERN>

### Formalization Summary
<maximum 2 sentences>

## Rules

- Do not solve the problem.
- Do not derive numerical values.
- Do not invent missing information.
- Do not silently choose a coordinate convention.
- Do not assume circular orbit unless established or explicitly requested.
- Distinguish missing information from model-validity concerns.
- Keep the response concise.
