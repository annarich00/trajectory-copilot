#!/usr/bin/env bash
# TJC-19 diagnostic harness: run one GMAT GUI preview script variant under a
# self-managed Xvfb display, with a bounded timeout, and capture everything
# needed to tell a hang apart from a slow-but-completing run apart from a
# segfault.
#
# Why this harness exists (and why the previous TJC-19 session's results were
# misread): "===> Total Run Time: %.3lf seconds" and "Mission run completed."
# are emitted by libGmatBase.so into GMAT's *log file*, NOT onto stdout
# (confirmed via `strings bin/libGmatBase.so`). The previous session grepped
# only the captured stdout and concluded its runs "never reached Mission run
# completed"; that conclusion cannot be drawn from stdout at all. This harness
# therefore passes an explicit per-run `-l <logfile>` so each run gets its own
# GMAT log, and reports the run time from there.
#
# It also uses `-x` (--exit: exit GMAT after running the specified script) in
# addition to `-r`. The operator's original segfaulting run used a bare
# `-r` with no `-x`, which leaves the GUI event loop running forever after the
# mission completes (the operator closed the window by hand, and the segfault
# happened during that teardown). A bare `-r` under a timeout can therefore
# NEVER exit on its own, so exit code 124 from such a run means only "the GUI
# was still open", not "GMAT hung". `-x` drives GMAT through its own
# ExitMainLoop teardown, which is the closest automatable analogue of the
# operator's manual window close, and makes the process exit code meaningful
# (0 = clean exit, 139 = SIGSEGV on teardown, 124 = genuinely stuck).
#
# Usage: run_variant.sh <label> <script-path> <timeout-seconds> <with|without> [xvfb|inherit]
#   4th arg selects whether LD_LIBRARY_PATH includes GMAT's lib/ dir (the
#   TJC-3 asset-loading fix that attempt_gmat_gui_screenshot applies and a
#   bare interactive launch does not).
#   5th arg (default xvfb) selects the render target: a fresh self-managed Xvfb
#   framebuffer, or the sandbox's inherited DISPLAY (:0, WSLg's RDP-remoted X
#   server) -- which is what the operator's own segfaulting/124s interactive run
#   actually used, and is therefore required to reproduce its TIMING rather than
#   just its exit status.
set -u

LABEL="$1"
SCRIPT="$(readlink -f "$2")"
TIMEOUT_S="$3"
LDMODE="$4"
DISPMODE="${5:-xvfb}"

GMAT_BIN="$HOME/opt/GMAT/R2026a/bin"
GMAT_LIB="$HOME/opt/GMAT/R2026a/lib"
OUT_DIR="$(cd "$(dirname "$0")" && pwd)/logs"
mkdir -p "$OUT_DIR"

STDOUT_LOG="$OUT_DIR/${LABEL}.stdout.log"
GMAT_LOG="$OUT_DIR/${LABEL}.gmatlog.txt"
PS_LOG="$OUT_DIR/${LABEL}.ps.log"
SUMMARY="$OUT_DIR/${LABEL}.summary.txt"
rm -f "$STDOUT_LOG" "$GMAT_LOG" "$PS_LOG" "$SUMMARY"

# --- idle check, recorded with the timing it qualifies (method constraint) ---
{
  echo "label=$LABEL"
  echo "script=$SCRIPT"
  echo "timeout_s=$TIMEOUT_S"
  echo "ld_library_path_mode=$LDMODE"
  echo "display_mode=$DISPMODE"
  echo "--- pre-run idle check ---"
  uptime
  ps aux --sort=-%cpu | head -10
  echo "--- pre-run leftover GMAT processes ---"
  ps aux | grep -i '[g]mat' || echo "(none)"
  free -h
} >"$SUMMARY" 2>&1

# --- render target: either a fresh self-managed Xvfb (same -listen tcp
#     requirement as src/gmat_verify.py: /tmp/.X11-unix is read-only in this
#     sandbox) or the inherited WSLg DISPLAY ---
XVFB_PID=""
if [ "$DISPMODE" = "inherit" ]; then
  RUN_DISPLAY="${DISPLAY:-:0}"
  echo "inherited_display=$RUN_DISPLAY (no Xvfb launched)" >>"$SUMMARY"
else
  DISPNUM=0
  for n in $(seq 90 140); do
    if ! (echo >"/dev/tcp/127.0.0.1/$((6000 + n))") 2>/dev/null; then
      DISPNUM="$n"
      break
    fi
  done
  if [ "$DISPNUM" = "0" ]; then
    echo "FATAL: no free display number" >>"$SUMMARY"
    exit 2
  fi
  Xvfb ":$DISPNUM" -screen 0 1920x1080x24 -nolisten unix -listen tcp >/dev/null 2>&1 &
  XVFB_PID=$!
  for _ in $(seq 1 25); do
    if (echo >"/dev/tcp/127.0.0.1/$((6000 + DISPNUM))") 2>/dev/null; then break; fi
    sleep 0.2
  done
  RUN_DISPLAY=":$DISPNUM"
  echo "xvfb_display=$RUN_DISPLAY xvfb_pid=$XVFB_PID" >>"$SUMMARY"
fi

# --- periodic ps/free snapshots, to tell an unbounded memory leak apart from
#     a plateauing spin-wait if a run does hang (README step 4) ---
(
  while true; do
    echo "=== t=$(date +%H:%M:%S) ==="
    ps -o pid,etimes,pcpu,rss,vsz,stat,comm -C GMAT-R2026a 2>/dev/null || echo "(no GMAT process)"
    free -m | head -2
    sleep 5
  done
) >"$PS_LOG" 2>&1 &
SNAP_PID=$!

cd "$GMAT_BIN" || exit 2
export DISPLAY="$RUN_DISPLAY"
export LIBGL_ALWAYS_SOFTWARE=1
export GDK_BACKEND=x11
unset WAYLAND_DISPLAY
if [ "$LDMODE" = "with" ]; then
  export LD_LIBRARY_PATH="$GMAT_LIB"
else
  unset LD_LIBRARY_PATH
fi

START=$(date +%s.%N)
timeout "${TIMEOUT_S}s" ./GMAT-R2026a -ns -x -l "$GMAT_LOG" -r "$SCRIPT" >"$STDOUT_LOG" 2>&1
EXIT_CODE=$?
END=$(date +%s.%N)
WALL=$(echo "$END - $START" | bc)

kill "$SNAP_PID" 2>/dev/null
pkill -f 'GMAT-R2026a' 2>/dev/null
[ -n "$XVFB_PID" ] && kill "$XVFB_PID" 2>/dev/null
sleep 1

{
  echo "--- result ---"
  echo "exit_code=$EXIT_CODE   (0=clean exit, 124=timeout/stuck, 139=SIGSEGV, 134=SIGABRT)"
  echo "wall_seconds=$WALL"
  echo "stdout_lines=$(wc -l <"$STDOUT_LOG")"
  echo "font_error_lines=$(grep -c 'Error reading file' "$STDOUT_LOG" 2>/dev/null || echo 0)"
  echo "--- GMAT log run-time / completion markers ---"
  grep -E 'Total Run Time|Mission run completed|GUI exiting|Segmentation' "$GMAT_LOG" 2>/dev/null || echo "(no run-time marker in GMAT log)"
  echo "--- stdout segfault/abort markers ---"
  grep -iE 'segmentation|abort|core dumped|terminate called' "$STDOUT_LOG" 2>/dev/null || echo "(none)"
  echo "--- peak RSS observed in snapshots (MB) ---"
  awk '/^ *[0-9]+ /{if ($4+0 > max) max=$4+0} END{printf "%.0f\n", max/1024}' "$PS_LOG" 2>/dev/null
  echo "--- post-run leftover GMAT processes ---"
  ps aux | grep -i '[g]mat' || echo "(none)"
} >>"$SUMMARY" 2>&1

cat "$SUMMARY"
