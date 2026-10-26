#!/usr/bin/env bash
# Usage: run_all.sh <pilot|main> [new_output_directory]
source "$(dirname "$0")/common.sh"

MODE="${1:?Usage: run_all.sh pilot|main [new_output_directory]}"

case "$MODE" in
  pilot) R=3; W=15; M=20 ;;
  main)  R=10; W=30; M=60 ;;
  *) echo "Mode must be pilot or main." >&2; exit 1 ;;
esac

OUTD="${2:-$RESULTS/$MODE}"
OUTD="$(realpath -m "$OUTD")"

if [ -e "$OUTD" ]; then
  echo "STOP: output path already exists: $OUTD" >&2
  echo "Choose a new directory; previous results will be preserved." >&2
  exit 1
fi

mkdir -p "$OUTD/metadata" "$OUTD/security"

{
  echo "MODE=$MODE"
  echo "REPS=$R"
  echo "WARMUP_SECONDS=$W"
  echo "MEASUREMENT_SECONDS=$M"
  echo "STARTED_UTC=$(date -u +%FT%TZ)"
  echo "COMMIT=$(git -C "$ROOT" rev-parse HEAD)"
} > "$OUTD/metadata/run.txt"

git -C "$ROOT" diff HEAD -- app docker scripts stub .gitignore \
  > "$OUTD/metadata/code_changes.patch"

bash "$ROOT/scripts/build.sh" 2>&1 | tee "$OUTD/build.log"
cp "$RESULTS/build_info.csv" "$OUTD/metadata/"

bash "$ROOT/scripts/functional.sh" 2>&1 | tee "$OUTD/functional.log"
cp "$RESULTS/functional.csv" "$OUTD/metadata/"

# functional.sh records failures but does not itself exit nonzero.
python3 - "$RESULTS/functional.csv" "${ALL_VARIANTS[@]}" <<'PY'
import csv
import sys

with open(sys.argv[1]) as stream:
    rows = list(csv.DictReader(stream))

expected = set(sys.argv[2:])
actual = {row["variant"] for row in rows}

if (
    actual != expected
    or len(rows) != len(expected)
    or any(row["result"] != "PASS" for row in rows)
):
    raise SystemExit("STOP: functional validation failed.")
PY

bash "$ROOT/scripts/inspect_images.sh" 2>&1 | tee "$OUTD/inventory.log"
cp "$RESULTS/tools_present.csv" "$OUTD/metadata/"

bash "$ROOT/scripts/scan.sh" 2>&1 | tee "$OUTD/scan.log"
cp -a "$RESULTS/sbom" "$RESULTS/trivy" "$OUTD/security/"
cp "$RESULTS/security_summary.csv" "$OUTD/security/"
cp "$RESULTS/project_findings_comparison.json" "$OUTD/security/"
cp "$RESULTS/tool_versions.txt" "$OUTD/metadata/"

bash "$ROOT/scripts/record_env.sh" > "$OUTD/environment.md"

bash "$ROOT/scripts/startup.sh" "$R" "$OUTD/startup.csv"
bash "$ROOT/scripts/load.sh" "$R" "$W" "$M" "$OUTD/load"
python3 "$ROOT/scripts/analyze_perf.py" "$OUTD"

date -u +%FT%TZ > "$OUTD/metadata/completed_utc.txt"
echo "Pipeline finished. Review perf_quality.json before accepting results."
echo "Results: $OUTD"
