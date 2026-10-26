#!/usr/bin/env bash
# Phase 3: build all images with the same context, record IDs, sizes and runtime versions.
source "$(dirname "$0")/common.sh"
mkdir -p "$RESULTS"
OUT="$RESULTS/build_info.csv"
echo "variant,image_id,size_bytes,node_version_in_image,built_at_utc" > "$OUT"
for v in "${ALL_VARIANTS[@]}"; do
  docker build --build-arg NODE_VERSION="$NODE_VERSION" -f "$ROOT/docker/Dockerfile.$v" -t "$(img "$v")" "$ROOT/app"
  id=$(docker image inspect "$(img "$v")" --format '{{.Id}}')
  size=$(docker image inspect "$(img "$v")" --format '{{.Size}}')
  nv=$(docker run --rm --entrypoint "" "$(img "$v")" node -v 2>/dev/null || docker run --rm "$(img "$v")" -e 'console.log(process.version)')
  echo "$v,$id,$size,$nv,$(date -u +%FT%TZ)" >> "$OUT"
done
cat "$OUT"
