# GMAT example corpus schema — version 1.0.0

Machine-readable contract for `research/gmat_example_corpus/corpus.json`, the
file the GMAT-example reviewer subagent (TJC-14) loads at runtime. The
authoritative enforcement is `src/gmat_example_corpus.py::validate_corpus`
(constants `SCHEMA_VERSION`, `ENTRY_REQUIRED_FIELDS`, `MISSION_TYPES`,
`CONVENTION_TAGS` there must match this document); it is exercised by
`tests/test_gmat_example_corpus.py`.

Bump `SCHEMA_VERSION` (and this heading and the README) on any change to
required fields, field meaning, or the controlled vocabularies.

## Top level

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | string | `"1.0.0"` |
| `entries` | array of entry | One per script collected in TJC-10 |

## Entry (all fields required)

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Unique, stable slug (`<source>-<script stem>`, lowercase) |
| `source_url` | string | Exact raw URL the script was fetched from (TJC-10 log) |
| `source_repo` | string | `owner/repo` on GitHub |
| `source_commit` | string | Commit SHA of the branch HEAD at TJC-10 fetch time |
| `license` | object | See below |
| `redistributable` | boolean | `true` only if `license.status == "clear"` **and** `license.spdx_id` is in `CLEAR_SPDX_IDS` (currently `Apache-2.0`). The validator fails any other `true`. |
| `mission_type` | string | One of the `MISSION_TYPES` vocabulary |
| `convention_tags` | array of string | Subset of the `CONVENTION_TAGS` vocabulary, auto-detected from the script text (formatting/structure conventions the script exhibits) |
| `description` | string | Short description of what the script demonstrates |
| `raw_source_path` | string | Repo-relative path to the TJC-10 raw copy; must exist (used for provenance and the hash) |
| `content_path` | string \| null | Repo-relative path to the script text the subagent may read and quote. **Equals `raw_source_path` when `redistributable` is true; `null` when false** (no script text is exposed for non-redistributable entries) |
| `content_sha256` | string | SHA-256 of the raw file; must match |

### `license` object (all fields required)

| Field | Type | Meaning |
|---|---|---|
| `status` | string | `clear` (confirmed redistributable license), `unknown` (TJC-10 found no license), or `incompatible` |
| `spdx_id` | string \| null | SPDX id when known, else `null` |
| `attribution` | string | Attribution/copyright line to carry when citing |
| `evidence` | string | Where the license determination came from |

## Non-redistributable entries

Entries from TJC-10 sources B, C and D (license unknown/unclear) are **kept as
metadata-only entries**: `redistributable: false`, `content_path: null`. The
subagent may use `mission_type`, `convention_tags`, `description` and
`source_url` (e.g. to cite or point a human at the original) but must not
quote or reproduce their script text. They are never presented as if clear.
The raw copies remain in `research/gmat_examples_raw/` from TJC-10 and are
referenced only by `raw_source_path` for provenance/hash checking.

## Controlled vocabularies

`mission_type`: `orbit_transfer`, `lunar_transfer`, `lunar_impactor`,
`lunar_swingby`, `finite_burn_propulsion`, `electric_propulsion`,
`attitude_pointing`, `mars_orbit_constellation`, `station_keeping`,
`leo_propagation`, `elliptical_orbit_propagation`, `sso_inclination_study`,
`ground_station_contact`, `interplanetary_transfer`,
`outer_planet_moon_exploration`.

`convention_tags` (regex detection rules live in
`scripts/build_gmat_example_corpus.py::TAG_PATTERNS`):
`percent_comment_section_banners`,
`create_objects_before_begin_mission_sequence`,
`gmat_prefixed_property_assignment`, `burn_vnb_axes`,
`target_vary_achieve_differential_corrector`, `finite_burn_begin_end`,
`propagate_with_stop_condition`, `custom_coordinate_systems`, `xyplot_output`,
`orbitview_output`, `groundtrackplot_output`, `reportfile_output`,
`conditional_or_loop_logic`.
