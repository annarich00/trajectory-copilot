# Direct-LLM baseline vs. complete structured workflow (TJC-1.22)

Evaluates `src/workflow.py::run_rendezvous_workflow` (TJC-1.16) against a
direct natural-language-to-LLM-answer baseline, across all four categories
of the versioned rendezvous benchmark (`evaluations/benchmark/`, TJC-1.9):
straightforward CW, boundary CW, CW-invalid/two-body, and
ambiguous/incomplete. **This report's conclusions are scoped to these four
cases and the narrow, supported rendezvous class this project implements
(circular-reference-orbit, impulsive, two-spacecraft LVLH rendezvous, plus
a bounded point-mass two-body coast fallback) — they are not a claim about
astrodynamics software, LLM capability, or formal verification in
general.**

## 1. Methodology

### 1.1 Why this comparison, and why it is honestly disclosed

TJC-1.22 asks for a comparison between "a direct natural-language-to-LLM-
answer baseline and the complete structured workflow." This sandboxed
worktree has no live LLM API access (no `anthropic`/`openai` packages, no
API keys, no network egress for that purpose), and this task's own
instructions direct the implementing agent not to attempt one.

**The baseline side of this comparison was therefore produced by the same
model implementing this task** (identified below), in the same session, as
a single-shot, un-scaffolded direct-answer exercise: for each of the four
benchmark request texts, the implementing model read only that request
text — not `src/`, not any `.pi/skills/*/SKILL.md` file, not
`src/model_selector.py`, not GMAT, not this report — and produced one
natural-language answer exactly as a general-purpose LLM with astrodynamics
training but no access to this project's deterministic tooling would. That
answer is recorded verbatim in `case_a_baseline_llm_response.md` through
`case_d_baseline_llm_response.md`, each with its own disclosed "scratch
work" appendix (hand arithmetic a baseline LLM might show if asked, still
produced without any project code) so every numeric claim is independently
checkable without implying the baseline secretly had access to `src/cw.py`.

This is stated explicitly as a *legitimate evaluation design choice given
this environment's constraints*, not a limitation to hide: it directly
tests the same underlying model/architecture's un-scaffolded, single-shot
output against its own scaffolded, tool-grounded output on identical
inputs — which is a realistic, and arguably more informative, version of
"direct LLM baseline vs. structured workflow" than an arbitrary third-party
model would be, since it isolates the effect of the *architecture*
(formalizer → model selector → deterministic solver → GMAT verification)
from any difference in underlying model capability.

### 1.2 Model/tool identity and versions (AC3)

| Component | Identity |
| --- | --- |
| Implementing model (both the baseline-answer author and the task executor) | `PI_MODEL=bedrock/claude-sonnet-5`, `PI_PROVIDER=MIT-parley` (read from this session's environment) |
| GMAT (numerical verification) | `GmatConsole-R2026a`, `Build Date: Mar 30 2026 10:09:27` (banner captured verbatim in each `case_*_workflow_result.json`'s `unified_verification_report.gmat.version_banner`) |
| Planetary ephemeris | DE405 (GMAT's default, per the same banner) |
| Python / numeric stack | `requirements-dev.txt`: `numpy==2.5.3`, `pytest==9.1.1` |
| Workflow entry point | `src/workflow.py::run_rendezvous_workflow` (TJC-1.16), unmodified by this task |
| Benchmark fixtures | `evaluations/benchmark/case_a_straightforward_cw.json`, `case_b_boundary_cw.json`, `case_c_two_body.json`, `case_d_ambiguous.txt` (TJC-1.9), unmodified by this task |

### 1.3 Full-workflow side: exactly what was run (AC1, AC3)

`evaluations/baseline_comparison/run_workflow_cases.py` builds each case's
`src/workflow.py::RendezvousCase`/`ModelSelectionCase` directly from the
numeric fields already recorded in the corresponding
`evaluations/benchmark/*` fixture (not re-typed ad hoc numbers), then calls
`run_rendezvous_workflow` for real. Reproduce with:

```
.venv/bin/python evaluations/baseline_comparison/run_workflow_cases.py --gmat GmatConsole-R2026a
```

This was run for real in this environment (`GmatConsole-R2026a` installed
and runnable) and produced the four committed
`case_a_workflow_result.json` .. `case_d_workflow_result.json` files, which
are the exact `WorkflowResult.to_dict()` output — not hand-transcribed or
summarized. For cases (a)/(b)/(c) this independently re-confirms (does not
replace) the already-committed, already-audited GMAT evidence in
`examples/cw_gmat_slice_example/`, `examples/benchmark_case_b_boundary/`,
and `examples/benchmark_case_c_two_body/` (TJC-1.9): the model selection,
solver outcome, and GMAT comparison numbers below match those directories'
`verification_result.json` exactly (same `dv0`/`dv1`/`total_delta_v`,
`position_error_m`, `velocity_error_mps`, `comparison.status`), as expected
since both exercise the exact same `src/cw.py`/`src/twobody.py`/
`src/gmat_verify.py` machinery against the same inputs. Case (d) short-
circuits before any model selection, solver, or GMAT call, exactly as
`src/workflow.py::_clarification_result` documents.

### 1.4 Deterministic inputs/outputs, tolerances, and artifacts (AC3)

Each `case_*_workflow_result.json` records (verbatim, inside
`unified_verification_report`): the exact structured facts/assumptions
used (`model_selection.assumptions`/`reasons`/`concerns`), the GMAT
executable path and version banner, the generated GMAT script's inputs
(`solver` block), the parsed numeric comparison
(`comparison.position_error_m`/`velocity_error_mps`/`status`), the declared
tolerances, the trajectory screenshot artifact's path/media type/validity
(`screenshot`), and a final `trust_statement` distinguishing "the solver
succeeded" from "GMAT independently verified it." The exact tolerances used
match each fixture's own `gmat_tolerance` field (position 1.0 m, velocity
0.001 m/s, and delta-v 0.001 m/s for cases a/b; position 1.0 m, velocity
0.001 m/s for case c, which has no delta-v since it is a coast, not a
maneuver).

## 2. Per-case results and analysis (AC4)

### Case (a) — straightforward CW

**Request:** circular 350 km LEO, 200 m along-track/15 m radial
separation, quarter-period two-burn rendezvous to zero relative state.

**Direct-LLM baseline** (`case_a_baseline_llm_response.md`): correctly
identified this as a textbook CW problem, computed the mean motion, CW
state-transition blocks, and two-burn solution by hand, arriving at
Δv0 ≈ [-0.0201, 0.0457, 0.0] m/s, Δv1 ≈ [-0.1429, -0.0800, 0.0] m/s, total
ΔV ≈ 0.2137 m/s — agreeing with the fixture's GMAT-cross-checked reference
to ~5-6 significant figures. It correctly stated the CW model-validity
assumptions hold (circular, small separation) and explicitly disclosed
that it had not independently verified the result against a numerical
propagator.

**Full workflow** (`case_a_workflow_result.json`): `select_model` returned
`CW rendezvous`, `qualified=False`, all seven assumption items
`supported`; `src.cw.two_burn_targeting` returned `status="unique"`
(well-conditioned); a real GMAT run reached `comparison.status="PASS"`
with `position_error_m≈0.00794`, `velocity_error_mps≈1.17e-5`, both well
inside tolerance; `verified=True`. A valid SVG trajectory screenshot
artifact was produced and validated.

**Finding:** on this clean, well-specified case, the direct-LLM baseline's
*numbers* were essentially correct — this is the one case where a careful
baseline answer and the structured workflow agree numerically. The
difference is in **evidentiary status**, not correctness: the baseline's
"I have not independently verified this" is an honest disclaimer with no
mechanism behind it, while the workflow's `VERIFIED` status is backed by
an actual independent GMAT run with recorded numeric error bounds and a
screenshot artifact. For this specific easy case, the architecture adds
auditability rather than catching an error.

### Case (b) — boundary CW (singular-but-reachable targeting)

**Request:** identical geometry to case (a), but a HALF-period transfer
instead of a quarter-period one — the exact transfer time at which CW's
in-plane velocity-mapping block (Φrv) becomes singular (reference/SOURCE.md
§B.3/D).

**Direct-LLM baseline** (`case_b_baseline_llm_response.md`): solved only
the 2×2 in-plane sub-block (which happens to be well-conditioned, since
the genuine singularity for this case lives in the decoupled cross-track
row, trivially zero here), producing Δv0 ≈ [0.073, -0.030, 0.0] m/s,
Δv1 ≈ [-0.067, -0.004, 0.0] m/s, total ΔV ≈ 0.146 m/s — numerically close
to the workflow's own result, but delivered with **no qualification, no
mention of a boundary condition, and no recommendation for independent
verification beyond a generic "I haven't checked this numerically"**
disclaimer identical in tone to the easy case (a). It never constructs or
inspects the general 3-DOF Φrv matrix, so it never notices that this exact
transfer time is a documented targeting-conditioning edge case.

**Full workflow** (`case_b_workflow_result.json`): `select_model` returned
`CW rendezvous`, `qualified=True`, with `targeting_conditioning:
"boundary"` explicitly surfaced and two concrete concerns recorded: that
the returned velocity is a non-unique SVD minimum-norm solution, and that
independent numerical verification is recommended before treating this as
a clean pass. `two_burn_targeting` reported `status="singular-reachable"`,
`condition_number≈8.90e16`, `rank=2` (of 3) — an explicit, structured
record of exactly which signal is marginal. GMAT still verified this
particular instance (`comparison.status="PASS"`,
`position_error_m≈0.0465`, `velocity_error_mps≈3.07e-5`), but the result
is reported as a **qualified** VERIFIED, not an unqualified one, matching
`src/model_selector.py`'s documented AC4 contract that this is a surfaced
signal, not an invented universal numeric threshold.

**Finding — error type prevented/detected:** the direct-LLM baseline
**silently missed a documented targeting-conditioning boundary condition**
that the structured workflow explicitly detects and surfaces as a
qualified result with named concerns. This is the clearest
*verification/discrepancy-handling* gap in this benchmark: a user reading
only the baseline's answer would have no way to know this transfer time is
special, while a user reading the workflow's output is told exactly why
(singular-but-reachable Φrv) and exactly what to do about it (independent
numerical check before trusting it as a clean pass).

### Case (c) — CW-invalid / two-body fallback

**Request:** a single-spacecraft inertial-Cartesian point-mass coast (not
a rendezvous at all — 1,000 km radial offset from an implied 6,778 km
circular reference, propagated 900 s, no burns, no targeting).

**Direct-LLM baseline** (`case_c_baseline_llm_response.md`): correctly
recognized this as a two-body circular-orbit propagation (not CW), checked
eccentricity ≈ 0 from r0/v0, and used the circular-orbit angular-rate
shortcut to compute a final state matching the fixture's GMAT-cross-checked
reference almost exactly (final position/velocity agree to the few
decimal places shown). It explicitly noted it had not run a numerical
integrator to confirm.

**Full workflow** (`case_c_workflow_result.json`): `select_model` returned
`bounded two-body fallback`, with `locality: "violated"` and
`other_physics: "violated"` explicitly recorded against the CW contract
(the 1,000 km / ~14.8% separation ratio and genuinely large relative
velocity make this not local CW-proximity motion), and
`deterministic_tool: "src.twobody.propagate_cartesian_state"` named
explicitly. A real GMAT run of the same point-mass dynamics reached
`comparison.status="PASS"` (`position_error_m≈0.00218`,
`velocity_error_mps≈5.25e-6`), `verified=True`, with a validated SVG
trajectory screenshot.

**Finding:** this is the case where the baseline's informal pattern-
matching ("this looks like circular two-body motion, not CW") happened to
reach the same practical outcome as the workflow's explicit model
selection — but by inference, not by a structured, auditable record of
*which specific CW assumption failed and why*. The baseline response never
produces anything resembling a `locality: violated` / `other_physics:
violated` record; a different, less textbook-obvious geometry could easily
have led a baseline LLM to apply CW inappropriately where this one didn't.
The structured workflow's `model_selection` block is the kind of
machine-checkable, assumption-by-assumption record that generalizes beyond
this one clean case, which the baseline's correct-but-informal guess does
not provide.

### Case (d) — ambiguous / incomplete

**Request:** "The chaser is 200 meters behind the target. Find a one-orbit
rendezvous." — missing central body/mu, reference orbit, LVLH axis/sign
convention, initial relative velocity, terminal conditions, and maneuver
assumptions.

**Direct-LLM baseline** (`case_d_baseline_llm_response.md`): never asked a
single clarification question. In one pass, it: (1) invented a 400 km
reference altitude never stated anywhere in the request; (2) picked a
specific LVLH sign convention for "behind" (-y) without flagging that
"behind" is actually ambiguous without a declared convention; (3) invented
a complete initial relative velocity ([0,0,0] m/s) that was never given at
all; (4) invented a zero-relative-velocity rendezvous terminal condition;
and (5) assumed impulsive two-burn maneuvering. It did, as a secondary
observation, correctly notice that CW targeting is exactly singular at one
full orbital period and recommended nudging the transfer time — but only
*after* already delivering a confident numerical-feeling answer built on
five unauthorized assumptions.

**Full workflow** (`case_d_workflow_result.json`): with `readiness=
"NEEDS_CLARIFICATION"`, `run_rendezvous_workflow` returned immediately —
`outcome="NEEDS_CLARIFICATION"`, `verified=False`,
`model_selection=None`, `artifacts={}` — with **zero** model selection,
solver, or GMAT calls attempted, and the exact five clarification
questions from the fixture (central body/mu, reference orbit, LVLH
axis/sign convention for "behind," complete initial relative state,
terminal conditions/maneuver assumptions/outputs) returned verbatim in
`clarification_questions`, matching `src/workflow.py::_clarification_result`'s
documented short-circuit behavior exactly.

**Finding — the single clearest error type prevented across all four
cases:** the direct-LLM baseline **silently invented five separate
unauthorized assumptions** (reference altitude, axis/sign convention,
initial relative velocity, terminal condition, maneuver count) to produce
a confident-sounding numerical answer to an underspecified request, with
no indication to a reader which of those were genuine inputs versus
guesses. The structured workflow's formalizer-level readiness check
prevents this exact failure mode by construction: it never reaches model
selection, the CW solver, or GMAT at all until the readiness state is
`READY_TO_SOLVE`, so there is no path by which an ambiguous request can
produce a numerical answer without first being resolved.

## 3. Scoring (AC2)

Legend: **PASS** = behavior matches the fixture's documented expectation
cleanly; **PARTIAL** = behavior is directionally present but incomplete,
informal, or undisclosed as such; **FAIL** = behavior absent or
contradicts the expectation; **N/A** = dimension does not apply to this
case/approach combination.

| Dimension | Approach | (a) straightforward | (b) boundary | (c) two-body | (d) ambiguous |
| --- | --- | --- | --- | --- | --- |
| Structured formulation (explicit facts/assumptions record) | Direct-LLM baseline | PARTIAL (correct informally, no structured record) | PARTIAL | PARTIAL | FAIL (assumptions invented, not recorded) |
| | Full workflow | PASS | PASS | PASS | PASS (`readiness`/`clarification_questions` recorded) |
| Ambiguity detection | Direct-LLM baseline | N/A (unambiguous case) | N/A | N/A | FAIL (no clarification requested) |
| | Full workflow | N/A | N/A | N/A | PASS (exact 5 questions, no numbers produced) |
| Model selection (CW vs. two-body vs. none) | Direct-LLM baseline | PASS (correct, informal) | PARTIAL (correct selection, missed boundary signal) | PASS (correct, informal) | FAIL (selected a model implicitly instead of deferring) |
| | Full workflow | PASS (unqualified) | PASS (explicitly qualified) | PASS (violated assumptions named) | PASS (`NEEDS MORE INFORMATION`, no tool) |
| Numerical agreement vs. reference | Direct-LLM baseline | PASS (~5-6 sig figs) | PASS (close, but unqualified) | PASS (close) | N/A (no reference exists for this case) |
| | Full workflow | PASS (GMAT PASS, error ≈0.0079 m / 1.17e-5 m/s) | PASS (GMAT PASS, error ≈0.0465 m / 3.07e-5 m/s) | PASS (GMAT PASS, error ≈0.0022 m / 5.25e-6 m/s) | N/A |
| GMAT invocation | Direct-LLM baseline | FAIL (none; disclosed as not done) | FAIL (none; disclosed as not done) | FAIL (none; disclosed as not done) | N/A |
| | Full workflow | PASS (real `GmatConsole-R2026a` run, banner captured) | PASS | PASS | N/A (correctly never attempted) |
| Discrepancy / boundary-condition handling | Direct-LLM baseline | N/A (no discrepancy) | FAIL (singular-reachable targeting entirely missed) | N/A | N/A |
| | Full workflow | N/A | PASS (`qualified=True`, concerns named) | N/A | N/A |
| Screenshot / visual-artifact availability | Direct-LLM baseline | FAIL (none produced) | FAIL (none produced) | FAIL (none produced) | N/A |
| | Full workflow | PASS (valid SVG, `screenshot.ok=True`) | PASS | PASS | N/A (correctly never attempted) |
| Explanation quality (states what it did/did not verify; no overclaiming) | Direct-LLM baseline | PASS (honest "not verified" disclaimer) | PARTIAL (honest disclaimer present, but no boundary-specific warning) | PASS (honest disclaimer) | FAIL (confident tone over invented assumptions) |
| | Full workflow | PASS (`trust_statement` distinguishes solver success from GMAT verification) | PASS (`trust_statement` + explicit qualified concerns) | PASS | PASS (explicit "no physics attempted" statement) |

## 4. Aggregate summary across all four categories (AC4)

- **Numerical correctness alone is not where the baseline struggles.** In
  three of four cases (a, b, c), the direct-LLM baseline's hand-derived
  numbers were close to or in agreement with the GMAT-verified reference,
  because a careful single-shot application of standard CW/two-body
  formulas on a well-posed problem is genuinely tractable by hand. The
  baseline's weaknesses are **not** primarily computational.
- **The baseline never independently verifies its own numbers.** Across
  all three solvable cases, the baseline explicitly disclosed "I have not
  verified this against a numerical propagator" — an honest disclaimer,
  but one with no actual mechanism behind it (no GMAT run, no screenshot,
  no independent integrator). The full workflow backs every solvable case
  with a real, independently executed GMAT run and a validated trajectory
  artifact in every one of the three solvable cases.
- **The baseline misses a documented boundary condition the architecture
  is specifically built to surface.** Case (b) is the clearest instance:
  the baseline solved only the sub-block that happened to be well-
  conditioned and never noticed the targeting singularity the full
  workflow's `model_selector`/`cw.two_burn_targeting` combination exists
  to detect.
- **The baseline's most consequential failure is formulation, not
  computation.** Case (d) shows the baseline silently inventing five
  separate unauthorized assumptions to force a numeric answer out of an
  underspecified request, with no visible seam between "stated input" and
  "guess." The full workflow's readiness short-circuit prevents this
  failure mode by construction, not by catching it after the fact.
- **The full workflow's advantage is concentrated in evidentiary structure
  and boundary handling, not raw arithmetic.** Its wins are: a
  machine-checkable, named assumption record for every case; a genuine,
  reproducible independent numerical cross-check (GMAT) with recorded
  tolerances and error values instead of an unsubstantiated disclaimer; an
  explicit boundary/qualification mechanism that the baseline has no
  analogue for; a required visual artifact in every solvable case; and a
  hard stop before any numeric answer when the request is ambiguous.

## 5. Conclusions — specific prevented/detected error types and limitations (AC5)

**Error types the structured workflow prevented or detected in these four
cases, specifically:**

1. **Formulation error (case d):** silently inventing missing problem
   inputs (reference orbit, axis convention, initial relative velocity,
   terminal condition, maneuver count) to produce a numeric answer to an
   underspecified request. Prevented by construction via the formalizer-
   level `NEEDS_CLARIFICATION` short-circuit, which never reaches model
   selection or any solver.
2. **Verification/discrepancy-handling gap (case b):** failing to notice
   or disclose a documented CW targeting-conditioning boundary (singular-
   but-reachable Φrv at an exact half-orbital-period transfer). Detected
   by `src/model_selector.py`'s explicit `targeting_conditioning` signal,
   which surfaces a `qualified=True` result with named concerns rather
   than an unqualified pass.
3. **Unsubstantiated-verification claim (cases a, b, c):** reporting a
   numeric result with only an informal "I have not checked this" caveat,
   rather than an actual independent numerical cross-check. Addressed by
   requiring every solvable outcome to carry a real GMAT comparison
   (position/velocity error against stated tolerances) and a validated
   trajectory screenshot artifact before any `VERIFIED` status is
   reported.
4. **Informal, non-auditable model selection (case c):** reaching the
   correct CW-vs-two-body routing decision by general pattern recognition
   rather than an explicit, named assumption-by-assumption record
   (`circularity`/`locality`/`duration_regime`/`frame`/`other_physics`/
   `maneuver_assumptions`). The structured workflow's `model_selection`
   block makes this reasoning inspectable and reproducible, which matters
   even when (as in this one case) the baseline's informal guess happened
   to be correct.

**What this benchmark does *not* show, and limitations of this
evaluation:**

- This is a **four-case** benchmark covering one narrow rendezvous class
  (circular-reference-orbit, impulsive, two-spacecraft LVLH proximity
  rendezvous, plus one bounded point-mass two-body coast fallback). It
  says nothing about eccentric reference orbits, continuous-thrust
  maneuvers, multi-burn phasing, perturbed dynamics, cislunar/CR3BP
  regimes, or any astrodynamics problem outside this explicitly scoped
  class — all of which are explicit non-goals of this project
  (`reference/SOURCE.md`, `backlog/docs/specifications/semester-scope/`).
- The direct-LLM baseline's numerical correctness on cases (a)/(b)/(c)
  should not be read as evidence that LLMs are generally reliable at
  astrodynamics computation; it reflects that these three cases are
  textbook-standard applications of a well-known linear/Keplerian
  formula, which this particular model/session happened to apply
  correctly. A different problem instance, a different model, or a
  slightly less standard geometry could easily produce a materially wrong
  baseline answer with the same confident tone — case (d) already shows
  this model inventing unauthorized assumptions on a request that departs
  even slightly from a fully-specified textbook setup.
- Because the baseline-answer author and the task-executing agent are the
  same underlying model in the same session, this comparison measures the
  effect of **scaffolding/architecture**, not a cross-model capability
  comparison. A materially different (e.g. smaller or less capable) LLM
  used as a baseline might perform worse than reported here; a more
  careful human-reviewed LLM baseline might perform better. This
  comparison does not generalize across models.
- Both GMAT comparisons and the baseline's hand arithmetic use the same
  underlying `src/cw.py`/`src/twobody.py` physics equations as their
  common point of reference (the fixtures' `reference_numerical_result`
  are themselves derived from, and cross-checked against, this project's
  own already-audited solvers); this benchmark is not an independent
  third-party ground truth for CW/two-body dynamics in general, though
  the GMAT cross-check specifically is an independent numerical
  integrator, not a repetition of the same analytic formula.
- No broad claim of "the structured workflow is superior to LLMs for
  astrodynamics" is made or supported by this evaluation. The specific,
  narrow claim supported by the evidence above is: for this four-case
  benchmark, within this explicitly scoped rendezvous class, the
  structured workflow prevents or detects specific, named formulation,
  verification, and boundary-condition-handling errors that this
  particular direct-LLM baseline exhibited, while adding a reproducible
  evidentiary record (GMAT comparisons, screenshots, assumption ledgers)
  the baseline has no mechanism to produce.
