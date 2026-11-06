#!/usr/bin/env python3
"""TJC-19 AC3 probe: does ``attempt_gmat_gui_screenshot``'s own non-interactive
capture path hit the same teardown SIGSEGV that a ``-r``/``-x`` GUI run does?

The distinction that matters for AC3: ``attempt_gmat_gui_screenshot`` launches
GMAT with ``-ns -r <script>`` and *no* ``-x``, then kills it from the outside
(``process.terminate()``, escalating to ``process.kill()``) after grabbing the
window. It therefore never asks GMAT to run its own wxWidgets/OpenFrames
window-teardown path at all. This probe calls the real function on each TJC-19
variant and records both the capture result AND the killed process's exit
status, so "did the capture succeed" and "did the process die by SIGSEGV
rather than by our signal" are answered separately with observed evidence
instead of reasoning.

Run from the repo root:
    .venv/bin/python artifacts/tjc19_diagnosis/ac3_screenshot_probe.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import src.gmat_verify as gmat_verify  # noqa: E402
from src.gmat_verify import attempt_gmat_gui_screenshot  # noqa: E402

GUI_EXECUTABLE = str(Path.home() / "opt/GMAT/R2026a/bin/GMAT-R2026a")
VARIANTS_DIR = Path(__file__).resolve().parent / "variants"
OUT_DIR = Path(__file__).resolve().parent / "ac3_captures"


def _record_launched_processes() -> list[subprocess.Popen]:
    """Patch ``subprocess.Popen`` as seen by ``src.gmat_verify`` so this probe can
    read each launched GMAT child's final ``returncode`` after the function returns.

    This is the only way to observe *how* the GMAT child died inside
    ``attempt_gmat_gui_screenshot``: that function's ``GMATGUIScreenshotResult``
    deliberately reports only the capture outcome, not the child's exit status,
    and its ``finally`` block reaps the process before returning. A
    ``returncode`` of ``-15``/``-9`` means this repo's own
    ``terminate()``/``kill()`` ended it; ``-11`` would mean it had already died
    of SIGSEGV on its own, which is exactly the distinction AC3 asks for.
    """
    launched: list[subprocess.Popen] = []
    real_popen = subprocess.Popen

    class RecordingPopen(real_popen):  # type: ignore[misc,valid-type]
        def __init__(self, args, **kwargs):
            super().__init__(args, **kwargs)
            # Match only the *executable* (argv[0]), not any argument: patching
            # ``gmat_verify.subprocess.Popen`` patches the shared ``subprocess``
            # module, so a looser match also catches this probe's own
            # ``ps -C GMAT-R2026a`` leftover check and pollutes the evidence.
            argv = args if isinstance(args, (list, tuple)) else [args]
            if argv and "GMAT-R2026a" in str(argv[0]):
                launched.append(self)

    gmat_verify.subprocess.Popen = RecordingPopen  # type: ignore[assignment]
    return launched


def main() -> int:
    launched = _record_launched_processes()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    variants = sorted(VARIANTS_DIR.glob("variant_*.script"))
    print(f"idle check before timing: {subprocess.run(['uptime'], capture_output=True, text=True).stdout.strip()}")
    for script in variants:
        output_path = OUT_DIR / f"{script.stem}.png"
        start = time.monotonic()
        result = attempt_gmat_gui_screenshot(GUI_EXECUTABLE, script, output_path)
        elapsed = time.monotonic() - start
        leftover = subprocess.run(
            ["bash", "-c", "ps -o pid,stat,comm -C GMAT-R2026a 2>/dev/null || true"],
            capture_output=True, text=True,
        ).stdout.strip()
        size = output_path.stat().st_size if output_path.exists() else 0
        returncodes = [p.returncode for p in launched]
        launched.clear()
        print(
            f"\n=== {script.name} ===\n"
            f"  elapsed_s      = {elapsed:.2f}\n"
            f"  attempted      = {result.attempted}\n"
            f"  captured       = {result.captured}\n"
            f"  png_bytes      = {size}\n"
            f"  gmat_returncode= {returncodes} (-15=SIGTERM from terminate(), -9=SIGKILL, -11=SIGSEGV)\n"
            f"  reason         = {result.reason}\n"
            f"  leftover_procs = {leftover or '(none)'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
