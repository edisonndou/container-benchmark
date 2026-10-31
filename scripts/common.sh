#!/usr/bin/env bash
# Shared configuration. Every script sources this file so all variants get identical settings.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS="$(realpath -m "${RESULTS_DIR:-$ROOT/results}")"
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

wait_ready() {
  python3 - "$HOST_PORT" <<'PY'
import json
import sys
import time
import urllib.error
import urllib.request

url = f"http://127.0.0.1:{int(sys.argv[1])}/healthz"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({}), NoRedirect()
)
deadline = time.monotonic() + 30

while True:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        sys.exit(1)

    try:
        with opener.open(url, timeout=min(0.5, remaining)) as response:
            payload = json.loads(response.read(65536))
            if (
                response.status == 200
                and isinstance(payload, dict)
                and payload.get("status") == "ok"
            ):
                sys.exit(0)
    except (OSError, ValueError, urllib.error.URLError):
        pass

    time.sleep(0.01)
PY
}

cleanup_app() { docker rm -f "$1" >/dev/null 2>&1 || true; }
