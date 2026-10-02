---
name: orbital-targeting-planner
description: Convert a formalized rendezvous problem into an optimization problem with decision variables, constraints, objective, and a recommended solver.
---

# Orbital Targeting Planner

## Purpose

Transform a formalized rendezvous problem into an optimization formulation.

The LLM should not act as the physics engine. It should organize the problem and defer dynamics to reference equations and solver code.

## Inputs

- Initial state
- Terminal state
- Transfer time
- Delta-v constraints
- Mission objectives

## Outputs

- Decision variables
- Constraints
- Optimization objective
- Recommended solver

## Supported objectives

- Minimize total delta-v
- Minimize transfer time
- Produce a Pareto front between delta-v and time
- Respect a maximum delta-v budget

## Problem templates

### Minimize total delta-v
Decision variables typically include:
- initial burn vector,
- terminal burn vector,
- optional transfer time if not fixed.

Constraints:
- terminal rendezvous conditions,
- dynamics model constraints,
- delta-v budget if applicable.

Objective:
- minimize sum of burn magnitudes or a norm-based surrogate.

### Minimize transfer time
Decision variables may include:
- transfer duration,
- burn vectors,
- number of revolutions if relevant.

Objective:
- minimize transfer time subject to rendezvous feasibility.

### Pareto front between delta-v and time
Decision variables:
- burn vectors,
- transfer duration.

Objective:
- multi-objective or weighted-sum sweep.

### Delta-v constrained rendezvous
Decision variables:
- burn vectors,
- transfer time.

Constraints:
- total delta-v <= budget.

Objective:
- satisfy terminal conditions, then optimize time or margin.

## Recommended solver

Choose a solver appropriate to the model:
- closed-form CW targeting when the STM formulation applies,
- nonlinear least-squares or constrained optimization for more general problems,
- higher-fidelity trajectory optimization when perturbations or long arcs matter.

## Output style

Return:
- Problem class
- Decision variables
- Constraints
- Objective
- Solver recommendation
- Notes on feasibility and model dependence

Be concise and explicit.
