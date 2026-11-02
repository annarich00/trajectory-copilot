# uv adoption decision for the core project

## Decision

**Keep plain `venv`/`pip` for the core Trajectory CoPilot project (option b).**
`requirements-dev.txt`, the `python3 -m venv .venv` setup, and the documented
`.venv/bin/python -m pytest -q` reproduction commands in `README.md` and
`docs/baseline-provenance.md` are unchanged by this decision.

`uv` is not adopted as the core dependency-management tool at this time. This
is an explicit decision, not an oversight: the inconsistency between the core
project's plain pip/venv tooling and the isolated Poliastro verification
environment's `uv` usage (see "Relationship to the Poliastro environment"
below) has been considered and is intentional.

## Evidence consulted

- `uv` is installed and available in this sandbox (`uv 0.12.18`), so adoption
  is not blocked by tooling availability.
- The core project's current `.venv` (shared across worktrees at
  `/home/anna_ford/projects/class_example_traj_copilot/.venv`) was created with
  plain `venv`, not `uv`: its `pyvenv.cfg` records
  `command = /usr/bin/python3 -m venv /home/anna_ford/projects/class_example_traj_copilot/.venv`
  and has no `uv = <version>` field (which `uv venv` normally adds). This
  confirms the project's actual current state is plain pip/venv, not a
  partial or accidental uv migration.
- `requirements-dev.txt` is a small, flat, unpinned-by-hashes dependency list
  (`numpy`, `pytest`, `mss`, `python-xlib`) with no reported resolver
  conflicts, slow installs, or other documented pain points anywhere in this
  repository's docs, Backlog tasks, or `README.md`.
- The full existing test suite already passes under the current plain
  pip/venv setup (see `docs/baseline-provenance.md`), and the documented
  clean-checkout commands in `README.md` already work end-to-end.
- The only place `uv` is currently used in this repo
  (`docs/poliastro-verification-architecture.md`) is for a reason specific to
  that environment, not a general tooling preference: it provisions an
  **isolated Python 3.10 interpreter** (via `uv venv --python 3.10
  .poliastro-venv`) to run the archived, legacy-pinned Poliastro 0.17.0
  release, which requires a Python version incompatible with the core
  project's newer runtime. `uv`'s value there is fast, reproducible
  *interpreter* provisioning for a throwaway verifier environment, not
  dependency-management style for the main codebase.
- A sibling project (the Figure 4 reproduction, referenced in the Backlog task
  description) uses `uv` + `pyproject.toml` + `uv.lock` as its convention, but
  that is a different, separately maintained project with no documented
  shared tooling requirement with this repo.

## Reasoning

No concrete pain point with the current pip/venv setup exists in this repo:
no slow installs, no resolver conflicts, no broken reproduction commands, and
no stated operator preference for `uv` in the core project specifically. The
only in-repo precedent for `uv` (the Poliastro verifier) uses it to solve a
narrow problem — pinning a legacy Python interpreter for an archived,
EOL-dependency environment — that does not apply to the core project, which
targets a current Python runtime with a small, already-working dependency
set.

Converting `requirements-dev.txt` to `pyproject.toml` + `uv.lock` this late in
the semester would touch every documented reproduction command in `README.md`
and `docs/baseline-provenance.md`, require re-verifying the full test suite
under a new environment, and risk destabilizing already-passing,
already-documented setup instructions — all to fix a tooling-convention
inconsistency rather than a correctness defect. That cost is not justified by
any functional or operational benefit identified in this repo.

Per TJC-7's explicit guidance to lean toward the option that minimizes
risk/churn to the already-passing test suite and already-documented
reproduction commands unless there is concrete evidence that switching is
clearly better, and because no such evidence was found, option (b) is chosen.

## Relationship to the Poliastro environment

`docs/poliastro-verification-architecture.md`'s use of `uv` for the isolated
Poliastro verification environment is **unaffected by this decision** and
remains exactly as documented there (`uv venv --python 3.10
.poliastro-venv`, `uv pip install ...`). That usage is deliberate and
orthogonal to this decision: it exists to provision a legacy Python 3.10
interpreter for an archived, EOL dependency stack that must stay isolated
from the core `.venv`, not because the project has adopted `uv` as its
general dependency-management convention. The core project and the Poliastro
verifier are intentionally decoupled in their tooling for this reason — `uv`
exists in exactly one place in this repo, and this document records why that
split is deliberate rather than accidental.

## Revisiting this decision

If the core project's dependency set grows substantially, needs reproducible
hash-pinned locking, or a concrete operational pain point with pip/venv
emerges, this decision should be revisited. As of this writing (TJC-7), no
such pain point exists.
