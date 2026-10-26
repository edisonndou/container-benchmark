#!/usr/bin/env bash
# Time from `docker run` until the first valid /healthz response. Images are already local (no pull time).
# Usage: startup.sh <reps> [outfile]
source "$(dirname "$0")/common.sh"
REPS="${1:-10}"; OUT="${2:-$RESULTS/startup.csv}"
ensure_net_and_stub
[ -f "$OUT" ] || echo "round,variant,startup_ms,ok" > "$OUT"
for r in $(seq 1 "$REPS"); do
  for v in $(printf '%s\n' "${VARIANTS[@]}" | shuf); do     # random order each round
    cleanup_app app
    t0=$(date +%s%N)
    run_app "$v" app
    if wait_ready; then ok=1; else ok=0; fi
    t1=$(date +%s%N)
    echo "$r,$v,$(( (t1 - t0) / 1000000 )),$ok" | tee -a "$OUT"
    cleanup_app app; sleep 2
  done
done
