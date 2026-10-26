#!/usr/bin/env bash
# One-time installer for Ubuntu/Debian (also works inside WSL2 Ubuntu).
# Installs: Docker Engine, Node.js 22, autocannon 8.0.0, Syft, Trivy, jq, python3, curl.
# Run once:  bash scripts/setup.sh      (it will ask for your sudo password)
set -euo pipefail
say() { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
command -v apt-get >/dev/null || { echo "This installer needs apt (Ubuntu/Debian)."; exit 1; }

say "Base packages"
sudo apt-get update -y
sudo apt-get install -y curl ca-certificates jq python3 git coreutils

if ! command -v docker >/dev/null; then
  say "Docker Engine (official convenience script from get.docker.com)"
  curl -fsSL https://get.docker.com | sudo sh
else say "Docker already installed: $(docker --version)"; fi

say "Allow your user to run docker without sudo"
sudo usermod -aG docker "$USER" || true

say "Start the Docker service"
if pidof systemd >/dev/null 2>&1; then sudo systemctl enable --now docker
else sudo service docker start || true; fi

if ! command -v node >/dev/null || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 22 ]; then
  say "Node.js 22 (NodeSource)"
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
else say "Node already installed: $(node -v)"; fi

say "autocannon 8.0.0"
sudo npm install -g autocannon@8.0.0

if ! command -v syft >/dev/null; then
  say "Syft"
  curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sudo sh -s -- -b /usr/local/bin
else say "Syft already installed"; fi

if ! command -v trivy >/dev/null; then
  say "Trivy"
  curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin
else say "Trivy already installed"; fi

say "Done. IMPORTANT: close this terminal and open a new one (or run: newgrp docker),"
say "then run: bash scripts/preflight.sh"
