# Baseline Comparison: Orbital Problem Formalizer

## Date

September 17, 2026

## Purpose

Evaluate whether an orbital-problem formalization skill changes how an LLM handles astrodynamics problems with different levels of specification.

The initial experiment tests whether the agent:

* identifies missing information,
* avoids silently inventing assumptions,
* distinguishes solvable from underspecified problems,
* recognizes when a requested dynamics model may be inappropriate,
* and produces a structured problem specification before attempting a solution.

The three initial tests represent:

1. An underspecified rendezvous problem.
2. A fully specified CW rendezvous problem.
3. A rendezvous problem in which the requested CW model is inappropriate because of the separation scale.

---

# Test 1: Underspecified Rendezvous

## Input

> The chaser is 200 meters behind the target. Find a one-orbit rendezvous.

## Expected Behavior

The agent should **not attempt to solve the problem**.

The agent should identify:

* Missing reference orbit information
* Missing coordinate frame
* Missing relative velocity
* Missing axis convention
* Ambiguity in the phrase "200 meters behind"

The agent should recognize that:

* A rendezvous objective is implied
* A one-orbit transfer duration is requested
* A unique solution cannot be determined from the available information

### Expected Readiness

`NEEDS MORE INFORMATION`

### Expected Model Validity

`MODEL VALIDITY CONCERN`

The model-validity concern is not that CW is definitively invalid. Rather, the information provided is insufficient to establish whether CW is an appropriate model because the reference orbit and coordinate convention are unknown.

## Actual Result — Skill Version 1

### Readiness

`NEEDS MORE INFORMATION + MODEL VALIDITY CONCERN`

The formalizer produced a structured problem specification and identified:

* Unknown reference orbit
* Unknown orbital radius/altitude
* Unknown mean motion/period
* Unknown gravitational parameter
* Unknown coordinate frame
* Ambiguity in interpreting "behind"
* Incomplete initial relative state
* Unknown initial relative velocity
* Unspecified terminal velocity condition
* Unknown maneuver constraints
* Unconfirmed circularity of the reference orbit

The formalizer also explicitly stated that assuming "behind" corresponds to a particular CW/LVLH component would be an assumption rather than a confirmed input.

### Observation

**PASS**

The skill successfully prevented the agent from immediately generating a numerical trajectory and instead exposed the information required to formulate the problem.

An important behavior is that the skill did not simply declare CW invalid. It recognized that **model applicability itself cannot yet be established** because the reference orbit and coordinate convention are missing.

### Research Significance

This test establishes the baseline behavior the formalizer is intended to provide:

> **Do not solve an orbital problem until the information necessary to define the physical problem and assess the requested model is available.**

---

# Test 2: Fully Specified CW Rendezvous

## Input

> A target spacecraft is in a circular orbit at 350 km altitude around Earth.
>
> Earth radius is 6378 km and gravitational parameter is 398600 km^3/s^2. The LVLH frame has x radial outward, y along-track in the velocity direction, and z cross-track. At t=0, the chaser is 15 m radially outward and 200 m behind the target along-track. Its relative velocity is 0.14 m/s radially inward, with zero along-track and cross-track velocity. The objective is a two-burn rendezvous after one orbital period, ending with zero relative position and velocity.
>
> The problem specifies the initial and final conditions, the two-burn capability, and the objective to minimize ΔV and time.

## Expected Behavior

The agent should identify:

* Circular orbit
* LVLH frame
* Complete relative state
* Terminal constraints
* One-orbit timing requirement
* Two-burn maneuver structure
* CW/Hill dynamics as the likely model

The agent should recognize that:

* Orbital period can be computed
* Mean motion can be computed
* Burn timing can be determined as part of the solution
* The initial and terminal states are specified
* The problem is sufficiently specified for a CW solution

### Expected Readiness

`READY TO SOLVE`

### Expected Model Validity

`NO VALIDITY CONCERNS`

## Actual Result — Skill Version 1

### Readiness

`READY TO SOLVE`

The formalizer correctly constructed:

* Circular reference orbit
* Orbital radius of 6728 km
* Gravitational parameter of 398600 km³/s²
* LVLH/Hill coordinate convention
* Initial relative position `[15, -200, 0]` m
* Initial relative velocity `[-0.14, 0, 0]` m/s
* Zero terminal relative position
* Zero terminal relative velocity
* One-orbit transfer time
* Two-burn maneuver structure

It also recognized that the orbital period and mean motion are **derivable quantities**, rather than missing operator inputs.

The formalizer determined that CW dynamics are appropriate because the reference orbit is circular and the relative separation is very small compared with the 6728 km orbital radius.

### Observation

**PASS**

The skill correctly transitioned from problem formalization to a `READY TO SOLVE` state.

This is important because the formalizer is not intended simply to reject incomplete information. It must also recognize when the information provided is sufficient and **allow the downstream solver to proceed**.

### Research Significance

This test demonstrates the complementary behavior to Test 1:

> **A useful formalizer must distinguish missing information from quantities that can be derived from the information already provided.**

The result therefore supports a distinction between:

1. Required operator input
2. Derivable quantities
3. Standard modeling assumptions
4. Optional constraints
5. Model-validity concerns

The fully specified CW problem contains sufficient information to derive the orbital period and mean motion, so those quantities should not be treated as missing inputs.

---

# Test 3: CW Breakdown Scenario

## Input

> The target is in GEO and the chaser is approximately one-third of the way around the GEO belt from the target. Find a rendezvous using Clohessy-Wiltshire equations.

## Expected Behavior

The agent should identify:

* GEO environment
* CW dynamics as the requested model
* Missing initial state information

The agent should also recognize:

* The separation is likely too large for CW validity
* CW is a local linearized approximation
* Full orbital dynamics may be required

### Expected Readiness

`NEEDS MORE INFORMATION`

### Expected Model Validity

`MODEL VALIDITY CONCERN`

## Actual Result — Skill Version 1

### Readiness

`NEEDS MORE INFORMATION + MODEL VALIDITY CONCERN`

The formalizer identified:

* GEO as the reference environment
* CW as the explicitly requested model
* Missing precise initial relative position
* Missing radial and cross-track state information
* Missing initial relative velocity
* Missing coordinate convention
* Missing terminal velocity requirement
* Missing transfer time
* Missing maneuver constraints

It also identified a fundamental CW applicability concern.

The agent recognized that a separation of approximately one-third of the GEO belt is not small relative to the GEO orbital radius and therefore violates the small-relative-distance assumption underlying the CW linearization.

It further identified that nonlinear/two-body dynamics would become important and that a full two-body or Lambert/phasing-type approach would generally be more appropriate for such a geometry.

### Observation

**PASS**

The skill correctly identified both:

1. Missing information needed to formulate a unique rendezvous problem.
2. A model-validity problem with the explicitly requested CW equations.

This is particularly important because the agent did **not simply obey the user's request to use CW**. It evaluated whether the requested model was physically appropriate for the stated geometry.

### Research Significance

This test directly supports the eventual Trajectory Copilot architecture:

> **The agent should be able to recognize when a requested astrodynamics model is outside its region of validity rather than blindly applying the requested equations.**

This provides the motivation for a later model-selection and verification layer in which a CW-generated solution can be checked against a higher-fidelity two-body model and, eventually, GMAT.

---

# Baseline Results

| Test                          | Expected Readiness     | Actual Skill V1                           | Model Validity                                               | Result   |
| ----------------------------- | ---------------------- | ----------------------------------------- | ------------------------------------------------------------ | -------- |
| Underspecified rendezvous     | Needs more information | Needs more information + validity concern | Cannot establish CW applicability from available information | **PASS** |
| Fully specified CW rendezvous | Ready to solve         | Ready to solve                            | No validity concern                                          | **PASS** |
| Large-separation GEO/CW       | Needs more information | Needs more information + validity concern | CW small-relative-motion assumption violated                 | **PASS** |

---

# Initial Research Findings

## Finding 1 — The formalizer changes the agent's workflow

The formalizer creates a distinct step between natural-language input and trajectory generation.

Rather than immediately attempting to solve every orbital problem, the agent first constructs a structured representation of:

* the reference orbit,
* coordinate frame,
* initial state,
* terminal conditions,
* timing,
* maneuver constraints,
* requested dynamics model,
* missing information,
* and model-validity concerns.

This behavior is demonstrated most clearly by Test 1.

## Finding 2 — The formalizer can prevent unsupported assumptions

In the underspecified rendezvous test, the agent identified that quantities such as the reference orbit, coordinate convention, and initial velocity were not provided.

Instead of silently selecting those values, the formalizer surfaced them as missing information.

This is a central requirement for an operator-facing astrodynamics system because a physically plausible numerical answer can still be incorrect if the underlying assumptions were never authorized.

## Finding 3 — The formalizer can distinguish missing information from derivable information

Test 2 is important because the formalizer did **not** require the operator to provide every quantity used by the solver.

For example, mean motion and orbital period were not explicitly supplied but could be calculated from:

* Earth gravitational parameter
* Earth radius
* orbital altitude

The formalizer therefore correctly classified the problem as:

`READY TO SOLVE`

rather than treating every derived quantity as missing.

This distinction should remain explicit in future versions of the formalizer.

## Finding 4 — The formalizer can identify model-validity concerns

Test 3 demonstrates that problem specification and model selection are separate questions.

A problem may explicitly request a particular model while simultaneously describing a physical regime in which that model is inappropriate.

The GEO scenario demonstrates this behavior:

> The user requested CW, but the stated separation is inconsistent with the small-relative-motion assumption underlying CW.

This provides an early example of the agent acting as a **critical reviewer of the requested model**, rather than merely a mathematical executor.

## Finding 5 — "Ready to solve" should mean the problem is sufficiently specified, not that every numerical quantity has been provided

The three tests suggest that readiness should be based on whether the agent has enough information to formulate the requested physical problem.

A useful classification is:

1. **Required operator input** — information the operator must provide.
2. **Derivable quantity** — information the agent can calculate from provided inputs.
3. **Standard modeling assumption** — an assumption that may be acceptable if explicitly declared.
4. **Optional constraint** — information that affects optimization or operations but is not required to define the basic problem.
5. **Model-validity concern** — evidence that the selected dynamics model may not adequately represent the physical situation.

This classification is more useful than simply counting how many pieces of information are present or absent.

---

# Current Research Question

The initial tests support the hypothesis that an explicit formalization layer can improve the agent's handling of underspecified and potentially invalid astrodynamics problems.

The next question is whether this improvement in **problem formulation** translates into improved **trajectory-generation reliability**.

In particular:

> Does requiring the agent to formalize the orbital problem before solving it reduce incorrect assumptions and improve the reliability of the resulting trajectory?

---

# Next Experiment: Constrained Rendezvous Optimization

The next experiment should extend beyond the binary question of whether a problem is "ready to solve."

A more realistic operator request could specify an initial orbital geometry and ask the agent to find a rendezvous trajectory while minimizing both:

* ΔV
* transfer time

The experiment should investigate whether the agent recognizes that these are competing objectives rather than a single scalar objective.

Questions to test include:

* Does the agent recognize that ΔV and time are separate objectives?
* Does it recognize that a weighting or priority must be specified if a single optimum is required?
* Does it identify the existence of multiple feasible solutions?
* Can it identify or construct a Pareto front of time versus ΔV?
* Does it recognize that the available spacecraft ΔV capability is an **input constraint** when a maximum ΔV budget is specified?
* Can it distinguish the spacecraft's available ΔV from the **ΔV required by a candidate trajectory**, which is an output?
* If a very large ΔV capability is specified, does the agent recognize that a faster, higher-ΔV solution may become feasible?
* If a finite ΔV budget is imposed, can the agent find the fastest feasible solution subject to that constraint?
* How many agent prompts, tool calls, and reasoning/verification steps are required to reach a correct solution?

This experiment would move the project from:

**"Can the agent correctly formalize an orbital problem?"**

toward:

**"Can the agent correctly translate an operator's mission objective and constraints into a mathematically well-posed trajectory-design problem?"**

---

# Next Implementation Step

Build the CW rendezvous solver so that it consumes the formalizer's structured problem specification rather than the original natural-language prompt.

The solver should:

* calculate the reference mean motion,
* formulate the CW state-transition equations,
* solve for the required impulsive maneuvers,
* propagate the resulting relative trajectory,
* calculate total ΔV,
* verify the terminal state,
* and expose the solution in a form that can be independently checked.

The formalizer and solver should remain separate components so that the contribution of the formalization step can be evaluated independently.

The eventual verification loop should then compare the CW solution against a higher-fidelity two-body propagation and, ultimately, GMAT.
