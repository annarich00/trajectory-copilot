"""Schema and validator for the GMAT example corpus (TJC-11).

The corpus file (``research/gmat_example_corpus/corpus.json``) is the stable,
versioned contract the GMAT-example reviewer subagent (TJC-14) loads at
runtime. ``validate_corpus`` is the single enforcement point for that
contract; ``research/gmat_example_corpus/SCHEMA.md`` is its prose description
and must stay in sync with the constants below.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"
CORPUS_RELATIVE_PATH = "research/gmat_example_corpus/corpus.json"

TOP_LEVEL_REQUIRED_FIELDS = ("schema_version", "entries")

ENTRY_REQUIRED_FIELDS = (
    "id",
    "source_url",
    "source_repo",
    "source_commit",
    "license",
    "redistributable",
    "mission_type",
    "convention_tags",
    "description",
    "raw_source_path",
    "content_path",
    "content_sha256",
)

LICENSE_REQUIRED_FIELDS = ("status", "spdx_id", "attribution", "evidence")

# "clear" = confirmed license compatible with redistribution (see
# CLEAR_SPDX_IDS); "unknown" = TJC-10 found no license; "incompatible" =
# a license was found that does not permit redistribution.
LICENSE_STATUSES = ("clear", "unknown", "incompatible")
CLEAR_SPDX_IDS = ("Apache-2.0",)

MISSION_TYPES = (
    "orbit_transfer",
    "lunar_transfer",
    "lunar_impactor",
    "lunar_swingby",
    "finite_burn_propulsion",
    "electric_propulsion",
    "attitude_pointing",
    "mars_orbit_constellation",
    "station_keeping",
    "leo_propagation",
    "elliptical_orbit_propagation",
    "sso_inclination_study",
    "ground_station_contact",
    "interplanetary_transfer",
    "outer_planet_moon_exploration",
)

CONVENTION_TAGS = (
    "percent_comment_section_banners",
    "create_objects_before_begin_mission_sequence",
    "gmat_prefixed_property_assignment",
    "burn_vnb_axes",
    "target_vary_achieve_differential_corrector",
    "finite_burn_begin_end",
    "propagate_with_stop_condition",
    "custom_coordinate_systems",
    "xyplot_output",
    "orbitview_output",
    "groundtrackplot_output",
    "reportfile_output",
    "conditional_or_loop_logic",
)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_corpus(corpus: Any, root: Path) -> list[str]:
    """Return a list of human-readable schema violations (empty if valid).

    ``root`` is the repository root against which ``raw_source_path`` and
    ``content_path`` are resolved.
    """
    errors: list[str] = []
    if not isinstance(corpus, dict):
        return ["corpus must be a JSON object"]
    for field in TOP_LEVEL_REQUIRED_FIELDS:
        if field not in corpus:
            errors.append(f"corpus missing required field {field!r}")
    if corpus.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        errors.append(
            f"schema_version {corpus.get('schema_version')!r} != {SCHEMA_VERSION!r}"
        )
    entries = corpus.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("entries must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        label = f"{label} ({entry.get('id', '?')})"
        for field in ENTRY_REQUIRED_FIELDS:
            if field not in entry:
                errors.append(f"{label} missing required field {field!r}")
        entry_id = entry.get("id")
        if entry_id in seen_ids:
            errors.append(f"{label} duplicate id {entry_id!r}")
        seen_ids.add(entry_id)
        errors.extend(_validate_entry(label, entry, root))
    return errors


def _validate_entry(label: str, entry: dict, root: Path) -> list[str]:
    errors: list[str] = []
    for field in ("id", "source_url", "source_repo", "source_commit", "description"):
        if field in entry and not (isinstance(entry[field], str) and entry[field].strip()):
            errors.append(f"{label} field {field!r} must be a non-empty string")

    if "mission_type" in entry and entry["mission_type"] not in MISSION_TYPES:
        errors.append(f"{label} mission_type {entry['mission_type']!r} not in vocabulary")

    tags = entry.get("convention_tags")
    if "convention_tags" in entry:
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            errors.append(f"{label} convention_tags must be a list of strings")
        else:
            unknown = [t for t in tags if t not in CONVENTION_TAGS]
            if unknown:
                errors.append(f"{label} convention_tags not in vocabulary: {unknown}")

    license_info = entry.get("license")
    license_status = None
    spdx_id = None
    if "license" in entry:
        if not isinstance(license_info, dict):
            errors.append(f"{label} license must be an object")
        else:
            for field in LICENSE_REQUIRED_FIELDS:
                if field not in license_info:
                    errors.append(f"{label} license missing required field {field!r}")
            license_status = license_info.get("status")
            spdx_id = license_info.get("spdx_id")
            if "status" in license_info and license_status not in LICENSE_STATUSES:
                errors.append(f"{label} license.status {license_status!r} not in {LICENSE_STATUSES}")

    redistributable = entry.get("redistributable")
    if "redistributable" in entry:
        if not isinstance(redistributable, bool):
            errors.append(f"{label} redistributable must be a boolean")
        elif redistributable and not (
            license_status == "clear" and spdx_id in CLEAR_SPDX_IDS
        ):
            errors.append(
                f"{label} marked redistributable but license is not clear "
                f"(status={license_status!r}, spdx_id={spdx_id!r})"
            )

    errors.extend(_validate_paths(label, entry, root, redistributable is True))
    return errors


def _validate_paths(label: str, entry: dict, root: Path, redistributable: bool) -> list[str]:
    errors: list[str] = []
    raw = entry.get("raw_source_path")
    if "raw_source_path" in entry:
        if not isinstance(raw, str) or not (root / raw).is_file():
            errors.append(f"{label} raw_source_path {raw!r} is not an existing file")
        elif "content_sha256" in entry and sha256_of(root / raw) != entry["content_sha256"]:
            errors.append(f"{label} content_sha256 does not match raw_source_path file (sha256 mismatch)")

    if "content_path" in entry:
        content_path = entry["content_path"]
        if redistributable:
            if not isinstance(content_path, str) or not (root / content_path).is_file():
                errors.append(f"{label} redistributable entry needs an existing content_path, got {content_path!r}")
            elif content_path != raw:
                errors.append(f"{label} content_path must equal raw_source_path")
        elif content_path is not None:
            errors.append(
                f"{label} non-redistributable entry must have content_path null, got {content_path!r}"
            )
    return errors
