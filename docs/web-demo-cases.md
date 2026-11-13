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

## Demo C: GEO request, expect OUT_OF_SCOPE

A GEO-style out-of-scope example from `examples/geo_failure_case.yaml`. It
must stop after formalization identifies the request as outside the supported
primarily circular-LEO LVLH rendezvous scope. It must not claim a CW solve, a
bounded two-body fallback, or a GMAT verification result. Downstream steps
should be recorded as not called/not generated with truthful reasons; the UI
must show those reasons and must not substitute another plot.

```
problem_type: rendezvous
objective: minimize_delta_v
reference_orbit:
  orbit: geostationary
  altitude_m: 35786000
  radius_m: 42164000
  gravitational_parameter_m3_s2: 398600441800000.0
coordinate_frame:
  frame: LVLH
  convention: x radial, y along-track, z cross-track
initial_relative_state:
  position_m: [0.0, 14000000.0, 0.0]
  velocity_mps: [0.0, 0.0, 0.0]
terminal_conditions:
  position_m: [0.0, 0.0, 0.0]
  velocity_mps: [0.0, 0.0, 0.0]
timing:
  transfer_time_s: unknown
maneuver_constraints:
  burns: 2
  burn_type: impulsive
  max_delta_v_mps: unknown
dynamics_model: CW
```

## Capture notes

- Expected outcomes above are the owner's expectations. The stored runs must
  record what the pipeline actually returned. If an outcome differs, record
  the real result and flag the difference in the task notes.
- Earlier runs exist under `artifacts/runs/manual/` (for example
  `pi_demo_live/` and `circular_leo_400km_one_period_rendezvous*`), but they
  use different inputs (for example a 1000 m offset). Check the inputs before
  reusing any of them; do not relabel an earlier run as a demo case.
- Demo C now uses the GEO failure-case pattern from `examples/geo_failure_case.yaml` and is an OUT_OF_SCOPE stop, not the two-body coast example.
- A recorded `NEEDS CLARIFICATION` example is not yet chosen. The benchmark
  `evaluations/benchmark/case_d_ambiguous.txt` is a candidate.
