#!/usr/bin/env bash
# Creates ONE injected fault. The "preparer" runs this; the "diagnoser" must not know which scenario it is.
# Usage: fault.sh <config|permissions|connectivity> <variant>   -> leaves container "app" running/failed
source "$(dirname "$0")/common.sh"
if [ "$#" -ne 2 ]; then
  echo "Usage: fault.sh <config|permissions|connectivity> <variant>" >&2
  exit 1
fi
S="$1"; V="$2"
case "$S" in
  config|permissions|connectivity) ;;
  *) echo "Unknown scenario: $S" >&2; exit 1 ;;
esac
case "$V" in
  debian|alpine|distroless|distroless-debug) ;;
  *) echo "Unknown variant: $V" >&2; exit 1 ;;
esac
ensure_net_and_stub
cleanup_app app
case "$S" in
  config)       run_app "$V" app -e APP_MODE= ;;                       # empty -> treated as missing
  permissions)  # Volume with a root-owned, mode-600 sample.txt mounted at /data: the non-root app user cannot read it.
                docker volume rm -f benchperm >/dev/null 2>&1 || true
                docker run --rm -v benchperm:/d "node:${NODE_VERSION}-alpine" \
                  sh -c 'echo secret > /d/sample.txt && chown 0:0 /d/sample.txt && chmod 600 /d/sample.txt'
                run_app "$V" app -v benchperm:/data ;;
  connectivity) run_app "$V" app -e UPSTREAM_URL=http://stub-wrong:4000/ping ;;
  *) echo "unknown scenario"; exit 1 ;;
esac
echo "Fault prepared. Container name: app, published at http://localhost:${HOST_PORT}"
echo "Fix criterion: node app/test.js http://localhost:${HOST_PORT} prints RESULT: PASS"
