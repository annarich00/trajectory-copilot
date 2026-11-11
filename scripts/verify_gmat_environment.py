
#!/usr/bin/env python3
"""
Verify that Trajectory CoPilot is configured to execute GMAT
scripts through the GMAT Console (GmatConsole).

Run from repository root:
    python scripts/verify_gmat_environment.py

Optionally execute a known-good GMAT script:
    python scripts/verify_gmat_environment.py --script path/to/test.script

Override the GMAT installation:
    GMAT_BIN=/path/to/GMAT/R2026a/bin \
        python scripts/verify_gmat_environment.py
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_GMAT_BIN = Path.home() / "opt/GMAT/R2026a/bin"
GMAT_BIN = Path(os.environ.get("GMAT_BIN", DEFAULT_GMAT_BIN)).expanduser()
GMAT_CONSOLE = GMAT_BIN / "GmatConsole"

# Directories where the agent's execution logic/configuration may live.
SEARCH_DIRS = ["src", ".pi", "scripts"]

# Executables that would indicate a different GMAT execution path.
ALTERNATIVE_EXECUTABLES = [
    "GmatMain",
    "GMAT.exe",
    "GmatGUI",
]

SKIP_DIRS = {
    ".git", ".venv", "venv", "__pycache__",
    "node_modules", ".pytest_cache",
}


def section(title):
    print(f"\n{'=' * 65}\n{title}\n{'=' * 65}")


def check_file_system():
    section("1. GMAT installation")

    print(f"Repository:    {ROOT}")
    print(f"GMAT bin:      {GMAT_BIN}")
    print(f"GmatConsole:   {GMAT_CONSOLE}")

    if not GMAT_BIN.is_dir():
        print("[FAIL] GMAT bin directory does not exist.")
        return False

    if not GMAT_CONSOLE.is_file():
        print("[FAIL] GmatConsole executable not found.")
        return False

    if not os.access(GMAT_CONSOLE, os.X_OK):
        print("[FAIL] GmatConsole exists but is not executable.")
        return False

    print("[PASS] GmatConsole exists and is executable.")
    return True


def find_agent_references():
    section("2. Agent configuration and execution code")

    matches = []
    alternative_matches = []

    for directory in SEARCH_DIRS:
        base = ROOT / directory

        if not base.exists():
            continue

        for path in base.rglob("*"):
            if not path.is_file():
                continue

            if any(part in SKIP_DIRS for part in path.parts):
                continue

            if path.suffix.lower() not in {
                ".py", ".md", ".json", ".yaml", ".yml",
                ".toml", ".sh", ".js", ".ts"
            }:
                continue

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
            except OSError:
                continue

            relative = path.relative_to(ROOT)

            for line_number, line in enumerate(
                content.splitlines(), start=1
            ):
                if "GmatConsole" in line:
                    matches.append(
                        (relative, line_number, line.strip())
                    )

                for executable in ALTERNATIVE_EXECUTABLES:
                    if executable.lower() in line.lower():
                        alternative_matches.append(
                            (relative, line_number, line.strip())
                        )

    if matches:
        print("[PASS] References to GmatConsole found:")
        for path, line_number, line in matches:
            print(f"  {path}:{line_number}: {line}")
    else:
        print("[WARN] No GmatConsole references found in searched files.")

    if alternative_matches:
        print("\n[WARN] Other GMAT executable references found:")
        for path, line_number, line in alternative_matches:
            print(f"  {path}:{line_number}: {line}")
    else:
        print("\n[PASS] No references to alternative GMAT executables found.")

    return matches, alternative_matches


def check_execution_implementation(matches):
    section("3. Check for an actual execution implementation")

    if not matches:
        print("[WARN] Cannot identify a GmatConsole execution implementation.")
        return False

    execution_patterns = [
        r"subprocess",
        r"Popen",
        r"run\s*\(",
        r"os\.system",
        r"exec",
    ]

    candidate_files = sorted(set(path for path, _, _ in matches))
    found = False

    for relative in candidate_files:
        path = ROOT / relative

        try:
            content = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        except OSError:
            continue

        if any(re.search(pattern, content) for pattern in execution_patterns):
            print(f"[PASS] Possible execution implementation: {relative}")
            found = True

    if not found:
        print(
            "[WARN] GmatConsole is referenced, but no obvious process "
            "execution call was found in those files."
        )

    return found


def run_console_test(script_path):
    section("4. Actual GmatConsole execution test")

    script = Path(script_path).expanduser().resolve()

    if not script.is_file():
        print(f"[FAIL] Test script not found: {script}")
        return False

    command = [
        str(GMAT_CONSOLE),
        "--run",
        str(script),
        "--exit",
    ]

    print("Executing:")
    print(" ".join(command))
    print(f"Working directory: {GMAT_BIN}")

    try:
        result = subprocess.run(
            command,
            cwd=str(GMAT_BIN),
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        print("[FAIL] GMAT execution timed out.")
        return False
    except OSError as error:
        print(f"[FAIL] Could not launch GmatConsole: {error}")
        return False

    print(f"\nReturn code: {result.returncode}")

    if result.stdout:
        print("\n--- STDOUT (last 4000 characters) ---")
        print(result.stdout[-4000:])

    if result.stderr:
        print("\n--- STDERR (last 4000 characters) ---")
        print(result.stderr[-4000:])

    if result.returncode == 0:
        print("[PASS] GmatConsole process returned successfully.")
        print(
            "[NOTE] This confirms execution through GmatConsole, "
            "but not yet that the simulation results are correct."
        )
        return True

    print("[FAIL] GmatConsole returned a nonzero exit code.")
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--script",
        help="Optional known-good GMAT .script file to execute."
    )
    args = parser.parse_args()

    section("TRAJECTORY COPILOT — GMAT ENVIRONMENT AUDIT")

    install_ok = check_file_system()
    matches, alternatives = find_agent_references()
    implementation_ok = check_execution_implementation(matches)

    execution_ok = None

    if args.script and install_ok:
        execution_ok = run_console_test(args.script)

    section("5. AUDIT SUMMARY")

    checks = {
        "GmatConsole installed and executable": install_ok,
        "Agent references GmatConsole": bool(matches),
        "Possible execution implementation found": implementation_ok,
        "Alternative GMAT executable references": not bool(alternatives),
    }

    for name, passed in checks.items():
        status = "[PASS]" if passed else "[WARN/FAIL]"
        print(f"{status} {name}")

    if execution_ok is not None:
        print(
            f"{'[PASS]' if execution_ok else '[FAIL]'} "
            "GmatConsole test execution"
        )

    print("\nImportant: static inspection cannot prove which executable")
    print("the agent actually launches at runtime.")
    print("Use the runtime process check described below.")

    if not install_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
