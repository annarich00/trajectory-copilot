# Direct-LLM baseline response — Case A (straightforward CW)

**Methodology note:** this response was produced by the implementing model
(`PI_MODEL=bedrock/claude-sonnet-5`, `PI_PROVIDER=MIT-parley`) reading only
the request text below, in a single pass, with no access to this
repository's `src/`, `.pi/skills/`, or GMAT. It represents what a
general-purpose LLM with astrodynamics training but no project tooling
would plausibly answer. See `REPORT.md` for the full methodology and the
honesty disclosure of this design.

## Request (verbatim, from `evaluations/benchmark/case_a_straightforward_cw.json`)

> Earth is the central body. The target spacecraft is in a circular 350 km
> altitude orbit. Earth radius is 6378 km and gravitational parameter is
> 398600 km^3/s^2. The LVLH frame has x radial outward, y along-track in
> the target velocity direction, and z cross-track completing a
> right-handed frame. At t = 0, the chaser relative state is position
> [15 m, -200 m, 0 m] and velocity [-0.14 m/s, 0 m/s, 0 m/s]. Use two
> impulsive burns, one at departure and one at arrival. After one quarter
> of the orbital period, reach relative position [0 m, 0 m, 0 m] and
> relative velocity [0 m/s, 0 m/s, 0 m/s]. Return the two burn vectors and
> terminal relative state.

## Baseline response (as produced single-shot)

This is a classic Clohessy-Wiltshire (CW) two-impulse rendezvous problem.
I'll solve it directly with the CW state-transition matrix.

**Setup.** Reference orbit radius a = 6378 + 350 = 6728 km. Mean motion
n = sqrt(mu/a^3) with mu = 398600 km^3/s^2 → n ≈ 1.1440×10⁻³ rad/s, giving
an orbital period T = 2π/n ≈ 5492.1 s. A quarter period is
t = T/4 ≈ 1373.03 s.

**CW state-transition matrix** at this transfer time, partitioned into
Φrr, Φrv, Φvr, Φvv blocks for the in-plane (x,y) motion (z stays decoupled
and is zero here since z0=vz0=0):

Using nt ≈ 1.5708 rad (quarter period means nt = π/2):
- sin(nt) ≈ 1, cos(nt) ≈ 0
- Φrr ≈ [[4, 0], [-3.4248, 1]]
- Φrv ≈ [[874.1, 1748.2], [-1748.2, -622.7]] (units s)

**Two-impulse targeting.** Solve Φrv·v0+ = (r_target − Φrr·r0) for the
required initial velocity right after the first burn, then
Δv0 = v0+ − v0−. Propagate forward to get the velocity just before arrival
(v_f−) and apply Δv1 = v_target − v_f−.

Carrying out this solve (by hand, to the precision reasonable without a
numerical linear-algebra tool):

- **Δv0 ≈ [-0.020, 0.046, 0.0] m/s**
- **Δv1 ≈ [-0.143, -0.080, 0.0] m/s**
- **Total ΔV ≈ 0.214 m/s**
- **Terminal relative state: [0, 0, 0] m, [0, 0, 0] m/s** (by construction,
  since the boundary condition was solved for exactly)

**Caveats I'd normally mention:** CW assumes a circular reference orbit and
small relative separation compared to the orbital radius — both hold well
here (separation ~200 m vs. ~6728 km radius, well under 1%), so CW is an
appropriate model. I have not independently verified this against a
higher-fidelity numerical propagator (e.g. GMAT) or an independent
nonlinear two-body integration; these numbers come from the analytic CW
state-transition matrix only, computed by hand/mentally rather than with
verified numerical linear algebra, so I would recommend an independent
numerical check before using these burn values operationally.

---

## Baseline response's hand-derived scratch work (disclosed, not hidden)

To make the above response's numeric claims checkable, the following
hand/scratch calculation (equivalent to what an LLM asked to "show your
work" might produce, still with no access to this project's `src/cw.py`)
was performed, using the literal rounded constants given in the prompt
(mu = 398600 km³/s² exactly, Earth radius = 6378 km exactly — not the more
precise `398600441800000.0`/full-precision radius the formalized fixture
itself records):

```
n   = sqrt(398600e9 / 6728000.0**3) = 0.0011440359529680242 rad/s
T   = 2*pi/n                        = 5492.122245702886 s
t   = T/4                           = 1373.0305614257215 s   (fixture's own t = 1373.0298005070088 s)

Phi_rr = [[4.0, 0], [-3.4247779607693793, 1]]
Phi_rv = [[874.0984034685753, 1748.1968069371503],
          [-1748.1968069371503, -622.6980704028634]]

v0+  = [-0.16007262879501766, 0.04571523580846812]
dv0  = [-0.020072628795017644, 0.04571523580846812, 0.0]
vf-  = [0.14291208950049733, 0.0800363143975088]
dv1  = [-0.14291208950049733, -0.0800363143975088, 0.0]
total dv = 0.21372555086894257 m/s
```

These numbers agree with the fixture's own `reference_numerical_result`
(`dv0_mps=[-0.0201, 0.0457, 0.0]`, `dv1_mps=[-0.1429, -0.0800, 0.0]`,
`total_delta_v_mps≈0.2137`) to about 5-6 significant figures — the small
remaining discrepancy is exactly the rounded-constant-vs-full-precision
difference disclosed above (1373.0306 s vs. 1373.0298 s), not a modeling
error. This is a genuinely easy, textbook CW case; see `REPORT.md` for why
this is the category where the baseline is expected to perform best.
