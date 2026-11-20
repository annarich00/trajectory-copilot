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
directly (for example via a Windows/WSL UNC path) cannot load any of
that -- the page looks like it "doesn't load."

This script embeds each demo's manifest and every small image artifact
(PNG/SVG) directly as a ``data:`` URI inside ``site/data/demo-runs.js``'s
``demo.run`` field, which the existing loader already supports
(``loadRun()`` returns ``demo.run`` immediately when present, skipping
``fetch()`` entirely). Large non-image artifacts (for example the ~5 MB
Plotly 3D scene HTML) are left as relative artifact paths instead of being
inlined; the page embeds those paths in a local iframe, while inlining
megabytes of HTML into a `<script>` tag would make the generated file
unwieldy.

Usage::

    .venv/bin/python scripts/build_embedded_demo_runs.py
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data" / "demo-runs.js"

# One real recorded workflow run per demo slot; see docs/web-demo-cases.md.
# Demo A recorded NUMERICAL_DISAGREEMENT, Demo B passed at its recorded
# tolerances, Demo C was refused by the model selector (UNSUPPORTED), and
# Demo D records a 15-candidate transfer-time scan whose minimum is not
# GMAT-verified.
DEMO_RUN_DIRS = {
    "demoA": ROOT / "artifacts/runs/demo-a-400km-one-period-10km-alongtrack/bridge",
    "demoB": ROOT / "artifacts/runs/demo-b-400km-quarter-period-10km-alongtrack/bridge",
    "demoC": ROOT / "artifacts/runs/demo-c-400km-quarter-period-14000km-alongtrack",
    "demoD": ROOT / "artifacts/runs/earth-400km-15time-scan",
}

# A run's full record is its run_summary.json when the pipeline reached a GMAT
# verification, and its run_manifest.json otherwise; the first of these that
# exists in a run directory is the one embedded.
RUN_FILE_NAMES = ("run_summary.json", "run_manifest.json")

DEMO_LABELS = {"demoA": "Demo A", "demoB": "Demo B", "demoC": "Demo C", "demoD": "Demo D — 15-time scan"}

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


def run_file_for(run_dir: Path) -> Path | None:
    """Return the run's full record (see :data:`RUN_FILE_NAMES`), or ``None``
    when the directory holds neither."""
    for name in RUN_FILE_NAMES:
        candidate = run_dir / name
        if candidate.is_file():
            return candidate
    return None


def build_embedded_run(run_file: Path) -> dict:
    """Load one recorded run and return a copy with every inlinable artifact
    (PNG/SVG) replaced by a ``data:`` URI.
    """
    run = json.loads(run_file.read_text())
    run["steps"] = [_embed_step(ROOT, step) for step in run.get("steps", [])]
    if run.get("artifacts"):
        run["artifacts"] = [_embed_artifact(ROOT, a) for a in run["artifacts"]]
    return run


def main() -> int:
    entries = []
    for demo_id, label in DEMO_LABELS.items():
        run_file = run_file_for(DEMO_RUN_DIRS[demo_id])
        if run_file is None:
            raise SystemExit(f"{demo_id}: no {' or '.join(RUN_FILE_NAMES)} in {DEMO_RUN_DIRS[demo_id]}")
        run = build_embedded_run(run_file)
        source_note = f"embedded from {run_file.relative_to(ROOT).as_posix()}"
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
