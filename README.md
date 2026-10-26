# Container image benchmark: Debian Slim vs Alpine vs Distroless

Controlled comparison of three container base images running the same Node.js API.
Course: Information Security (seminar project). Domain: operating-system, container and platform security.

## Layout
- `app/` — Express API (`/healthz`, `/data`, `/compute`, `/file`, `/upstream`) and `test.js` functional test
- `stub/` — local test service used by `/upstream`
- `docker/` — one Dockerfile per variant (`distroless-debug` is reported separately)
- `scripts/` — build, scan (Syft/Trivy), startup, load, fault injection, analysis
- `results/` — generated CSV/JSON (pilot and main kept apart)
- `docs/RUNBOOK.md` — step-by-step run instructions (Albanian); `docs/UDHEZUES_FAZAT_2-10.md` — phase guide

## Quick start
```bash
bash scripts/setup.sh      # once, then open a new terminal
bash scripts/preflight.sh  # must print READY
bash scripts/run_all.sh pilot
```
Full step-by-step instructions: `docs/RUNBOOK.md`.

## Requirements
Linux host (or Linux VM), Docker Engine, Node.js >= 22 (host, for `app/test.js`), Python 3,
`npm i -g autocannon@8.0.0`, [Syft](https://github.com/anchore/syft), [Trivy](https://trivy.dev).

## Run
```bash
scripts/run_all.sh pilot   # 3 repetitions, short load
scripts/run_all.sh main    # 10 repetitions, 30 s warm-up + 60 s measurement
```
Fixed settings (CPU/RAM, Node version, port) are in `scripts/common.sh`.
Diagnostics: `scripts/fault.sh <config|permissions|connectivity> <variant>`, record in `scripts/diagnosis_log_template.csv`.

## Safety
Everything runs locally in containers with synthetic data; no third-party systems are scanned.

## Contributions
See `CONTRIBUTIONS.md` (to be filled in by the group).
