# Rendezvous Pipeline Result — `circular_leo_400km_one_burn_free_velocity_rendezvous`

Run through the complete `orbital-problem-formalizer` →
`orbital-model-selector` → `src/workflow.py::run_rendezvous_workflow`
pipeline, with `gmat_executable="GmatConsole-R2026a"`.

## Request

Earth is the central body, `R_earth = 6378.137 km`, `mu = 398600.4418 km^3/s^2`.
The target is in a circular orbit at 400 km altitude. LVLH frame: x radial
outward, y along-track, z cross-track, right-handed. At t = 0, the chaser
relative position is `[0 m, 1000 m, 0 m]` and relative velocity is
`[0 m/s, 0 m/s, 0 m/s]`. Use one impulsive burn at departure only. After one
orbital period, reach relative position `[0 m, 0 m, 0 m]`; do not constrain
terminal relative velocity — a nonzero drift-through velocity at rendezvous
is acceptable. Return the burn vector and terminal relative state.

## Step 1 — `orbital-problem-formalizer`

### Scope
- Classification: supported — derived
- Reason: Two spacecraft (target/chaser), circular LEO reference orbit,
  impulsive maneuver, LVLH relative state, one-period time of flight — all
  within the supported class. — derived

### Participants
- Central body: Earth — specified
- Target/chief: target (circular 400 km orbit) — specified
- Chaser/deputy: chaser — specified

### Reference Orbit
- Circularity: circular — specified
- Altitude: 400 km — specified
- Radius or orbital elements: r = R_earth + altitude = 6378.137 km + 400 km
  — derived (formula shown, value not computed)
- Gravitational parameter: mu = 398600.4418 km^3/s^2 — specified
- Mean motion or period: n = sqrt(mu / r^3), T = 2*pi / n — derived
  (formula shown, value not computed)

### Relative Frame and State
- Frame: LVLH/Hill — specified
- LVLH convention: x radial outward, y along-track, z cross-track,
  right-handed — specified
- Initial relative position: `[0 m, 1000 m, 0 m]` — specified
- Initial relative velocity: `[0 m/s, 0 m/s, 0 m/s]` — specified

### Terminal Conditions
- Relative position: `[0 m, 0 m, 0 m]` — specified
- Relative velocity: unconstrained — not required to reach any particular
  value; a nonzero drift-through velocity is explicitly acceptable —
  specified
- Requested outputs: burn vector and terminal relative state — specified

### Timing and Maneuvers
- Time of flight: one orbital period of the target's reference orbit
  (T = 2*pi / n, derivable from r and mu above) — derived
- Period count: 1 — specified
- Maneuver assumptions: exactly one impulsive burn, at departure (t = 0)
  only — no second/arrival burn — specified

### Blocking Issues
- None

### Clarification Questions
- None

### Readiness
READY TO SOLVE

### Formalization Summary
A fully specified single-impulse rendezvous: chaser starts 1000 m
along-track from a target in a circular 400 km Earth orbit and must reach
zero relative position after exactly one orbital period, using one
departure-only burn, with terminal relative velocity explicitly left free.

## Step 2 — `orbital-model-selector` assessment

| # | Item | Assessment | Evidence |
|---|------|------------|----------|
| 1 | Circularity | supported | Reference orbit explicitly specified as circular at 400 km altitude. |
| 2 | Locality | supported | Separation 1000 m along-track vs. r ≈ 6,778,137 m (ratio ≈ 1.5×10⁻⁴); well under `validate_cw_use`'s "large separation" warning threshold. |
| 3 | Duration/regime | supported | Fixed transfer duration is exactly one orbital period (single revolution); not "more than ~two orbital periods". |
| 4 | Frame | supported | Explicit right-handed LVLH, x radial outward / y along-track / z cross-track, `[x,y,z,xdot,ydot,zdot]` SI ordering, matching `src/cw.py`'s convention. |
| 5 | Other physics | supported | Earth point-mass dominance, no perturbations stated, chaser relative velocity initially zero, impulsive (not finite-burn/continuous-thrust) maneuver assumed. |
| 6 | Maneuver assumptions | **violated** | `src/cw.py`'s CW rendezvous contract (`CW_RENDEZVOUS_ASSUMPTIONS`, used by `two_burn_targeting`/`solve_cw_rendezvous`) is built on **exactly two** impulsive burns — one at departure and one at arrival — that together drive the full six-element terminal state `[x,y,z,ẋ,ẏ,ż]` to a specified target. This request explicitly asks for **one burn only** (departure, no arrival burn) and explicitly leaves terminal velocity **unconstrained**. Neither `two_burn_targeting` nor any other function in `src/cw.py` solves a single-impulse / free-terminal-velocity boundary-value problem; there is no "one-burn CW targeting" entry point. |

**Violated or unknown assumptions:** item 6 (maneuver assumptions) is
violated; items 1–5 are supported.

**Selection:** Because a required item (`maneuver_assumptions`) is
violated, CW rendezvous is rejected outright (`select_model` never
reaches the boundary/qualified branch). The case is then checked against
the bounded two-body coast contract (`src/twobody.py`): that contract
requires a **coast-only** request (no commanded burn at all) with a given
inertial Cartesian state and fixed duration. This request commands one
burn, so it is **not** a coast-only request either — the two-body fallback
contract is also not satisfied.

Both scoped deterministic implementations are therefore inapplicable, so
`select_model` returns:

**Selection: `UNSUPPORTED`**

- **Reasons:** "Violated CW assumption(s): maneuver_assumptions." and "The
  case does not satisfy the bounded two-body coast contract ... or
  requests an unsupported capability (targeting, maneuvers, optimization,
  thrust, or perturbations)."
- **Deterministic tool handoff:** none — `deterministic_tool=None`. Per
  the model-selector skill, an `UNSUPPORTED` result must not recommend an
  unimplemented higher-fidelity solver.
- **Verification handoff:** not applicable — `gmat-rendezvous-verification`
  only receives candidates that already have a named deterministic tool.

No burn, delta-v, or final state has been computed or reported at this
point; this step is reasoning over the recorded assumptions only. (The
`select_model` call that produced this exact table ran only inside the
single real `run_rendezvous_workflow(...)` call in Step 3 below — no
separate/early Python call to `src/cw.py`, `src/twobody.py`, or
`select_model` was made outside of that one entry point.)

## Step 3 — Real `run_rendezvous_workflow(...)` call

A `RendezvousCase` was constructed from exactly the Step 1/2 values
(`mu_m3_s2=398600.4418e9`, `reference_radius_m=6378137.0+400000.0=6778137.0`,
`initial_relative_state=[0.0, 1000.0, 0.0, 0.0, 0.0, 0.0]`,
`final_relative_state=None` because terminal velocity is explicitly
unconstrained and not a usable six-element target,
`transfer_time_s≈5553.624271252229`, and a `model_selection_case` encoding
the six-item table above, including `maneuver_assumptions="violated"` and
`is_coast_only_request=False` since a burn is commanded) and passed to:

```python
run_rendezvous_workflow(
    case,
    output_dir=Path("artifacts/manual_runs/circular_leo_400km_one_burn_free_velocity_rendezvous").resolve(),
    gmat_executable="GmatConsole-R2026a",
)
```

No direct call was made to `src/cw.py` or `src/twobody.py`.

## Step 4 — Final result

| Field | Value |
|---|---|
| `outcome` | `UNSUPPORTED` |
| `verified` | `False` |
| `verification_status` | `NOT VERIFIED: UNSUPPORTED` |
| `trust_statement` | "No deterministic solver or GMAT verification was attempted: model selection returned 'UNSUPPORTED', not a usable deterministic tool. Violated CW assumption(s): maneuver_assumptions. The case does not satisfy the bounded two-body coast contract (finite six-element inertial Cartesian state, positive mu, finite duration, positive RK4 step count, coast-only request) or requests an unsupported capability (targeting, maneuvers, optimization, thrust, or perturbations)." |

**This is neither `VERIFIED` nor a solver-only result — no solver ran at
all.** Because `select_model` returned `UNSUPPORTED`, `run_rendezvous_workflow`
short-circuited before any CW solve, any two-body coast propagation, and any
GMAT execution (`src/workflow.py::_unresolved_selection_result`). No burn
vector, delta-v, or terminal relative state can be reported, because none
was ever computed under the two scoped deterministic tools this project
supports (`src/cw.py::two_burn_targeting`/`solve_cw_rendezvous` and
`src/twobody.py::propagate_cartesian_state`).

### Artifacts

- Structured result: `artifacts/manual_runs/circular_leo_400km_one_burn_free_velocity_rendezvous/workflow_result.json`
- No GMAT script, screenshot, or report files exist for this case — none
  were generated, because the workflow stopped before the CW/two-body/GMAT
  stage.

## Step 5 — GMAT GUI

Not applicable: no request was made to open the interactive GMAT GUI, and
no GUI preview script was ever generated for this case (there is nothing
to preview — no solver ran). If the GMAT GUI is requested separately for
this or another case, an interactive GMAT window cannot be opened from
inside this sandboxed session (no GPU render-node path; WSLg/RDP never
forwards a rendered buffer to the user's real desktop even when a window
registers — see `src/gmat_verify.py::attempt_gmat_gui_screenshot`'s
docstring for the full diagnosis). The user would need to run, in their
own terminal:

```bash
cd /home/anna_ford/opt/GMAT/R2026a/bin
./GMAT-R2026a -r <path to the generated GUI preview script>
```

with a GUI preview script regenerated first for whichever case is actually
being visualized.
