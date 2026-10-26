#!/usr/bin/env bash
# Phase 2: writes results/environment.md with everything needed to describe the host in the paper.
source "$(dirname "$0")/common.sh"
mkdir -p "$RESULTS"; OUT="$RESULTS/environment.md"
v() { "$@" 2>&1 | head -n "${N:-1}" || true; }
{
echo "# Measurement environment"
echo "Recorded (UTC): $(date -u +%FT%TZ)"; echo "Recorded by: ${USER:-unknown}"; echo
echo "## Host"
echo '```'; uname -a; echo; (lsb_release -ds 2>/dev/null || grep PRETTY_NAME /etc/os-release); echo
lscpu | grep -E 'Model name|^CPU\(s\)|Thread|Core|Socket|MHz|Architecture'; echo
free -h; echo
echo "CPU governor: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo 'n/a (VM or no cpufreq)')"
echo "Virtualization: $(systemd-detect-virt 2>/dev/null || echo unknown)"
echo "On AC power: $(cat /sys/class/power_supply/AC*/online 2>/dev/null | head -1 || echo n/a)"
echo "Load average at record time: $(cut -d' ' -f1-3 /proc/loadavg)"
echo '```'; echo
echo "## Tools"
echo '```'
echo "docker:    $(docker version --format '{{.Server.Version}}' 2>/dev/null | head -1 || true)"; docker info >/dev/null 2>&1 || echo "WARNING: Docker daemon not reachable"
echo "storage:   $(docker info --format '{{.Driver}} / cgroup {{.CgroupVersion}} / {{.OperatingSystem}}' 2>&1 | head -1)"
echo "node:      $(node -v 2>&1)"
echo "autocannon: $(command -v autocannon >/dev/null && autocannon --version 2>&1 | head -1 || echo 'NOT INSTALLED')"
echo "syft:      $(command -v syft >/dev/null && syft version 2>&1 | grep -i '^Version' | head -1 || echo 'NOT INSTALLED')"
echo "trivy:     $(command -v trivy >/dev/null && trivy --version 2>&1 | head -1 || echo 'NOT INSTALLED')"
echo "python:    $(python3 --version 2>&1)"
echo '```'; echo
echo "## Fixed experiment settings (scripts/common.sh)"
echo '```'; echo "CPUS=$CPUS"; echo "MEMORY=$MEMORY"; echo "NODE_VERSION=$NODE_VERSION"; echo "HOST_PORT=$HOST_PORT"; echo '```'
} > "$OUT"
cat "$OUT"
