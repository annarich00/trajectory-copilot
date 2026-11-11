# Stored demo cases for the web demo interface

Source: project owner, supplied during the web-interface design session.
Context: `docs/web-interface-decisions.md`. These are the first stored runs
for the static site (Phase 1) and the replay examples for the live app.

## Naming

These are **demo cases** and are numbered Demo A, B and C. They are *not* the
same as the benchmark cases in `evaluations/benchmark/` (A straightforward CW,
B boundary, C two-body, D ambiguous), and not the "Case B" on the course
walkthrough page (1000 m offset). Always say "Demo A/B/C" in tasks, code and
UI text to avoid confusion.

## Demo A: one orbital period, expect NUMERICAL_DISAGREEMENT

A failure example. The CW model and GMAT disagree beyond the strict tolerance
but within the warning margin. The UI must show this honestly as
`NOT VERIFIED`, not as a pass.

```
/rendezvous Earth is the central body, R_earth = 6378.137 km, μ = 398600.4418 km³/s². The target is in a circular orbit at 400 km altitude. LVLH frame: x radial outward, y along-track, z cross-track, right-handed. At t = 0, the chaser relative position is [0 m, 10000 m, 0 m] and relative velocity is [0 m/s, 0 m/s, 0 m/s]. Use two impulsive burns, one at departure and one at arrival. After one orbital period, reach relative position [0 m, 0 m, 0 m] and relative velocity [0 m/s, 0 m/s, 0 m/s]. Return the two burn vectors and terminal relative state.
```

## Demo B: quarter period, expect VERIFIED

The same scenario over T/4 (1388.406068 s). CW is accurate enough over the
shorter arc to pass GMAT's tolerance.

```
/rendezvous Earth is the central body, R_earth = 6378.137 km, μ = 398600.4418 km³/s². The target is in a circular orbit at 400 km altitude. LVLH frame: x radial outward, y along-track, z cross-track, right-handed. At t = 0, the chaser relative position is [0 m, 10000 m, 0 m] and relative velocity is [0 m/s, 0 m/s, 0 m/s]. Use two impulsive burns, one at departure and one at arrival. After 1388.406068 seconds (one quarter of the target's orbital period), reach relative position [0 m, 0 m, 0 m] and relative velocity [0 m/s, 0 m/s, 0 m/s]. Return the two burn vectors and terminal relative state.
```

## Demo C: two-body coast, expect VERIFIED

A single-spacecraft inertial coast. It exercises the step-1 exception in
`.pi/prompts/rendezvous.md` (formalizer returns OUT OF SCOPE for this shape;
the pipeline proceeds to the two-body path). Per TJC-16.5, the three plot
stages are `not_generated` on this path, each with a reason. The UI must show
that, and must not substitute another plot.

```
/rendezvous A spacecraft is in Earth orbit with an initial inertial Cartesian state position [7778000, 0, 0] m, velocity [0, 7158.7124559338245, 0] m/s. Earth's gravitational parameter is 398600441800000.0 m^3/s^2. Propagate this state forward 900 seconds under point-mass gravity only (no thrust, no perturbations, no targeting). Report the final inertial Cartesian state.
```

## Capture notes

- Expected outcomes above are the owner's expectations. The stored runs must
  record what the pipeline actually returned. If an outcome differs, record
  the real result and flag the difference in the task notes.
- Earlier runs exist under `artifacts/manual_runs/` (for example
  `pi_demo_live/` and `circular_leo_400km_one_period_rendezvous*`), but they
  use different inputs (for example a 1000 m offset). Check the inputs before
  reusing any of them; do not relabel an earlier run as a demo case.
- A recorded `NEEDS CLARIFICATION` example is not yet chosen. The benchmark
  `evaluations/benchmark/case_d_ambiguous.txt` is a candidate.
