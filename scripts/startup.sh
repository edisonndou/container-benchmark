#!/usr/bin/env bash
# Measure container launch to readiness, with images already local.
# Usage: startup.sh <reps> [outfile]
source "$(dirname "$0")/common.sh"

REPS="${1:-10}"
OUT="${2:-$RESULTS/startup.csv}"

if ! [[ "$REPS" =~ ^[1-9][0-9]*$ ]]; then
  echo "Repetitions must be a positive integer." >&2
  exit 1
fi

if [ -e "$OUT" ]; then
  echo "STOP: output already exists: $OUT" >&2
  echo "Choose a new output path to preserve previous results." >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
ensure_net_and_stub
trap 'cleanup_app app' EXIT

echo "round,variant,startup_ms,ok" > "$OUT"

for r in $(seq 1 "$REPS"); do
  for v in $(printf '%s\n' "${VARIANTS[@]}" | shuf); do
    cleanup_app app

    t0=$(date +%s%N)
    if run_app "$v" app && wait_ready; then
      ok=1
    else
      ok=0
    fi
    t1=$(date +%s%N)

    echo "$r,$v,$(( (t1 - t0) / 1000000 )),$ok" \
      | tee -a "$OUT"

    if [ "$ok" -eq 0 ]; then
      docker logs app > "${OUT%.csv}_${r}_${v}.log" 2>&1 || true
    fi

    cleanup_app app
    sleep 2
  done
done
