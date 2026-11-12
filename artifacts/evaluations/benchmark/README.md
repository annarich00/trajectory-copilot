# `evaluations/benchmark/` — four-category rendezvous benchmark (TJC-1.9)

A small, reviewable benchmark covering exactly the four required categories
for the scoped semester experiment: straightforward CW, boundary,
CW-invalid/two-body, and ambiguous/incomplete. It does not expand into
broad astrodynamics coverage.

| File | Category | Expected selection | Solvable |
| --- | --- | --- | --- |
| `case_a_straightforward_cw.json` | straightforward CW | `CW rendezvous` (unqualified) | yes |
| `case_b_boundary_cw.json` | boundary | `CW rendezvous` (**qualified**) | yes |
| `case_c_two_body.json` | CW-invalid / two-body | `bounded two-body fallback` | yes |
| `case_d_ambiguous.txt` | ambiguous / incomplete | `NEEDS MORE INFORMATION` (no model) | no |

Each JSON fixture records, per the formalizer schema
(`.pi/skills/orbital-problem-formalizer/SKILL.md`) and model-selector
contract (`.pi/skills/orbital-model-selector/SKILL.md`, `src/model_selector.py`):

- `request` — the natural-language or structured input;
- `expected_structured_problem` — the expected formalizer output, with the
  skill's exact provenance labels;
- `expected_model` — the expected `src/model_selector.py::select_model`
  outcome (`selection`, `qualified`, `assumptions_assessed`, `concerns`);
- `reference_numerical_result` — a real, GMAT-cross-checked numerical result
  (cases a/b/c) *or* `expected_clarification_questions` (case d, in its own
  text-block format matching `evaluations/formalizer/`'s precedent);
- `gmat_tolerance` — the position/velocity (and, for CW cases, delta-v)
  tolerances used;
- `expected_explanation_behavior` — what the human-readable output must and
  must not state;
- `schema_version` / `case_version` / `provenance` — explicit versioning and
  provenance (AC5), alongside explicit units/frames/assumptions throughout
  each fixture's own fields.

JSON (not YAML) is used for cases a/b/c because they carry structured
numerical fixture data and this repository deliberately avoids adding an
undeclared PyYAML dependency (see `scripts/run_cw_gmat_slice.py`'s own
`load_simple_yaml` docstring); `verification_result.json` already
establishes this JSON convention for structured numerical GMAT evidence.
Case d uses the existing `evaluations/formalizer/`-style text-block format,
since it is a pure clarification-question case with no numerical fixture
data, matching that directory's closest existing precedent exactly
(including reusing `test_01_underspecified.txt`'s own request text, so this
benchmark never maintains a second, drifting restatement of an
already-audited fixture).

## Reproducible GMAT evidence (AC3)

- Case (a) reuses the already-committed, already-verified
  `examples/cw_gmat_vertical_slice.yaml` / `examples/cw_gmat_slice_example/`
  (produced by the existing `scripts/run_cw_gmat_slice.py` pipeline).
- Cases (b) and (c) are produced by
  `scripts/generate_benchmark_gmat_evidence.py`, a thin benchmark-specific
  caller of the already-audited `src/cw.py`, `src/twobody.py`, and
  `src/gmat_verify.py` modules (none of those modules are modified):
  `examples/benchmark_case_b_boundary/` and
  `examples/benchmark_case_c_two_body/` each contain a generated GMAT
  script, a `verification_result.json`, and a required SVG trajectory
  screenshot artifact.

Reproduce all three with:

```
.venv/bin/python scripts/run_cw_gmat_slice.py --gmat GmatConsole-R2026a
.venv/bin/python scripts/generate_benchmark_gmat_evidence.py --gmat GmatConsole-R2026a
```

## Boundary case and AC4

`case_b_boundary_cw.json` exercises `src/model_selector.py`'s documented
targeting-conditioning signal (a singular-but-reachable `Phi_rv` at an exact
half-orbital-period transfer time) to produce a `qualified=True` CW decision
with surfaced concerns — not a flat pass/fail, and not a newly invented
universal numeric validity threshold. The separation ratio and duration for
this case are each comfortably inside `validate_cw_use()`'s existing
heuristics; the only borderline signal is targeting conditioning at this
specific transfer time, exactly as `.pi/skills/orbital-model-selector/SKILL.md`
and `reference/SOURCE.md` §D already document.

## Schema validation (AC5)

`tests/test_benchmark_fixtures.py` loads every fixture in this directory and
asserts the required fields above are present with correct types, that
exactly one case exists per required category, and that each fixture
declares an explicit `schema_version`/`case_version`.
