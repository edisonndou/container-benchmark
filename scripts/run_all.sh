#!/usr/bin/env bash
# Usage: run_all.sh pilot   (3 reps, 15 s warm-up, 20 s measure, results/pilot)
#        run_all.sh main    (10 reps, 30 s warm-up, 60 s measure, results/main)
source "$(dirname "$0")/common.sh"
MODE="${1:?pilot|main}"
case "$MODE" in pilot) R=3; W=15; M=20;; main) R=10; W=30; M=60;; *) exit 1;; esac
OUTD="$RESULTS/$MODE"; mkdir -p "$OUTD"
"$ROOT/scripts/build.sh"
"$ROOT/scripts/functional.sh"
"$ROOT/scripts/inspect_images.sh"
"$ROOT/scripts/scan.sh"
"$ROOT/scripts/startup.sh" "$R" "$OUTD/startup.csv"
"$ROOT/scripts/load.sh" "$R" "$W" "$M" "$OUTD/load"
python3 "$ROOT/scripts/analyze_perf.py" "$OUTD"
