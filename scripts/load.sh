#!/usr/bin/env bash
# Load test + resource sampling. Usage: load.sh <reps> [warmup_s] [measure_s] [outdir]
# Requires autocannon on the host: npm i -g autocannon@8.0.0
source "$(dirname "$0")/common.sh"
REPS="${1:-10}"; WARM="${2:-30}"; MEAS="${3:-60}"; OUTD="${4:-$RESULTS/load}"
CONNS="${CONNS:-32}"; ENDPOINT="${ENDPOINT:-/compute}"
mkdir -p "$OUTD"; ensure_net_and_stub
for r in $(seq 1 "$REPS"); do
  for v in $(printf '%s\n' "${VARIANTS[@]}" | shuf); do
    cleanup_app app; run_app "$v" app; wait_ready || { echo "$r,$v,NOT_READY" >> "$OUTD/failures.log"; continue; }
    autocannon -c "$CONNS" -d "$WARM" "http://localhost:${HOST_PORT}${ENDPOINT}" >/dev/null 2>&1   # warm-up, discarded
    ( while true; do docker stats app --no-stream --format '{{.CPUPerc}},{{.MemUsage}}' >> "$OUTD/stats_${r}_${v}.csv" 2>/dev/null || break; sleep 1; done ) &
    sp=$!
    autocannon -c "$CONNS" -d "$MEAS" -j "http://localhost:${HOST_PORT}${ENDPOINT}" > "$OUTD/ac_${r}_${v}.json" 2>/dev/null || echo "$r,$v,AUTOCANNON_FAIL" >> "$OUTD/failures.log"
    kill $sp 2>/dev/null || true; wait $sp 2>/dev/null || true
    docker inspect app --format '{{.State.OOMKilled}} {{.RestartCount}}' > "$OUTD/state_${r}_${v}.txt"
    cleanup_app app; sleep 3
  done
done
