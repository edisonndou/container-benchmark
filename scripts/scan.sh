#!/usr/bin/env bash
# Phase 4/6: SBOM (Syft) + vulnerabilities (Trivy) for each variant, using ONE frozen Trivy DB.
# Install: https://github.com/anchore/syft  and  https://trivy.dev/docs/latest/getting-started/installation/
source "$(dirname "$0")/common.sh"
mkdir -p "$RESULTS/sbom" "$RESULTS/trivy"
command -v syft >/dev/null && command -v trivy >/dev/null || { echo "install syft and trivy first"; exit 1; }

# Download the DB once; later runs reuse it so every image is scanned against the same snapshot.
if [ ! -f "$RESULTS/trivy/DB_FROZEN" ]; then
  trivy image --download-db-only
  date -u +%FT%TZ > "$RESULTS/trivy/DB_FROZEN"
fi
{ syft version; trivy version --format json; } > "$RESULTS/tool_versions.txt" 2>&1

for v in "${VARIANTS[@]}"; do
  syft "$(img "$v")" -o json > "$RESULTS/sbom/$v.syft.json"
  trivy image --skip-db-update --scanners vuln --format json --output "$RESULTS/trivy/$v.json" "$(img "$v")"
done
python3 "$ROOT/scripts/analyze_scan.py"
