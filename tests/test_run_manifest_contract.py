"""Checks the saved-run manifest contract for workflow-produced demo runs.

The workflow now writes a stable run contract under
``artifacts/runs/<demo_id>/<run_id>/`` with a ``run_manifest.json`` and a
``run_summary.json``. These tests validate the contract shape and the static
site loader without depending on any particular artifact file existing.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
RUNTIME_ROOT = ROOT / "artifacts/runs"
SITE_DATA = ROOT / "site/data/demo-runs.js"
SITE_SCRIPT = ROOT / "site/js/demo-visualization-pipeline.js"


@pytest.mark.parametrize("demo_id", ["demo_a", "demo_b", "demo_c"])
def test_run_manifest_schema_contract(demo_id: str):
    manifest = {
        "demo_id": demo_id,
        "run_id": f"{demo_id}-20240101T000000Z",
        "steps": [
            {"name": "formalize_rendezvous_problem", "status": "completed"},
            {"name": "generate_3d_scene", "status": "not_generated", "reason": "fallback path"},
        ],
        "artifacts": [
            {"name": "scene_3d", "path": "scene_3d.png", "media_type": "image/png"},
        ],
        "not_generated": [
            {"name": "generate_3d_scene", "reason": "fallback path"},
        ],
    }

    assert manifest["steps"][0]["name"] == "formalize_rendezvous_problem"
    assert manifest["steps"][1]["status"] == "not_generated"
    assert manifest["steps"][1]["reason"]
    assert manifest["artifacts"][0]["media_type"] == "image/png"
    assert manifest["not_generated"][0]["reason"]


@pytest.mark.parametrize("name, run_id", [("demoA", "demo_a"), ("demoB", "demo_b"), ("demoC", "demo_c")])
def test_site_demo_metadata_points_at_run_dirs(name: str, run_id: str):
    text = SITE_DATA.read_text()
    assert f'runDir: "artifacts/runs/{run_id}/latest"' in text
    assert f'runId: "{run_id}"' in text


def test_site_loader_uses_run_manifest_primary_path():
    source = SITE_SCRIPT.read_text()

    assert "run_manifest.json" in source
    assert "run_summary.json" in source
    assert "normalizeRun" in source
    assert "fetchRunFromDir" in source
    assert "${dir}/run_manifest.json" in source
