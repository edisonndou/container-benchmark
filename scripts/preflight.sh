#!/usr/bin/env bash
# Checks that the machine is ready for the benchmark, pre-pulls images, writes results/environment.md.
source "$(dirname "$0")/common.sh"
ok=1; pass() { printf '  [ OK ] %s\n' "$*"; }; fail() { printf '  [FAIL] %s\n' "$*"; ok=0; }; warn() { printf '  [WARN] %s\n' "$*"; }

echo "Checking tools"
for t in docker node npm autocannon syft trivy jq python3 curl shuf; do
  command -v "$t" >/dev/null && pass "$t" || fail "$t not installed (run scripts/setup.sh)"
done
docker info >/dev/null 2>&1 && pass "Docker daemon reachable" || fail "Docker daemon not reachable (is it running? are you in the docker group? open a NEW terminal)"
[ "$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)" -ge 22 ] && pass "Node >= 22" || fail "Node >= 22 required"

echo "Checking location and host"
case "$ROOT" in /mnt/*) fail "Repo is on the Windows disk ($ROOT). Move it into ~/ inside Linux, otherwise timings are distorted.";; *) pass "Repo is on the Linux filesystem";; esac
grep -qi microsoft /proc/version 2>/dev/null && warn "Running in WSL2: record this as a limitation in the paper."
[ "$(uname -m)" = x86_64 ] && pass "Architecture x86_64" || warn "Architecture $(uname -m): record it; results are not comparable with x86_64."
nproc_n=$(nproc); [ "$nproc_n" -ge 2 ] && pass "$nproc_n CPUs visible" || fail "Need >= 2 CPUs (app is limited to $CPUS, load generator needs its own)"
mem_mb=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo); [ "$mem_mb" -ge 3000 ] && pass "${mem_mb} MB RAM" || warn "${mem_mb} MB RAM is low"
load=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{exit !($load < 0.5)}" && pass "Idle machine (load $load)" || warn "Load average $load: close other programs"

if docker info >/dev/null 2>&1; then
  echo "Checking that container limits really work"
  docker run --rm --cpus="$CPUS" --memory="$MEMORY" hello-world >/dev/null 2>&1 && pass "docker run with --cpus/--memory" || fail "docker run with limits failed"
  mem=$(docker run --rm --memory="$MEMORY" "node:${NODE_VERSION}-alpine" node -e 'console.log(process.constrainedMemory?process.constrainedMemory()/1048576:0)' 2>/dev/null || echo 0)
  echo "  memory limit seen inside container: ${mem} MB (expected ~256)"
  echo "Pre-pulling base images"
  for i in "node:${NODE_VERSION}-bookworm-slim" "node:${NODE_VERSION}-alpine" "gcr.io/distroless/nodejs22-debian12:nonroot" "gcr.io/distroless/nodejs22-debian12:debug-nonroot"; do
    docker pull -q "$i" >/dev/null 2>&1 && pass "pulled $i" || fail "could not pull $i (check the tag / network)"
  done
fi
if bash "$ROOT/scripts/record_env.sh" >/dev/null 2>&1; then
  pass "wrote $RESULTS/environment.md (add 'wsl --version' and Windows version by hand if on WSL2)"
else
  fail "could not record the measurement environment in $RESULTS/environment.md"
fi
[ $ok -eq 1 ] && echo -e "\nREADY. Next: bash scripts/run_all.sh pilot" || { echo -e "\nNOT READY: fix the [FAIL] lines above."; exit 1; }
