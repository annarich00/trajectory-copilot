# GMAT example corpus (TJC-11)

Schema version: 1.0.0 (see [`SCHEMA.md`](SCHEMA.md))

`corpus.json` is the structured, validated index of the open-source GMAT
mission scripts collected in TJC-10 (`research/gmat_examples_log.md`,
`research/gmat_examples_raw/`). It is the file the GMAT-example reviewer
subagent (TJC-14, `.pi/agents/gmat-example-reviewer.md`) should reference:

    research/gmat_example_corpus/corpus.json

## Contents

- 18 entries covering all TJC-10 scripts.
- 12 `nasa/GMAT` official samples (Apache-2.0): `redistributable: true`,
  `content_path` points at the script text. Cite with the entry's
  `license.attribution`.
- 6 entries from sources with no discoverable license (TridibeshChattoraj,
  hannxmarie, iamxanadu): `redistributable: false`, `content_path: null`,
  metadata only. They must not be quoted or redistributed.

## Validate

    .venv/bin/python -m pytest tests/test_gmat_example_corpus.py -q
    .venv/bin/python scripts/build_gmat_example_corpus.py --check

The tests fail on a missing required field, a license-flagged entry marked
redistributable, a non-redistributable entry exposing `content_path`, a hash
mismatch, vocabulary violations, duplicate ids, any TJC-10 script missing from
the corpus, or a stale `corpus.json`.

## Regenerate / update after refreshing TJC-10's collection

1. Refresh the scripts under `research/gmat_examples_raw/` and update
   `research/gmat_examples_log.md` (URL, license line, commit) as in TJC-10.
2. Edit the metadata tables in `scripts/build_gmat_example_corpus.py`:
   `SOURCES` (repo, commit, URL prefix, license, redistributable) for a new or
   re-licensed source, and `SCRIPTS` (mission type, description) for each new
   script. A source may only be `redistributable: True` with a confirmed
   `clear` license in the TJC-10 log; otherwise use `_unknown_license`.
   Convention tags and SHA-256 hashes are computed automatically.
3. Regenerate: `.venv/bin/python scripts/build_gmat_example_corpus.py`
4. Rerun the validation commands above. If you changed the schema, bump
   `SCHEMA_VERSION` in `src/gmat_example_corpus.py` and the version in
   `SCHEMA.md` and this README.
