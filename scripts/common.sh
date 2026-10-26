#!/usr/bin/env bash
# Shared configuration. Every script sources this file so all variants get identical settings.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS="$ROOT/results"
NODE_VERSION="${NODE_VERSION:-22.22.0}"
VARIANTS=(debian alpine distroless)          # main comparison
ALL_VARIANTS=(debian alpine distroless distroless-debug)
CPUS="${CPUS:-1}"
MEMORY="${MEMORY:-256m}"
HOST_PORT="${HOST_PORT:-8080}"
NET="benchnet"
SYFT_VERSION="${SYFT_VERSION:-}"            # fill in after install, recorded in env.json
img() { echo "bench-$1:latest"; }

ensure_net_and_stub() {
  docker network inspect "$NET" >/dev/null 2>&1 || docker network create "$NET" >/dev/null
  if ! docker ps --format '{{.Names}}' | grep -qx stub; then
    docker rm -f stub >/dev/null 2>&1 || true
    docker run -d --name stub --network "$NET" --network-alias stub \
      -v "$ROOT/stub/stub.js:/stub.js:ro" "node:${NODE_VERSION}-alpine" node /stub.js >/dev/null
  fi
}

# run_app <variant> <name> [extra docker args...]
run_app() {
  local v="$1" name="$2"; shift 2
  docker run -d --name "$name" --network "$NET" -p "${HOST_PORT}:3000" \
    --cpus="$CPUS" --memory="$MEMORY" "$@" "$(img "$v")" >/dev/null
}

wait_ready() {  # prints nothing; returns 0 when /healthz answers 200, 1 on 30 s timeout
  local deadline=$(( $(date +%s%N) + 30000000000 ))
  until curl -sf --max-time 0.5 -o /dev/null "http://localhost:${HOST_PORT}/healthz"; do
    [ "$(date +%s%N)" -gt "$deadline" ] && return 1
    sleep 0.01
  done
}
cleanup_app() { docker rm -f "$1" >/dev/null 2>&1 || true; }
