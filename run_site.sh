#!/usr/bin/env bash
# Trajectory CoPilot — Interactive Physics & Verification Lab
#
# Serves the local educational site in ./site using a tiny Node static file
# server (no external dependencies; Node is already required by the pi
# toolchain in this environment). Works entirely offline.
#
# Usage:
#   ./run_site.sh            # serve on 127.0.0.1, default port 4173
#   PORT=5050 ./run_site.sh  # serve on a specific port
#   ./run_site.sh 5050       # same, via argument

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PORT="${1:-${PORT:-4173}}"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required to run this local server but was not found on PATH." >&2
  exit 1
fi

echo "Trajectory CoPilot — Interactive Physics & Verification Lab"
echo "Serving ./site on http://127.0.0.1:${PORT}  (Ctrl+C to stop)"
echo

exec node "$(dirname "${BASH_SOURCE[0]}")/site/server.js" "$PORT"
