# Trajectory CoPilot — local educational site

Run from the repository root:

```sh
./run_site.sh
```

Open `http://127.0.0.1:4173`. The site is static and dependency-free: Node built-ins only, no npm install, build step, CDN, external font/asset, or runtime internet request.

## Scope and truthfulness

This is the living progress/demo surface for the approved semester flow:

> natural-language rendezvous request → structured problem → assumption-based CW applicability → deterministic CW or bounded two-body fallback → GMAT numerical comparison plus returned trajectory screenshot → explanation

The complete flow and GMAT integration do **not** work yet. Pages distinguish implemented primitives from planned tasks. Optimization/Pareto fronts, learned validity boundaries, broad sweeps, CR3BP/cislunar dynamics, and general mission planning are deferred/excluded.

## Authority boundaries

- Authoritative implementation: repository Python under `src/`.
- Authoritative tests: `.venv/bin/python -m pytest -q tests` from the repository root.
- Authoritative controlled text: repository `reference/`, skills, examples, evaluations, and baseline document.
- `site/data/` contains verbatim display mirrors. Never edit these copies for presentation.
- `site/js/physics.js` is a **non-authoritative pedagogical browser mirror**. It is deliberately absent from the sync mapping and cannot verify Python.
- Site prose/derivations teach the current implementation but are not independent physics audits. TJC-1.2–1.6 own those audits and corrections.

## Synchronize authoritative display mirrors

The Python-built-in-only command has an explicit source-to-mirror mapping in `tools/sync_site_data.py`:

```sh
python3 tools/sync_site_data.py          # refresh mirrors
python3 tools/sync_site_data.py --check  # non-mutating; exits 1 on drift
```

Add an explicit mapping when a later task exposes another authoritative file. Do not map generated artifacts or `site/js/physics.js`.

## Task completion / site maintenance checklist

Before an in-scope task is marked Done:

1. Update `site/data/project-progress.js` with truthful status, date, final commit subject, outcome, limitations, and links to code/docs/site/evidence.
2. Update every affected route; avoid claiming planned GMAT or integration work operates.
3. Refresh mirrors with `python3 tools/sync_site_data.py`, then require `--check` to pass.
4. If Python physics changed, separately review/update the pedagogical JS hand port and preserve its non-authoritative labels.
5. Run repository tests and `python3 tools/compare_upstream.py --check`.
6. Launch `./run_site.sh`; smoke-check every changed route and representative CSS, JS, and data artifact locally without internet access.
7. Run JS syntax checks, offline URL scan, `git diff --check`, generated/process-artifact scan, and secret scan.
8. Record objective evidence in Backlog, verify every AC/DoD, and use one atomic task commit.

## Structure

- `site/index.html`: SPA shell and navigation
- `site/js/app.js`: hash router
- `site/js/lib.js`: shared rendering and teaching-contract helpers
- `site/js/pages/`: route modules
- `site/data/project-progress.js`: manually maintained static progress model
- `site/data/`: synchronized verbatim authoritative mirrors
- `site/server.js`: minimal built-in Node static server
