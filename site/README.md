# Trajectory CoPilot — Interactive Physics & Verification Lab

A local, dependency-free educational website for this repository. Run it with:

```
./run_site.sh
```

then open `http://127.0.0.1:4173` in a browser. No internet access, no npm
install, no external services — just the Node.js runtime already present in
this environment serving static files from this `site/` directory.

## What this is

An interactive walkthrough of the actual `trajectory-copilot` source code,
tests, skills, and reference material — connecting natural-language operator
requests to problem formalization, model selection, deterministic physics
(`src/cw.py`, `src/twobody.py`), independent verification (`src/verify.py`),
and the tests that establish correctness (`tests/`).

## Source of truth

- **Authoritative physics implementation:** the Python in `src/cw.py`,
  `src/twobody.py`, `src/verify.py`, `src/optimization.py` (copied verbatim
  into `site/data/src/` for display — never edited for presentation).
- **Authoritative test results:** running `pytest tests/` in the repository
  root. This website cannot execute Python/pytest; it is a static browser
  page.
- **Pedagogical browser mirror:** `site/js/physics.js` is a hand-ported
  JavaScript copy of specific Python functions, used ONLY to drive
  interactive sliders/tables in the browser. It is explicitly labeled
  throughout the site ("PEDAGOGICAL BROWSER MIRROR") and is never presented
  as verifying, confirming, or substituting for the Python implementation or
  its test suite. If the Python changes, this mirror must be updated by hand
  — there is no shared code path, so treat any disagreement as a bug in the
  mirror, not in the Python.

## Structure

- `site/index.html` — single-page app shell + sidebar nav
- `site/js/app.js` — tiny hash router
- `site/js/lib.js` — shared rendering helpers (badges, code blocks, mirror/
  authority banners)
- `site/js/physics.js` — the pedagogical browser mirror described above
- `site/js/pages/*.js` — one module per page, each registering itself on
  `window.TCPages[routeName]`
- `site/data/` — verbatim copies of repository source/tests/reference/
  skills/examples/evaluations, fetched at runtime for display
- `site/server.js` — minimal static file server (no dependencies)
