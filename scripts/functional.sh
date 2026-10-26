#!/usr/bin/env bash
# Same functional tests against every variant (requires node on the host).
source "$(dirname "$0")/common.sh"
ensure_net_and_stub
OUT="$RESULTS/functional.csv"; echo "variant,result" > "$OUT"
for v in "${ALL_VARIANTS[@]}"; do
  cleanup_app app; run_app "$v" app
  if wait_ready && node "$ROOT/app/test.js" "http://localhost:${HOST_PORT}"; then r=PASS; else r=FAIL; fi
  echo "$v,$r" | tee -a "$OUT"
  cleanup_app app
done
