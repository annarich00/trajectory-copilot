# Direct-LLM baseline response — Case C (CW-invalid / two-body)

**Methodology note:** see `case_a_baseline_llm_response.md`'s identical
disclosure. This response was produced single-shot by the implementing
model with no access to this repository's tooling.

## Request (verbatim, from `evaluations/benchmark/case_c_two_body.json`)

> A spacecraft is in Earth orbit with an initial inertial Cartesian state
> position [7778000, 0, 0] m, velocity [0, 7158.7124559338245, 0] m/s.
> Earth's gravitational parameter is 398600441800000.0 m^3/s^2. Propagate
> this state forward 900 seconds under point-mass gravity only (no thrust,
> no perturbations, no targeting). Report the final inertial Cartesian
> state.

## Baseline response (as produced single-shot)

This is a straightforward two-body (Keplerian) propagation problem, not a
rendezvous or CW problem at all — there's no second spacecraft, no
relative frame, and no targeting objective here, just "propagate this
one orbit forward by 900 seconds under point-mass gravity."

**Checking the orbit type.** r0 = 7,778,000 m, v0 = 7158.71 m/s, and
r0·v0 = 0 (velocity is purely tangential), so this looks like it's at
perigee or apogee of an orbit, or possibly circular. Computing specific
orbital energy and eccentricity from r0, v0, mu confirms the eccentricity
vector is essentially zero — **this is (to numerical precision) a circular
orbit** at radius ≈ 7778 km, with orbital period T = 2π·sqrt(a³/mu) ≈
6826.7 s.

**Propagating 900 s forward.** For a circular orbit, this is just uniform
circular motion: the spacecraft advances through an angle
θ = n·Δt ≈ 0.8283 rad (≈ 47.46°) in the orbital plane (here the x-y plane,
since the initial velocity is purely in y).

- **Final position ≈ [5,258,695, 5,730,917, 0] m**
- **Final velocity ≈ [-5274.6, 4840.0, 0] m/s**

**Caveats:** this assumes point-mass, unperturbed Keplerian motion exactly
as stated (no J2, no drag, no third-body) and that the problem is
genuinely circular (confirmed above). I computed this using the circular-
orbit angular-rate shortcut rather than fully propagating Kepler's
equation for a general eccentric orbit, which is valid here but would not
generalize to an eccentric case without more care. I have not
independently verified this against a numerical integrator (e.g. GMAT) or
run an RK4/high-order propagation to confirm — I'd recommend doing so
before treating this as an authoritative result.

---

## What this baseline response does / does not do (disclosed, not hidden)

This hand-derived result is numerically close to the fixture's own
GMAT-cross-checked reference (`final_state_m_mps =
[5258694.86, 5730917.24, 0.0, -5274.62, 4839.995, 0.0]`) — essentially
exact, since this really is a clean circular two-body coast and the
closed-form circular shortcut is exact for this case.

**What this response never does, and never had any mechanism to do, is
flag that the request is outside the two-spacecraft LVLH-relative
rendezvous class this project's formalizer/model-selector/CW pipeline is
actually built around.** A general-purpose LLM baseline has no formal
"scope" check at all: it simply recognizes "this looks like a two-body
propagation" from general astrodynamics knowledge and solves it, with no
structured record of *why* this is not a CW case (no `locality`/
`other_physics` assumption ever gets explicitly marked `violated`, no
`scope: out of scope` classification is ever produced) and no
machine-checkable boundary between "this routed to two-body because CW's
assumptions were explicitly reviewed and failed" versus "this routed to
two-body because the LLM's informal pattern-matching happened to notice
the geometry." For a single clean case like this one, that informality
produces a numerically fine answer; `REPORT.md` discusses why that
informality is itself the risk the structured workflow is designed to
remove, not merely redundant with it.
