"""Regression checks for the standalone demo page (TJC-21.4).

The page carries a Content-Security-Policy with ``script-src 'self'``, so any
inline <script> body is silently blocked by the browser and the demo never
renders. That was the real cause of the "Demo A/B/C do not load" report. These
checks keep that from regressing without needing a browser.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
PAGE = Path(os.environ.get("DEMO_PAGE_UNDER_TEST", ROOT / "site/demo-visualization-pipeline.html"))
DATA = ROOT / "site/data/demo-runs.js"


def test_no_inline_script_body_under_script_src_self():
    html = PAGE.read_text()
    assert "script-src 'self'" in html
    for match in re.finditer(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", html, re.S):
        if "src=" not in match.group("attrs"):
            assert not match.group("body").strip(), "inline script is blocked by the page CSP"


def test_page_script_and_data_are_referenced_and_exist():
    html = PAGE.read_text()
    for src in re.findall(r'<script src="([^"]+)"', html):
        assert (ROOT / "site" / src).is_file(), src


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_demo_data_file_parses_and_has_three_demos():
    code = (
        "const vm=require('vm');const fs=require('fs');const c={window:{}};vm.createContext(c);"
        f"vm.runInContext(fs.readFileSync({str(DATA)!r},'utf8'),c);"
        "console.log(Object.keys(c.window.TCDemoRuns).join(','))"
    )
    out = subprocess.run(["node", "-e", code], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "demoA,demoB,demoC"


# --- chat-style playback (TJC-21.4 scope change) ---------------------------------
JS = ROOT / "site/js/demo-visualization-pipeline.js"
CONTROL_IDS = ("chat-log", "play-pause", "next-step", "show-all", "restart")


def test_page_has_chat_log_and_playback_controls():
    html = PAGE.read_text()
    for control_id in CONTROL_IDS:
        assert f'id="{control_id}"' in html, control_id


def test_playback_delay_defaults_to_1500ms_and_is_overridable_by_url():
    js = JS.read_text()
    assert "URLSearchParams" in js and "DELAY_MS" in js
    assert "1500" in js


def test_script_shows_request_as_a_user_message_then_agent_steps():
    js = JS.read_text()
    assert "msg user" in js and "msg agent" in js
    assert js.index("msg user") < js.index("msg agent")


def test_page_labels_data_as_sample_until_recaptured():
    assert "sample data" in PAGE.read_text().lower()
