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

## Demo A: one orbital period, measured NUMERICAL_DISAGREEMENT

A failure example. The CW model and GMAT disagree beyond the recorded tolerance:
the recorded run's position error is 281.46 m against a 20 m tolerance (velocity
error 0.00094833 m/s against 0.001 m/s). The UI must show this honestly as
`NOT VERIFIED`, not as a pass. Model selection is a *qualified* CW selection:
over a full period the two-impulse targeting matrix is singular but reachable
(`targeting_conditioning: boundary`), so the returned burns are a non-unique
SVD minimum-norm solution.

Recorded run: `artifacts/runs/demo-a-400km-one-period-10km-alongtrack/bridge/`.

```
/rendezvous Earth is the central body, R_earth = 6378.137 km, μ = 398600.4418 km³/s². The target is in a circular orbit at 400 km altitude. LVLH frame: x radial outward, y along-track, z cross-track, right-handed. At t = 0, the chaser relative position is [0 m, 10000 m, 0 m] and relative velocity is [0 m/s, 0 m/s, 0 m/s]. Use two impulsive burns, one at departure and one at arrival. After one orbital period, reach relative position [0 m, 0 m, 0 m] and relative velocity [0 m/s, 0 m/s, 0 m/s]. Return the two burn vectors and terminal relative state.
```

## Demo B: quarter period, measured NUMERICAL_DISAGREEMENT

The same scenario over T/4 (1388.406068 s). The owner's original expectation was
that CW would be accurate enough over the shorter arc to pass GMAT's tolerance.
The recorded run **passes**: the measured position error is 19.60 m
against a 20 m tolerance and velocity error 0.029826 m/s against 0.05 m/s, so the
real outcome is `NUMERICAL_DISAGREEMENT` / `NOT VERIFIED`, the same failure mode
as Demo A but a much smaller error (19.60 m versus Demo A's 281.46 m). The UI
must show the recorded FAIL, not the predicted pass.

Recorded run: `artifacts/runs/demo-b-400km-quarter-period-10km-alongtrack/bridge/`.

```
/rendezvous Earth is the central body, R_earth = 6378.137 km, μ = 398600.4418 km³/s². The target is in a circular orbit at 400 km altitude. LVLH frame: x radial outward, y along-track, z cross-track, right-handed. At t = 0, the chaser relative position is [0 m, 10000 m, 0 m] and relative velocity is [0 m/s, 0 m/s, 0 m/s]. Use two impulsive burns, one at departure and one at arrival. After 1388.406068 seconds (one quarter of the target's orbital period), reach relative position [0 m, 0 m, 0 m] and relative velocity [0 m/s, 0 m/s, 0 m/s]. Return the two burn vectors and terminal relative state.
```

## Demo C: 14 000 km along-track offset, measured UNSUPPORTED

A refusal example, supplied by the project owner to replace an earlier GEO
framing. It is the same 400 km circular LEO scenario, LVLH frame and quarter-
period timing as Demo B, with one change: the initial relative position is
`[0 m, 14000000 m, 0 m]`. That 14 000 km offset is 2.07x the 6778.137 km
reference radius (~118 deg of arc), which is not a local separation at all.

The recorded pipeline formalizes the request as `READY TO SOLVE` (every
required field is specified, so the refusal is a model-selection judgment, not
a formalizer scope rejection), and then `select_rendezvous_model` returns
`UNSUPPORTED` with `deterministic_tool: null` for two reasons: the violated CW
locality assumption, and the fact that a two-burn targeting request does not
satisfy the bounded two-body coast contract. The pipeline stops there. It must
not claim a CW solve, a bounded two-body fallback, or a GMAT verification
result; every downstream step is recorded as not called / not generated with a
truthful reason, and the UI must show those reasons and must not substitute
another plot.

Recorded run: `artifacts/runs/demo-c-400km-quarter-period-14000km-alongtrack/run_manifest.json`
(manifest only -- no solver, GMAT or plot artifacts exist, because none were
produced).

```
/rendezvous Earth is the central body, R_earth = 6378.137 km, μ = 398600.4418 km³/s². The target is in a circular orbit at 400 km altitude. LVLH frame: x radial outward, y along-track, z cross-track, right-handed. At t = 0, the chaser relative position is [0 m, 14000000 m, 0 m] and relative velocity is [0 m/s, 0 m/s, 0 m/s]. Use two impulsive burns, one at departure and one at arrival. After 1388.406068 seconds (one quarter of the target's orbital period), reach relative position [0 m, 0 m, 0 m] and relative velocity [0 m/s, 0 m/s, 0 m/s]. Return the two burn vectors and terminal relative state.
```

## Capture notes

- The headings above record what the pipeline actually returned. Demo A and
  Demo B were re-run through the real pipeline tools against GMAT R2026a; both
  recorded `NUMERICAL_DISAGREEMENT`. Demo B's heading originally predicted
  `VERIFIED`; the measured 19.60 m error replaced that prediction.
- Earlier runs exist under `artifacts/runs/manual/` (for example
  `pi_demo_live/` and `circular_leo_400km_one_period_rendezvous*`), and the
  earlier `artifacts/runs/earth-400km-*` captures are kept as prior evidence,
  but they use different inputs (for example a 1000 m offset) or lack the
  request text. Check the inputs before reusing any of them; do not relabel an
  earlier run as a demo case.
- Demo C replaced the earlier GEO `examples/geo_failure_case.yaml` framing with
  the owner-supplied 14 000 km LEO locality case above. It is an `UNSUPPORTED`
  model-selection refusal, not an `OUT_OF_SCOPE` formalizer stop and not the
  two-body coast example.
- A recorded `NEEDS CLARIFICATION` example is not yet chosen. The benchmark
  `evaluations/benchmark/case_d_ambiguous.txt` is a candidate.
