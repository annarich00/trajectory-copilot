# Direct-LLM baseline response — Case B (boundary CW)

**Methodology note:** see `case_a_baseline_llm_response.md`'s identical
disclosure. This response was produced single-shot by the implementing
model with no access to this repository's tooling.

## Request (verbatim, from `evaluations/benchmark/case_b_boundary_cw.json`)

> Earth is the central body. The target spacecraft is in a circular 350 km
> altitude orbit. Earth radius is 6378 km and gravitational parameter is
> 398600 km^3/s^2. The LVLH frame has x radial outward, y along-track in
> the target velocity direction, and z cross-track completing a
> right-handed frame. At t = 0, the chaser relative state is position
> [15 m, -200 m, 0 m] and velocity [-0.14 m/s, 0 m/s, 0 m/s]. Use two
> impulsive burns. After exactly one HALF of the orbital period, reach
> relative position [0 m, 0 m, 0 m] and relative velocity [0 m/s, 0 m/s,
> 0 m/s]. Return the two burn vectors and terminal relative state.

## Baseline response (as produced single-shot)

This is nearly identical to a standard CW rendezvous setup, just with a
half-period transfer instead of a quarter-period one. Reference radius
a = 6728 km, mean motion n ≈ 1.1440×10⁻³ rad/s, orbital period T ≈ 5492.1 s,
so the half-period transfer time is t = T/2 ≈ 2746.06 s.

Since the initial relative velocity and position have no cross-track (z)
component, this reduces to a 2-D in-plane (radial/along-track) targeting
problem. Using the standard CW state-transition relations for the x-y
plane and solving for the two impulsive burns that drive the relative
state to zero at t = T/2:

- **Δv0 ≈ [0.073, -0.030, 0.0] m/s**
- **Δv1 ≈ [-0.067, -0.004, 0.0] m/s**
- **Total ΔV ≈ 0.146 m/s**
- **Terminal relative state: [0, 0, 0] m, [0, 0, 0] m/s**

As with any CW-based solution, this assumes the reference orbit is
circular and the relative separation is small compared with the orbital
radius — both hold comfortably here. I have not independently verified
this result against a higher-fidelity propagator, so I'd recommend an
independent numerical check before relying on these burn values
operationally.

---

## What this baseline response does NOT do (disclosed, not hidden)

The hand/scratch calculation behind the numbers above only ever solved the
**2×2 in-plane** subsystem (ignoring the cross-track/z row of the CW
state-transition matrix entirely, since z0 = vz0 = 0 made that row look
irrelevant to a quick solve). That 2×2 in-plane sub-block is in fact
well-conditioned at this transfer time (determinant ≈ 1.22×10⁷ — nothing
alarming), which is exactly why this baseline response arrives at a clean,
confident, unqualified-looking answer with no hint of anything unusual.

What this baseline response never notices is that at exactly
n·t = π (an exact half orbital period), the CW state-transition matrix's
velocity-mapping block (Φrv) is **singular in general** — not in the 2×2
in-plane sub-block used above, but through the decoupled cross-track term
`sin(n·t)/n`, which also vanishes at this exact instant. For this specific
request the cross-track component is trivially zero, so the degenerate
direction happens not to matter numerically; but a solver that constructs
and inverts the *general* 3-DOF Φrv (rather than silently reducing to the
in-plane 2×2 case because it "looks" planar) would correctly detect that
this transfer time sits exactly on a targeting singularity, that the
returned solution is only a non-unique minimum-norm solution in general,
and that a small, undisclosed deviation from exactly half the orbital
period, or any nonzero cross-track component, would materially change
that conclusion. This baseline response gives no such warning at all — it
reports this case with the same unqualified confidence as the genuinely
clean quarter-period case (a), which is exactly the gap `REPORT.md`
analyzes.
