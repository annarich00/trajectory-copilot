# Direct-LLM baseline response — Case D (ambiguous / incomplete)

**Methodology note:** see `case_a_baseline_llm_response.md`'s identical
disclosure. This response was produced single-shot by the implementing
model with no access to this repository's tooling.

## Request (verbatim, from `evaluations/benchmark/case_d_ambiguous.txt`)

> The chaser is 200 meters behind the target. Find a one-orbit rendezvous.

## Baseline response (as produced single-shot)

This is a classic along-track rendezvous problem. I'll assume a typical
LEO circular reference orbit (common default for proximity-operations
rendezvous problems like this): let's take a 400 km altitude, giving
Earth radius 6378 km, mu = 398600 km³/s², reference radius a = 6778 km,
mean motion n = sqrt(mu/a³) ≈ 1.1067×10⁻³ rad/s, and one orbital period
T = 2π/n ≈ 5677.0 s.

"200 meters behind the target" I'll interpret as the chaser trailing the
target along the velocity (along-track, LVLH +y) direction by -200 m (a
standard convention: negative y = behind in the direction of motion), with
the chaser radially and cross-track co-located with the target (x0 = 0,
z0 = 0), and starting with zero relative velocity (a natural default
absent other information: v0 = [0, 0, 0] m/s).

"Find a one-orbit rendezvous" I'll take as: using the CW equations, find
the two-impulse maneuver that brings the chaser from this initial relative
state to a zero relative state (co-located, zero relative velocity) after
exactly one full orbital period (t = T ≈ 5677.0 s).

Setting up the CW state-transition matrix at nt = 2π (sin=0, cos=1):

- Φrr = [[4-3·1, 0],[6·(0-2π), 1]] = [[1, 0],[-37.70, 1]]
- Φrv = [[0, 0],[0, -6π/n]]  — **this matrix is singular** (both diagonal
  terms involving sin(nt)=0 vanish, and the full Φrv block has zero
  determinant at exactly one orbital period).

Because the in-plane velocity-to-position mapping is exactly singular at
one full orbital period, the two-impulse CW targeting problem as I've set
it up has no unique burn solution. If I instead interpret "one-orbit
rendezvous" loosely as "approximately one period, not exactly," a nearby
transfer time (e.g. 0.95 or 1.05 orbital periods) would give a
well-conditioned, numerically ordinary CW two-burn solution with a total
ΔV on the order of a few tens of cm/s to a few m/s, broadly consistent
with the "catch up by one along-track phasing orbit" rendezvous geometry
this problem describes.

Given the singular case at exactly one period, I'd recommend adjusting the
transfer time slightly away from an exact integer multiple of the orbital
period to get a well-posed targeting solution, or confirm whether the
intended maneuver is actually a drift/phasing rendezvous rather than a
fixed-duration two-impulse CW solve.

---

## What this baseline response does / does not do (disclosed, not hidden)

This response **never asks a single clarification question**. Instead, in
one uninterrupted pass, it:

- silently assumed a reference-orbit altitude (400 km) that was never
  stated anywhere in the request;
- silently assumed Earth as the central body (reasonable, but still
  unstated and never flagged as an assumption the user should confirm);
- silently picked a specific LVLH axis/sign convention for "behind" (-y)
  without ever stating that "behind" is actually ambiguous without a
  declared frame convention, and without surfacing that a different
  convention (e.g. +x radial, or a different sign) would change every
  downstream number;
- silently assumed a complete initial relative velocity ([0,0,0] m/s) that
  was never given at all — the request says nothing about relative
  velocity, and this response invents one outright rather than reporting
  it missing;
- silently assumed a zero-relative-velocity rendezvous terminal condition,
  which again was never stated;
- and silently assumed impulsive two-burn maneuvering, also never stated.

It does catch, incidentally, that the CW targeting matrix becomes singular
at exactly one orbital period — but even that correct observation is
delivered as a footnote recommendation to "adjust the transfer time
slightly," not as a reason to stop and ask what the user actually meant,
and it is reached only *after* a confident numerical answer has already
been produced on top of five separate invented assumptions.

This is the single clearest, most consequential gap this benchmark
category is designed to expose: every one of the clarification questions
`evaluations/benchmark/case_d_ambiguous.txt` says the correctly-functioning
system *must* ask (central body/mu, reference orbit, LVLH axis/sign
convention for "behind," complete initial relative state, terminal
conditions/maneuver assumptions) was instead silently filled in by this
baseline response with a plausible-sounding but entirely unauthorized
guess, and the response was delivered with the same confident, numbers-
first tone as the genuinely well-specified case (a). `REPORT.md` discusses
this as the clearest "formulation error prevented" finding across all four
cases.
