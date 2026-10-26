#!/usr/bin/env bash
# Usage: load.sh <reps> [warmup_s] [measure_s] [outdir]
source "$(dirname "$0")/common.sh"

REPS="${1:-10}"
WARM="${2:-30}"
MEAS="${3:-60}"
OUTD="${4:-$RESULTS/load}"
CONNS="${CONNS:-32}"
ENDPOINT="${ENDPOINT:-/compute}"
sp=""

for value in "$REPS" "$WARM" "$MEAS" "$CONNS"; do
  if ! [[ "$value" =~ ^[1-9][0-9]*$ ]]; then
    echo "Repetitions, durations and connections must be positive integers." >&2
    exit 1
  fi
done

command -v autocannon >/dev/null || {
  echo "Autocannon is not available in PATH." >&2
  exit 1
}

if [ -e "$OUTD" ]; then
  echo "STOP: output path already exists: $OUTD" >&2
  echo "Choose a new directory to preserve previous results." >&2
  exit 1
fi

mkdir -p "$OUTD"

stop_sampler() {
  if [ -n "$sp" ]; then
    kill "$sp" 2>/dev/null || true
    wait "$sp" 2>/dev/null || true
    sp=""
  fi
}

finish() {
  stop_sampler
  cleanup_app app
}

save_evidence() {
  docker logs app > "$OUTD/app_${r}_${v}.log" 2>&1 || true
  docker inspect app \
    > "$OUTD/inspect_${r}_${v}.json" \
    2> "$OUTD/inspect_${r}_${v}.stderr" || true
  docker inspect app \
    --format '{{.State.OOMKilled}} {{.RestartCount}}' \
    > "$OUTD/state_${r}_${v}.txt" 2>/dev/null || true
}

trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

ensure_net_and_stub

{
  printf 'REPS=%s\nWARM=%s\nMEAS=%s\n' "$REPS" "$WARM" "$MEAS"
  printf 'CONNS=%s\nENDPOINT=%s\n' "$CONNS" "$ENDPOINT"
  printf 'CPUS=%s\nMEMORY=%s\nHOST_PORT=%s\n' "$CPUS" "$MEMORY" "$HOST_PORT"
  autocannon --version
} > "$OUTD/settings.txt" 2>&1

echo "round,variant,status,exit_code" > "$OUTD/runs.csv"

for r in $(seq 1 "$REPS"); do
  for v in $(printf '%s\n' "${VARIANTS[@]}" | shuf); do
    cleanup_app app
    echo "Load test: round=$r variant=$v"

    rc=0
    run_app "$v" app 2> "$OUTD/start_${r}_${v}.stderr" || rc=$?
    if [ "$rc" -ne 0 ]; then
      save_evidence
      echo "$r,$v,START_FAIL,$rc" >> "$OUTD/runs.csv"
      cleanup_app app
      continue
    fi

    if ! wait_ready; then
      save_evidence
      echo "$r,$v,NOT_READY,1" >> "$OUTD/runs.csv"
      cleanup_app app
      continue
    fi

    rc=0
    autocannon -c "$CONNS" -d "$WARM" \
      "http://localhost:${HOST_PORT}${ENDPOINT}" \
      > "$OUTD/warmup_${r}_${v}.stdout" \
      2> "$OUTD/warmup_${r}_${v}.stderr" || rc=$?

    if [ "$rc" -ne 0 ]; then
      save_evidence
      echo "$r,$v,WARMUP_FAIL,$rc" >> "$OUTD/runs.csv"
      cleanup_app app
      continue
    fi

    docker stats app \
      --format '{{.CPUPerc}},{{.MemUsage}}' \
      > "$OUTD/stats_${r}_${v}.csv" \
      2> "$OUTD/stats_${r}_${v}.stderr" &
    sp=$!

    rc=0
    autocannon -c "$CONNS" -d "$MEAS" -j \
      "http://localhost:${HOST_PORT}${ENDPOINT}" \
      > "$OUTD/ac_${r}_${v}.json" \
      2> "$OUTD/ac_${r}_${v}.stderr" || rc=$?

    stop_sampler
    save_evidence

    status=COMPLETED
    if [ "$rc" -ne 0 ]; then
      status=AUTOCANNON_FAIL
    fi
    echo "$r,$v,$status,$rc" >> "$OUTD/runs.csv"

    cleanup_app app
    sleep 3
  done
done

cat "$OUTD/runs.csv"
