#!/usr/bin/env python3
"""Build a fully self-contained ``site/data/demo-runs.js`` for the static
demo page (``site/demo-visualization-pipeline.html``) so it works when
opened directly as a ``file://`` page -- no local server, and no
``fetch()`` calls at all.

Why this exists: ``site/js/demo-visualization-pipeline.js`` normally loads
each demo's ``run_summary.json``/``run_manifest.json`` (and its referenced
image/HTML artifacts) via ``fetch()`` against a path like
``artifacts/runs/<case_id>/bridge/...``. Browsers block ``fetch()`` between
local files under the ``file://`` protocol, so opening the HTML page
directly (for example via a Windows/WSL UNC path, not through
``./run_site.sh``) cannot load any of that -- the page looks like it
"doesn't load."

This script embeds each demo's manifest and every small image artifact
(PNG/SVG) directly as a ``data:`` URI inside ``site/data/demo-runs.js``'s
``demo.run`` field, which the existing loader already supports
(``loadRun()`` returns ``demo.run`` immediately when present, skipping
``fetch()`` entirely). Large non-image artifacts (for example the ~5 MB
Plotly 3D scene HTML) are left as plain relative links instead of being
inlined, since ``<a href="...">`` to a sibling file still works from
``file://`` even though ``fetch()`` does not, and inlining megabytes of
HTML into a `<script>` tag would make the generated file unwieldy.

Usage::

    .venv/bin/python scripts/build_embedded_demo_runs.py
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data" / "demo-runs.js"

# One real workflow run per demo slot (the demo site's three fixed slots),
# or None when no run has been captured yet (Demo C): in that case the
# existing docs/web-demo-cases.md-derived sample stays in
# artifacts/saved_runs/demo_c/run.json and is embedded instead.
DEMO_RUN_DIRS = {
    "demoA": ROOT / "artifacts/runs/earth-400km-one-period-lvlh-rendezvous/bridge",
    "demoB": ROOT / "artifacts/runs/earth-400km-quarter-period-rendezvous/bridge",
    "demoC": None,
}

# Fallback sample data (not a real workflow run) when a demo has no captured
# run yet; see docs/web-demo-cases.md and artifacts/saved_runs/README.md.
SAMPLE_RUN_FILES = {
    "demoA": ROOT / "artifacts/saved_runs/demo_a/run.json",
    "demoB": ROOT / "artifacts/saved_runs/demo_b/run.json",
    "demoC": ROOT / "artifacts/saved_runs/demo_c/run.json",
}

DEMO_LABELS = {"demoA": "Demo A", "demoB": "Demo B", "demoC": "Demo C"}

# Inlined as data: URIs; anything else (notably the ~5 MB Plotly 3D scene
# HTML) is left as a plain relative link instead.
INLINABLE_MEDIA_TYPES = {"image/png", "image/svg+xml"}


def _data_uri(path: Path, media_type: str) -> str:
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def _embed_artifact(repo_root: Path, artifact: dict) -> dict:
    """Return a copy of ``artifact`` with its ``path`` inlined as a data URI
    when its file exists and its media type is inlinable; otherwise leave the
    original (repo-relative) path as a plain link, and mark it explicitly.
    """
    path_str = artifact.get("path")
    media_type = artifact.get("media_type", "application/octet-stream")
    if not path_str:
        return dict(artifact)
    full_path = (repo_root / path_str) if not Path(path_str).is_absolute() else Path(path_str)
    out = dict(artifact)
    if media_type in INLINABLE_MEDIA_TYPES and full_path.is_file():
        out["path"] = _data_uri(full_path, media_type)
        out["embedded"] = True
    else:
        out["embedded"] = False
    return out


def _embed_step(repo_root: Path, step: dict) -> dict:
    out = dict(step)
    if "artifact" in out and out["artifact"]:
        out["artifact"] = _embed_artifact(repo_root, out["artifact"])
    if "artifacts" in out and out["artifacts"]:
        out["artifacts"] = [_embed_artifact(repo_root, a) for a in out["artifacts"]]
    return out


def build_embedded_run(run_dir: Path) -> dict:
    """Load one workflow run's ``run_summary.json`` and return a copy with
    every inlinable artifact (PNG/SVG) replaced by a ``data:`` URI.
    """
    summary_path = run_dir / "run_summary.json"
    run = json.loads(summary_path.read_text())
    run["steps"] = [_embed_step(ROOT, step) for step in run.get("steps", [])]
    if run.get("artifacts"):
        run["artifacts"] = [_embed_artifact(ROOT, a) for a in run["artifacts"]]
    return run


def build_embedded_sample_run(sample_path: Path) -> dict:
    """Load a pre-existing ``artifacts/saved_runs/<demo>/run.json`` sample
    and inline its image artifacts the same way, for a demo with no
    captured workflow run yet (Demo C).
    """
    run = json.loads(sample_path.read_text())
    run["request"] = run.get("source_request_text", run.get("request", ""))
    for step in run.get("steps", []):
        artifact = step.get("artifact")
        if artifact and artifact.get("path"):
            media_type = artifact.get("media_type", "image/png")
            full_path = ROOT / artifact["path"]
            if media_type in INLINABLE_MEDIA_TYPES and full_path.is_file():
                artifact["path"] = _data_uri(full_path, media_type)
                artifact["embedded"] = True
            else:
                artifact["embedded"] = False
    return run


def main() -> int:
    entries = []
    for demo_id, label in DEMO_LABELS.items():
        run_dir = DEMO_RUN_DIRS.get(demo_id)
        if run_dir is not None and (run_dir / "run_summary.json").is_file():
            run = build_embedded_run(run_dir)
            source_note = f"embedded from {run_dir.relative_to(ROOT).as_posix()}"
        else:
            sample_path = SAMPLE_RUN_FILES[demo_id]
            run = build_embedded_sample_run(sample_path)
            source_note = f"embedded sample from {sample_path.relative_to(ROOT).as_posix()} (no captured workflow run yet)"
        entries.append((demo_id, label, run, source_note))

    lines = ["// Generated by scripts/build_embedded_demo_runs.py -- do not hand-edit.",
              "// Every demo's run data and small image artifacts are embedded as data: URIs",
              "// below (demo.run), so this page works opened directly as a file:// page with",
              "// no local server and no fetch() calls.",
              "window.TCDemoRuns = {"]
    for demo_id, label, run, source_note in entries:
        lines.append(f"  {demo_id}: {{")
        lines.append(f"    id: {json.dumps(demo_id)},")
        lines.append(f"    label: {json.dumps(label)},")
        lines.append("    recordedLabel: \"Recorded run\",")
        lines.append(f"    // {source_note}")
        lines.append(f"    run: {json.dumps(run)},")
        lines.append("  },")
    lines.append("};")
    lines.append("")

    SITE_DATA.write_text("\n".join(lines))
    print(f"Wrote {SITE_DATA.relative_to(ROOT)} ({SITE_DATA.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
