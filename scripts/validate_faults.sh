#!/usr/bin/env bash
# Preparatory validation only: no human diagnosis times are measured.
source "$(dirname "$0")/common.sh"

OUTD="${1:-$RESULTS/pilot/diagnostics_automated}"
if [ -e "$OUTD" ]; then
  echo "STOP: output path already exists: $OUTD" >&2
  exit 1
fi
mkdir -p "$(dirname "$OUTD")"
mkdir "$OUTD"

active=0
phase=setup
trial=""

finish() {
  local rc=$?
  if [ "$active" -eq 1 ]; then
    docker logs app > "$trial/aborted.log" 2>&1 || true
    printf '%s,%s,FAIL,%s\n' "$scenario" "$variant" "$phase" \
      >> "$OUTD/summary.csv"
  fi
  cleanup_app app
  return "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

echo "scenario,variant,result,phase" > "$OUTD/summary.csv"
echo "Preparatory automated checks; no operator diagnosis times." \
  > "$OUTD/README.txt"

ensure_net_and_stub

for variant in alpine distroless; do
  for scenario in config permissions connectivity; do
    trial="$OUTD/${scenario}_${variant}"
    mkdir "$trial"
    active=1
    phase=injection
    echo "Checking: $scenario / $variant"

    bash "$ROOT/scripts/fault.sh" "$scenario" "$variant" \
      > "$trial/setup.log" 2>&1

    if [ "$scenario" = config ]; then
      docker wait app > "$trial/exit_code.txt"
      grep -Fxq '1' "$trial/exit_code.txt"
    else
      wait_ready
    fi

    phase=verify_fault
    before_rc=0
    node "$ROOT/app/test.js" "http://127.0.0.1:$HOST_PORT" \
      > "$trial/test_before.txt" 2>&1 || before_rc=$?
    docker logs app > "$trial/before.log" 2>&1
    docker inspect app > "$trial/before.json"
    [ "$before_rc" -eq 1 ]

    case "$scenario" in
      config)
        grep -Fxq 'RESULT: FAIL (5)' "$trial/test_before.txt"
        grep -Fq 'missing required environment variable' "$trial/before.log"
        grep -Fq 'APP_MODE' "$trial/before.log"
        ;;
      permissions)
        grep -Fxq 'RESULT: FAIL (1)' "$trial/test_before.txt"
        grep -Fxq 'FAIL /file (500)' "$trial/test_before.txt"
        grep -Fq 'EACCES' "$trial/before.log"
        ;;
      connectivity)
        grep -Fxq 'RESULT: FAIL (1)' "$trial/test_before.txt"
        grep -Fxq 'FAIL /upstream (502)' "$trial/test_before.txt"
        grep -Fq 'upstream unreachable' "$trial/before.log"
        grep -Fq 'stub-wrong' "$trial/before.log"
        ;;
    esac

    phase=repair
    if [ "$scenario" = permissions ]; then
      docker run --rm -v benchperm:/d "node:${NODE_VERSION}-alpine" \
        sh -c 'ls -ln /d/sample.txt; chmod 0644 /d/sample.txt; ls -ln /d/sample.txt' \
        > "$trial/repair.log" 2>&1
      echo "helper_container" > "$trial/repair_method.txt"
    else
      cleanup_app app
      run_app "$variant" app -e APP_MODE=bench \
        -e UPSTREAM_URL=http://stub:4000/ping \
        > "$trial/repair.log" 2>&1
      echo "recreate_with_correct_configuration" \
        > "$trial/repair_method.txt"
    fi

    phase=verify_recovery
    wait_ready
    node "$ROOT/app/test.js" "http://127.0.0.1:$HOST_PORT" \
      > "$trial/test_after.txt" 2>&1
    docker logs app > "$trial/after.log" 2>&1
    docker inspect app > "$trial/after.json"
    grep -Fxq 'RESULT: PASS' "$trial/test_after.txt"

    printf '%s,%s,PASS,done\n' "$scenario" "$variant" \
      >> "$OUTD/summary.csv"
    active=0
    cleanup_app app
  done
done

cat "$OUTD/summary.csv"
