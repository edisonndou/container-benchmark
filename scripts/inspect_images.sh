#!/usr/bin/env bash
# Lists which tools exist inside each image by exporting its filesystem (works even without a shell).
source "$(dirname "$0")/common.sh"
mkdir -p "$RESULTS"
cid=""
trap 'if [ -n "$cid" ]; then docker rm "$cid" >/dev/null 2>&1 || true; fi' EXIT
OUT="$RESULTS/tools_present.csv"
TOOLS=(sh bash apt apt-get apk dpkg curl wget ps ls cat busybox)
{ echo -n "variant,files_total"; for t in "${TOOLS[@]}"; do echo -n ",$t"; done; echo; } > "$OUT"
for v in "${ALL_VARIANTS[@]}"; do
  cid=$(docker create "$(img "$v")")
  list=$(docker export "$cid" | tar -t 2>/dev/null)
  docker rm "$cid" >/dev/null
  cid=""
  row="$v,$(echo "$list" | wc -l)"
  for t in "${TOOLS[@]}"; do
    if grep -Eq "(^|/)(s?bin|busybox)/$t$" <<< "$list"; then row+=",yes"; else row+=",no"; fi
  done
  echo "$row" >> "$OUT"
done
cat "$OUT"
