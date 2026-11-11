# Session summary — 2026-10-30 (replaces 2026-10-28 version)

Context handoff for the next agent session on Trajectory CoPilot. Read this
before starting work. The operator has a demo for her PI on Tuesday; the top
priority for the next session is finishing demo prep (section 1), then
picking up `TJC-17` (section 2), then resuming the normal Backlog queue
(section 3).

## 1. PI demo prep for Tuesday — status and next steps

### What's ready now

A live-runnable demo script exists and has been run successfully, fresh,
multiple times in this sandbox with a real installed
`GmatConsole-R2026a`/`GMAT-R2026a`:

**`artifacts/manual_runs/pi_demo_live/run_pi_demo.py`**

```bash
cd /home/anna_ford/projects/class_example_traj_copilot
.venv/bin/python artifacts/manual_runs/pi_demo_live/run_pi_demo.py --case all
# or individually: --case one_period | --case quarter_period | --case two_body
```

Three cases, all confirmed working live just now, all producing real
captured GMAT GUI (OrbitView) PNG screenshots (not SVG fallback):

| Case | Scenario | Real result just observed |
|---|---|---|
| `one_period` | Operator's original request: CW two-burn rendezvous, 1000 m along-track offset, one full orbital period, zero terminal velocity | `NUMERICAL_DISAGREEMENT` (WARNING), position error 2.81 m vs. 1 m tolerance — **expected**, not a bug (see below) |
| `quarter_period` | Same scenario, transfer time = T/4 (1388.406068 s) instead of one full period | `VERIFIED`, PASS, position error 0.196 m |
| `two_body` | Bounded two-body RK4 coast (not CW): chaser at 7,778 km radius, same case as the committed `evaluations/benchmark/case_c_two_body.json` | `VERIFIED`, PASS, position error 0.0022 m |

**Why case `one_period` disagrees with GMAT (the operator's PI will likely
expect this, not be surprised by it):** at exactly one orbital period
(`n·t = 2π`), the CW state-transition matrix's `Phi_rv` block is numerically
singular (`cond ≈ 7.7e16`); `src/cw.py::two_burn_targeting` correctly detects
this and returns an SVD minimum-norm fallback (`status="singular-reachable"`)
rather than fabricating a unique answer. That SVD answer, propagated through
GMAT's full nonlinear two-body dynamics, lands 2.81 m off the exact target —
not because anything is broken, but because CW is a *linearized
approximation* being checked against the *true nonlinear* propagation over a
full-period coast, and linearization error grows with elapsed time. A real
sweep this session (same case, varying transfer time) showed the pattern
cleanly: T/8→0.04 m, T/4→0.20 m, 3T/4→2.35 m, T→2.81 m, 2T→5.58 m, with
extra error exactly at the `n·t = kπ` singular boundaries (`T/2`, `T`, `2T`).
This is textbook CW behavior and a good teaching moment, not a defect.

**Separately, case `two_body` answers the operator's question "shouldn't my
RK4 propagator line up with GMAT?":** yes, and it does, to 2.2 mm — because
`src/twobody.py::propagate_cartesian_state` and GMAT's own two-body script
(`Prop.Type = RungeKutta4`, 1 s fixed step, in `src/gmat_verify.py`) are
*both* numerical RK4 integrators of the same equations of motion, so RK4-vs-
RK4 naturally agrees far more tightly than CW's closed-form linearization
vs. GMAT's nonlinear RK4 does. This is a good side-by-side contrast to show
the PI alongside `one_period`.

### Poliastro — NOT part of any of the above, confirmed live

The operator asked whether Poliastro (`src/poliastro_verify.py`) double-
checks these results. Confirmed directly this session:
`verify_against_poliastro(...)` returns `UNAVAILABLE` right now in this
sandbox (no provisioned environment; `TRAJECTORY_COPILOT_POLIASTRO_PYTHON`
is unset). Even when provisioned, it only ever cross-checks the bounded
two-body RK4 fallback (`src/twobody.py`) — never CW — per
`docs/poliastro-verification-architecture.md`'s own stated scope. It is not
called anywhere in `src/workflow.py` (zero references) and is not part of
`run_rendezvous_workflow` or the `/rendezvous` prompt pipeline. It is a
separate, manual, developer-only verification step
(`uv venv --python 3.10 ...; pytest tests/test_poliastro_verify.py`).

### `.pi/prompts/rendezvous.md` — edited this session, NOT YET COMMITTED

Two changes were made (confirm via `git diff .pi/prompts/rendezvous.md`
before committing):

1. **Step 1 fix (important — would have broken the live Case C demo if
   unfixed):** the formalizer is scoped only to two-spacecraft LVLH
   requests, so a single-spacecraft inertial-Cartesian coast request
   (exactly what `two_body` above is) correctly comes back `OUT OF SCOPE`
   *from the formalizer specifically* — but the prompt previously said to
   stop and report OUT OF SCOPE unconditionally, which would have dead-
   ended the two-body case instead of routing it onward. Fixed to proceed
   to model selection in that specific case, per `reference/SOURCE.md` §C
   and the already-committed `evaluations/benchmark/case_c_two_body.json`
   precedent.
2. **New step 6:** states plainly that Poliastro is non-default, two-body-
   only, and not currently provisioned, so an agent won't claim it silently
   ran alongside GMAT.

**Next-session action:** review this diff, decide if it should be committed
as its own small task (or folded into whichever task touches the prompt
next), then run a *real* dry-run through the actual `/rendezvous` prompt
(not just the standalone script) before Tuesday, using the three exact
natural-language requests below.

### Exact live-demo requests to run through `/rendezvous` before Tuesday

```
/rendezvous Earth is the central body, R_earth = 6378.137 km, μ = 398600.4418 km³/s². The target is in a circular orbit at 400 km altitude. LVLH frame: x radial outward, y along-track, z cross-track, right-handed. At t = 0, the chaser relative position is [0 m, 1000 m, 0 m] and relative velocity is [0 m/s, 0 m/s, 0 m/s]. Use two impulsive burns, one at departure and one at arrival. After one orbital period, reach relative position [0 m, 0 m, 0 m] and relative velocity [0 m/s, 0 m/s, 0 m/s]. Return the two burn vectors and terminal relative state.
```

```
/rendezvous Earth is the central body, R_earth = 6378.137 km, μ = 398600.4418 km³/s². The target is in a circular orbit at 400 km altitude. LVLH frame: x radial outward, y along-track, z cross-track, right-handed. At t = 0, the chaser relative position is [0 m, 1000 m, 0 m] and relative velocity is [0 m/s, 0 m/s, 0 m/s]. Use two impulsive burns, one at departure and one at arrival. After 1388.406068 seconds (one quarter of the target's orbital period), reach relative position [0 m, 0 m, 0 m] and relative velocity [0 m/s, 0 m/s, 0 m/s]. Return the two burn vectors and terminal relative state.
```

```
/rendezvous A spacecraft is in Earth orbit with an initial inertial Cartesian state position [7778000, 0, 0] m, velocity [0, 7158.7124559338245, 0] m/s. Earth's gravitational parameter is 398600441800000.0 m^3/s^2. Propagate this state forward 900 seconds under point-mass gravity only (no thrust, no perturbations, no targeting). Report the final inertial Cartesian state.
```

Run each as a separate turn so each gets its own full pipeline trace and a
fresh verdict to narrate live.

### A related, deliberately NOT pursued extension

The operator asked about adding velocity-unconstrained / N-burn CW targeting
(matching her PI's narrower one-burn lecture derivation, pp. 9–10 of
`L21-Clohessy-Wiltshire Dynamics.pdf`, and her own `cw-pareto` repo's
closed-form trade-space). Decided **not to implement this now**. Important
finding if revisited later: dropping the terminal-velocity constraint does
**not** fix the `one_period` GMAT disagreement above — confirmed by actually
running it (position error stayed exactly 2.81 m) — because that
disagreement happens during the burn-1-to-coast arc, before any second burn
fires; it's pure CW linearization error, not a velocity-matching artifact.
If this is picked up later, scope it as two separate efforts: a small,
bounded "velocity-unconstrained target" extension, and a much larger,
separately-scoped "arbitrary N-burn" epic (that's an optimization problem,
not a linear boundary-value solve like today's two-burn `Phi_rv` inversion).

## 2. New Backlog task this session: TJC-17 (pick up next, High priority)

**TJC-17 — Fix `attempt_gmat_gui_screenshot`'s silent Xvfb-launch-failure
fallback to a broken real DISPLAY.** Created, **not started**.

Root cause, confirmed directly this session: TJC-9 made the real GMAT GUI
screenshot attempt-by-default via `src/gmat_verify.py`'s self-managed Xvfb
(`_launch_managed_xvfb`), specifically so the capture never depends on the
sandbox's real, broken, WSLg-forwarded `DISPLAY=:0`. But one real manual run
(`artifacts/manual_runs/circular_leo_one_period_rendezvous/`) recorded
`gui_screenshot_attempt.reason` showing it fell back to the real
`DISPLAY=:0` anyway (silently, when `_launch_managed_xvfb` failed to start
for that one run) — and capture against `:0` reliably returns a blank image
(the same documented GPU/compositor limitation that crashes an interactive
GMAT launch). A standalone retry moments later succeeded cleanly, confirming
the failure is transient/racy, not structural. Five ACs cover: making the
fallback observable in the result, retrying before falling back, picking an
explicit non-silent behavior if retry also fails, regression tests, and
re-confirming the operator's exact case now reliably gets `gmat_gui`.

## 3. Current Backlog queue (after TJC-17)

Current To Do order (confirmed via `backlog task list --plain` this
session): **TJC-17** (new, High, pick up next) → **TJC-5 → TJC-6 → TJC-7**
(the pre-existing required order from the 2026-10-28 session, still unstarted) →
(TJC-10...TJC-16 family, any order, not blocking) → **TJC-1.23 last**
(blocked on TJC-1.22, TJC-5, TJC-6, TJC-7, TJC-9 — TJC-9 is now Done).

TJC-9 (make `run_rendezvous_workflow` attempt a real GMAT GUI screenshot by
default) was completed and merged this session — commit `9b626a6` on
`master`, via an isolated worktree/branch per
`docs/task-commit-policy.md`. All 6 ACs checked with real evidence,
including a real run against installed GMAT (not just test mocks). TJC-17
above is a direct follow-up found while using TJC-9's new default behavior,
not a flaw in TJC-9's own completed scope.

The `TJC-16`/`TJC-16.1`–`TJC-16.5` family (demo visualization pipeline) and
`TJC-6.1` (CW singularity property coverage) are pre-existing, untouched
this session — still To Do, Medium priority, not blocking.

## 4. Open items / things to watch

- `.pi/prompts/rendezvous.md` has uncommitted edits from this session (see
  section 1) — confirm with `git diff .pi/prompts/rendezvous.md` and decide
  how to land them (own small task vs. folded into the next relevant task)
  before/after the Tuesday demo.
- `GmatLog.txt` (repo root) and `artifacts/manual_runs/` are untracked
  scratch/demo artifacts from manual runs this session and the prior one.
  `artifacts/manual_runs/pi_demo_live/` specifically should probably be kept
  (it's the demo script) but reviewed for whether its generated
  `results/` subdirectory needs `.gitignore` treatment like
  `evaluations/baseline_comparison/workflow_artifacts/` already has.
- Several `backlog/tasks/*.md` files are untracked or modified from a prior
  session (TJC-16 family, TJC-6.1, TJC-5/6 ordinal edits) — these were
  already present at the start of this session, not changed by it; confirm
  their status before committing unrelated work on top of them.
- This file replaces the 2026-10-28 version; fold anything durable into the
  right place (Backlog task notes, README, or the educational site) and
  delete/archive this file once absorbed, per the project's "don't leave
  stale docs lying around" convention.
