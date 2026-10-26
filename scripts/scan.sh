#!/usr/bin/env bash
# Scan every variant against the same dedicated Trivy database.
source "$(dirname "$0")/common.sh"

CACHE="$ROOT/.cache/trivy"
MANIFEST="$RESULTS/trivy/DB_SHA256SUMS"

mkdir -p "$CACHE" "$RESULTS/sbom" "$RESULTS/trivy"

for tool in syft trivy sha256sum; do
  command -v "$tool" >/dev/null || {
    echo "Missing required tool: $tool" >&2
    exit 1
  }
done

# Initialize the snapshot only once.
if [ ! -f "$MANIFEST" ]; then
  trivy --cache-dir "$CACHE" image --download-db-only

  (
    cd "$CACHE/db"
    sha256sum trivy.db metadata.json
  ) > "$MANIFEST"

  cp "$CACHE/db/metadata.json" "$RESULTS/trivy/db_metadata.json"
  date -u +%FT%TZ > "$RESULTS/trivy/DB_FROZEN"
fi

check_db() {
  (
    cd "$CACHE/db"
    sha256sum --check "$MANIFEST"
  )
}

check_db

{
  syft version
  trivy --version
} > "$RESULTS/tool_versions.txt" 2>&1

for v in "${VARIANTS[@]}"; do
  check_db

  syft "$(img "$v")" -o json > "$RESULTS/sbom/$v.syft.json"

  trivy --cache-dir "$CACHE" image \
    --skip-db-update \
    --scanners vuln \
    --format json \
    --output "$RESULTS/trivy/$v.json" \
    "$(img "$v")"

  check_db
done

python3 "$ROOT/scripts/analyze_scan.py"
