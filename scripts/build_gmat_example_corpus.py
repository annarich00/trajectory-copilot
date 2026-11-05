#!/usr/bin/env python3
"""Build ``research/gmat_example_corpus/corpus.json`` from TJC-10's collection.

Reads the raw scripts under ``research/gmat_examples_raw/`` plus the
hand-curated per-script metadata table below (URLs, license status, mission
type, description -- all taken from ``research/gmat_examples_log.md``),
auto-detects convention tags from each script's text, validates the result
with ``src/gmat_example_corpus.py::validate_corpus`` and writes the corpus.

Usage (from the repository root)::

    .venv/bin/python scripts/build_gmat_example_corpus.py          # rewrite corpus.json
    .venv/bin/python scripts/build_gmat_example_corpus.py --check  # fail if corpus.json is stale

See ``research/gmat_example_corpus/README.md`` for the full regeneration steps.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gmat_example_corpus import (  # noqa: E402
    CORPUS_RELATIVE_PATH,
    SCHEMA_VERSION,
    sha256_of,
    validate_corpus,
)

RAW_RELATIVE_DIR = "research/gmat_examples_raw"
RAW_URL_BASE = "https://raw.githubusercontent.com"

# Per-source facts from research/gmat_examples_log.md ("Source repositories used").
APACHE_LICENSE = {
    "status": "clear",
    "spdx_id": "Apache-2.0",
    "attribution": "Copyright (c) United States Government as represented by the Administrator of NASA (nasa/GMAT, Apache License 2.0)",
    "evidence": "nasa/GMAT License.txt; GET /repos/nasa/GMAT/license -> apache-2.0 (TJC-10 log, source A)",
}


def _unknown_license(repo: str, source_letter: str) -> dict:
    return {
        "status": "unknown",
        "spdx_id": None,
        "attribution": f"{repo} (no license; all rights presumed reserved by the author)",
        "evidence": f"No LICENSE file; GitHub API license: null (TJC-10 log, source {source_letter}). Metadata only; script text is not redistributable.",
    }


SOURCES = {
    "nasa_gmat_official_samples": {
        "repo": "nasa/GMAT",
        "commit": "c9b78bd1c8499845cb78fde315e1f761b6b06f1c",
        "url_prefix": f"{RAW_URL_BASE}/nasa/GMAT/main/application/samples/",
        "license": APACHE_LICENSE,
        "redistributable": True,
    },
    "other_sources/TridibeshChattoraj_GMAT_Mission_Portfolio": {
        "repo": "TridibeshChattoraj/GMAT_Mission_Portfolio",
        "commit": "29dbf52751115abe7dd03b90dbf275af75f13fc9",
        "url_prefix": f"{RAW_URL_BASE}/TridibeshChattoraj/GMAT_Mission_Portfolio/main/",
        "license": _unknown_license("TridibeshChattoraj/GMAT_Mission_Portfolio", "B"),
        "redistributable": False,
    },
    "other_sources/hannxmarie_impulsive_manoeuvres_interplanetary": {
        "repo": "hannxmarie/impulsive_manoeuvres_interplanetary",
        "commit": "b5e530c1c5873771e169a7e549adf55286c3dd7b",
        "url_prefix": f"{RAW_URL_BASE}/hannxmarie/impulsive_manoeuvres_interplanetary/main/",
        "license": _unknown_license("hannxmarie/impulsive_manoeuvres_interplanetary", "C"),
        "redistributable": False,
    },
    "other_sources/iamxanadu_GMAT-SaturnIcyMoonExplorer": {
        "repo": "iamxanadu/GMAT-SaturnIcyMoonExplorer",
        "commit": "c47aacb968a4b92aa1833338999c15c94c33d92b",
        "url_prefix": f"{RAW_URL_BASE}/iamxanadu/GMAT-SaturnIcyMoonExplorer/master/",
        "license": _unknown_license("iamxanadu/GMAT-SaturnIcyMoonExplorer", "D"),
        "redistributable": False,
    },
}

# (source dir, file name, URL path suffix override or None, mission_type, description)
SCRIPTS = (
    ("nasa_gmat_official_samples", "Ex_HohmannTransfer.script", None, "orbit_transfer",
     "Classic two-burn Hohmann transfer between circular orbits, targeting both impulsive burns with a differential corrector."),
    ("nasa_gmat_official_samples", "Tut_SimpleOrbitTransfer.script", None, "orbit_transfer",
     "GMAT Users Guide 'Simple Orbit Transfer' tutorial: introductory orbit-raising maneuver targeting."),
    ("nasa_gmat_official_samples", "Ex_LunarTransfer.script", None, "lunar_transfer",
     "Trans-lunar injection and transfer mission set up with targeting sequences."),
    ("nasa_gmat_official_samples", "Ex_GivenEpochGoToTheMoon.script", None, "lunar_transfer",
     "From a fixed separation epoch, target a trajectory that captures into lunar orbit."),
    ("nasa_gmat_official_samples", "Ex_LCROSSTrajectory.script", None, "lunar_impactor",
     "Reproduction of the LCROSS mission trajectory to lunar impact."),
    ("nasa_gmat_official_samples", "Ex_MMSSingleLunarSwingby.script", None, "lunar_swingby",
     "Single lunar swingby with multiple targeting sequences, modeled on the MMS mission family."),
    ("nasa_gmat_official_samples", "Ex_FiniteBurn.script", None, "finite_burn_propulsion",
     "Fuel tank and thruster setup used in a finite (non-impulsive) maneuver sequence."),
    ("nasa_gmat_official_samples", "Ex_ElectricPropulsion.script", None, "electric_propulsion",
     "Long-duration low-thrust burn using an electric thruster."),
    ("nasa_gmat_official_samples", "Ex_Attitude_NadirPointing.script", None, "attitude_pointing",
     "Attitude coordinate system defining a nadir-pointing attitude model."),
    ("nasa_gmat_official_samples", "Ex_Attitude_Spinner.script", None, "attitude_pointing",
     "Spinning (spinner) attitude model."),
    ("nasa_gmat_official_samples", "Ex_MarsOrbit.script", None, "mars_orbit_constellation",
     "Propagation of a constellation of satellites in orbit around Mars."),
    ("nasa_gmat_official_samples", "Ex_LEOStationKeeping.script", None, "station_keeping",
     "Altitude-box stationkeeping maneuver sequence for a LEO spacecraft."),
    ("other_sources/TridibeshChattoraj_GMAT_Mission_Portfolio", "Leo_V1_orbit_Visualisation_ISS.script", None, "leo_propagation",
     "LEO orbit propagation and visualization using ISS-like orbital parameters."),
    ("other_sources/TridibeshChattoraj_GMAT_Mission_Portfolio", "ESOC_ground_Contact_one_satellite.script",
     "ESOC%20Ground%20Station%20Coverage/ESOC%20ground%20Contact%20one%20satellite.script", "ground_station_contact",
     "Ground-station contact/coverage analysis for one satellite against an ESOC (Darmstadt) station."),
    ("other_sources/TridibeshChattoraj_GMAT_Mission_Portfolio", "Elliptical_Orbit.script",
     "Elliptical%20Orbit%20%2B%20SSO%20Analysis/Elliptical%20Orbit.script", "elliptical_orbit_propagation",
     "Keplerian-dynamics propagation of an elliptical orbit."),
    ("other_sources/TridibeshChattoraj_GMAT_Mission_Portfolio", "Inclination_098_SSO.script",
     "Inclination%20Study/Inclination_098_SSO.script", "sso_inclination_study",
     "Propagation of a ~98 degree inclination Sun-synchronous orbit as part of an inclination study."),
    ("other_sources/hannxmarie_impulsive_manoeuvres_interplanetary", "impulsive_trajectory_w001.script", None, "interplanetary_transfer",
     "Earth-to-Mars transfer for a 'Human Mars Lander' using impulsive maneuvers and B-plane (BdotT/BdotR) targeting in VNB-frame burns."),
    ("other_sources/iamxanadu_GMAT-SaturnIcyMoonExplorer", "ToEnceledus.script", None, "outer_planet_moon_exploration",
     "Mission to Saturn's moon Enceladus with user-defined celestial bodies (e.g. Titan) using SPICE kernels and NAIF IDs."),
)

# convention tag -> regex searched (MULTILINE) in the script text.
TAG_PATTERNS = {
    "percent_comment_section_banners": r"^%-{10,}",
    "create_objects_before_begin_mission_sequence": r"^Create\s+\w+[^\n]*\n(?s:.*)^BeginMissionSequence\b",
    "gmat_prefixed_property_assignment": r"^GMAT\s+\w+(\.\w+)+\s*=",
    "burn_vnb_axes": r"\.Axes\s*=\s*VNB\b",
    "target_vary_achieve_differential_corrector": r"^\s*Target\b(?s:.*?)^\s*Vary\b(?s:.*?)^\s*Achieve\b",
    "finite_burn_begin_end": r"^\s*BeginFiniteBurn\b",
    "propagate_with_stop_condition": r"^\s*Propagate\b[^\n]*\{[^}\n]*\b\w+(\.\w+)+\s*=",
    "custom_coordinate_systems": r"^Create\s+CoordinateSystem\b",
    "xyplot_output": r"^Create\s+XYPlot\b",
    "orbitview_output": r"^Create\s+OrbitView\b",
    "groundtrackplot_output": r"^Create\s+GroundTrackPlot\b",
    "reportfile_output": r"^Create\s+ReportFile\b",
    "conditional_or_loop_logic": r"^\s*(If|While|For)\b",
}


def detect_convention_tags(text: str) -> list[str]:
    return [
        tag
        for tag, pattern in TAG_PATTERNS.items()
        if re.search(pattern, text, flags=re.MULTILINE)
    ]


def _entry_id(source_dir: str, file_name: str) -> str:
    stem = file_name.removesuffix(".script")
    prefix = "nasa" if source_dir.startswith("nasa") else source_dir.split("/")[-1].split("_")[0].lower()
    return f"{prefix}-{stem}".lower()


def build_corpus(root: Path = ROOT) -> dict:
    entries = []
    for source_dir, file_name, url_suffix, mission_type, description in SCRIPTS:
        source = SOURCES[source_dir]
        raw_path = f"{RAW_RELATIVE_DIR}/{source_dir}/{file_name}"
        text = (root / raw_path).read_text()
        redistributable = source["redistributable"]
        entries.append(
            {
                "id": _entry_id(source_dir, file_name),
                "source_url": source["url_prefix"] + (url_suffix or file_name),
                "source_repo": source["repo"],
                "source_commit": source["commit"],
                "license": dict(source["license"]),
                "redistributable": redistributable,
                "mission_type": mission_type,
                "convention_tags": detect_convention_tags(text),
                "description": description,
                "raw_source_path": raw_path,
                "content_path": raw_path if redistributable else None,
                "content_sha256": sha256_of(root / raw_path),
            }
        )
    corpus = {"schema_version": SCHEMA_VERSION, "entries": entries}
    errors = validate_corpus(corpus, root)
    if errors:
        raise ValueError("generated corpus failed validation:\n" + "\n".join(errors))
    return corpus


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if the committed corpus.json is out of date")
    args = parser.parse_args(argv)

    rendered = json.dumps(build_corpus(ROOT), indent=2, ensure_ascii=False) + "\n"
    target = ROOT / CORPUS_RELATIVE_PATH
    if args.check:
        if not target.is_file() or target.read_text() != rendered:
            print(f"{CORPUS_RELATIVE_PATH} is out of date; rerun without --check", file=sys.stderr)
            return 1
        print(f"{CORPUS_RELATIVE_PATH} is up to date")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered)
    print(f"wrote {CORPUS_RELATIVE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
