# Security and Operability Trade-offs in Minimal Container Images

A controlled comparison of **Debian Slim, Alpine, and Distroless** running the same Node.js/Express application. This academic project belongs to **Operating System, Container and Platform Security** and evaluates software-inventory indicators, reported known vulnerabilities, functionality, diagnostic tools, image size, readiness, and behavior under load.

The repository includes source code, a pilot, a main experiment, raw evidence, and analysis. The [final technical audit](docs/FINAL_AUDIT.md) separates code inspection, historical execution evidence, independently recomputed results, and work that requires a new execution environment. File presence alone does not establish completion of the seminar requirements.

A subsequent [user-provided validation transcript](analysis/user-validation-2026-10-31/console.txt) confirms successful fresh builds, functional checks for all four variants, scans, and a complete three-repetition pilot with `issues: []`. These new validation results remain separate from the archived main study. See the audit's follow-up section for the evidence boundary.

## Authors and equal contribution

| Author | Student ID | Declared contribution |
|---|---|---|
| Edison Ndou | 260756200037 | One third |
| Donart Ajvazi | 260756200044 | One third |
| Bleron Baftiu | 260756200026 | One third |

**All three authors contributed equally, one third each**, across literature review, methodology, implementation, testing, evaluation, analysis, documentation, paper writing, and presentation preparation. This is the group's declaration, not a measurement inferred from commits or working hours. Historical records retain the identities of the people involved in individual recorded sessions. See [CONTRIBUTIONS.md](CONTRIBUTIONS.md) for the full declaration and AI disclosure.

## Research question and objectives

How does container-image choice affect security indicators, operability, and performance for the same web application under controlled conditions?

- Compare software inventories and reported findings while separating OS packages from application dependencies.
- Check the same functional contract across image variants.
- Measure local image size, launch-to-readiness time, throughput, latency, and CPU/memory usage.
- Document available diagnostic tools and recovery from configuration, permissions, and connectivity faults.
- Explain limitations without treating smaller inventories or fewer findings as proof of exploitability reduction or stronger isolation.

The original literature and methodology document is `docs/Faza1_Literatura_dhe_Metoda.docx`. The implemented operability assessment is narrower than its original plan: **no independent human diagnosis-time study was completed**.

## Repository structure

| Path | Purpose |
|---|---|
| `app/` | Express API, npm lockfile, fixture, and functional checks. |
| `stub/` | Local upstream HTTP service. |
| `docker/` | Four image definitions. |
| `scripts/` | Environment preparation, builds, scans, startup/load measurement, and fault scenarios. |
| `results/pilot/` | Archived pilot measurements and preparatory fault/recovery evidence. |
| `results/main/` | Archived main measurements, metadata, logs, SBOMs, and scan reports. |
| `results/operator_diagnostics/` | Original operator plan and the separately classified assisted orientation. |
| `analysis/` | Original analysis, tables, figures, report, and analysis scripts. |
| `analysis/audit-2026-10-31-reviewed/` | Authoritative new independent Node.js reanalysis of archived evidence. |
| `docs/` | Historical plans, guides, method records, and the final technical audit. |

Dated plans and original reports are retained for provenance. Use [FINAL_AUDIT.md](docs/FINAL_AUDIT.md) for the current code/evidence assessment.

## Architecture and API

```text
Host functional checks / Autocannon
                  |
          localhost:8080
                  |
       app container, port 3000
       Express + fixture file
                  |
          benchnet network
                  |
          stub:4000/ping
```

The application uses **Express 4.21.2**, a locked dependency tree, synthetic data, and no database. The upstream stub returns plain-text `pong`.

| Endpoint | Behavior |
|---|---|
| `GET /healthz` | JSON with `status: ok` and the configured application mode. |
| `GET /data` | Fixed dataset containing 200 items. |
| `GET /compute?seed=abc` | Performs 2,000 chained SHA-256 operations. |
| `GET /file` | Reads the configured fixture and returns its byte length and digest. |
| `GET /upstream` | Calls the configured local upstream service. |

All image definitions install production dependencies using `npm ci --omit=dev` from the same `app/` build context and lockfile. Debian/Alpine run as `node`; Distroless variants run as `nonroot`. The Distroless dependency stage uses Debian to match its glibc runtime. Alpine uses musl. Equal Node.js version strings do not isolate libc differences or runtime build differences. Native add-on and ARM compatibility were not established by this experiment.

## Historical experiment environment

The main run was recorded on **27 October 2026**. These are archived observations, not the requirements or observed versions of this audit machine.

| Item | Recorded value |
|---|---|
| Host | Windows with Ubuntu 26.04.1 LTS under WSL2, x86_64 |
| CPU | AMD Ryzen 5 5600H, 12 visible logical CPUs |
| WSL memory | Approximately 6.7 GiB; 2 GiB swap visible |
| Docker | Engine 29.9.2, overlayfs, cgroup v2 |
| Host Node.js | v22.22.1 |
| All four application images | Node.js v22.22.0 |
| Autocannon / Syft / Trivy | 8.0.0 / 1.55.0 / 0.76.1 |
| Measurement Python | 3.14.4 |
| Application resource limits | 1 CPU, 256 MiB |
| Main workload | `/compute`, 32 connections, 30 s warm-up, 60 s measurement |
| Repetitions | 10 startup and 10 load trials per primary image |

See [environment evidence](results/main/environment.md), [run settings](results/main/load/settings.txt), and [image identities](results/main/metadata/build_info.csv). The measurement commit was `f8d6bb95ec183bb5a26825f7833735df4bf61292`. This audit adds code corrections after those measurements; it does not replace their provenance.

## Reanalysis of existing evidence

This path reads saved files and does **not** build images, start containers, run API tests, or scan anything. Node.js 22 or newer is sufficient; no npm dependency installation is needed for the independent analyzer.

From the repository root:

```bash
node analysis/scripts/audit_archived_results.mjs --project . --out analysis/reanalysis-new
```

The output parent must exist and the output directory itself must be new. Outputs include performance/security summaries, per-run metrics, resource samples, variant-position frequencies, shared dependencies/findings, operability classifications, and an input SHA-256 manifest. The analyzer exits nonzero when a check fails, while retaining its report for review.

The audit on this Windows checkout recomputed all main results from 30 startup attempts, 30 load runs, and 3,600 resource samples: **185 checks passed and two exact-byte integrity checks failed**. All 186 affected prior input hashes match after explicit in-memory CRLF-to-LF normalization; no unexplained content mismatch was found. This is not byte-for-byte verification of the original archive. The database metadata similarly matches its recorded checksum only after newline normalization. Raw evidence was not rewritten to make checks pass.

Original Python analysis and figure regeneration remain available on a compatible Python environment with byte-faithful inputs:

```bash
python3 -m venv .venv-analysis
source .venv-analysis/bin/activate
python -m pip install -r analysis/requirements-analysis.txt
python analysis/scripts/analyze_results.py --project . --out analysis/regenerated-new
```

That script verifies the historical database metadata checksum exactly. It can stop on a checkout whose line endings have changed. Preserve the failure and use the original archive or a byte-faithful checkout rather than modifying evidence. The optional `--archive SOURCE.zip` argument adds source-archive provenance; the source ZIP is not included here. Python/figure regeneration was not executed during this audit because Python was unavailable.

## Requirements for a new replication

A new replication creates **new evidence**, separate from the archived study. Use an otherwise idle Linux x86_64 host or Ubuntu in WSL2 with Docker Engine, Bash, Node.js >=22, npm, Python 3, Autocannon 8.0.0, Syft, Trivy, jq, curl, and standard Linux tools. Internet access is needed for installation, base images, npm packages, and the initial scanner database.

Keep the working copy on the Linux filesystem, such as `~/container-benchmark`, rather than `/mnt/c`. Preflight rejects `/mnt/` paths. WSL2 is a documented limitation; it is not equivalent to native Linux.

For a fresh clone, disable Git's newline conversion to preserve indexed evidence bytes:

```bash
git -c core.autocrlf=false clone https://github.com/edisonndou/container-benchmark.git
cd container-benchmark
```

The audit corrections are local until separately committed and published. A clone of the remote will contain these corrections only after publication; otherwise use a copy of the audited working tree.

### Dependency installation

On Ubuntu/Debian, inspect and run the supplied installer once:

```bash
bash scripts/setup.sh
```

The installer uses apt, the Docker convenience installer, NodeSource when needed, global npm installation of Autocannon 8.0.0, and the Syft/Trivy installers. It requires sudo and downloads software. Close and reopen the terminal afterward to activate Docker group membership. These commands were checked against the script; installation was not repeated during this audit. Current installer defaults do not pin every tool to the historical version, so record the actual new versions.

### Isolate new results and the scanner cache

Before preflight or any experiment command, set **absolute paths** for a new workspace and cache:

```bash
export RESULTS_DIR="$PWD/replications/run-new"
export TRIVY_CACHE_DIR="$PWD/.cache/trivy-run-new"

# Both paths must be unused for the first run.
if [ -e "$RESULTS_DIR" ] || [ -e "$TRIVY_CACHE_DIR" ]; then
  echo "STOP: choose unused results and cache paths before proceeding."
else
  bash scripts/preflight.sh
fi
```

Use a different `run-new` identifier for every independent replication. Do not set these variables to the historical `results/` or historical `.cache/trivy` directory. Preflight must print `READY`; it checks tools, Docker access, resources and limits, pulls base images, and writes the environment into the selected results directory.

These variables isolate filesystem outputs. **Separate Git worktrees still share the Docker daemon**, `bench-*:latest` image tags, `app` and `stub` container names, `benchnet`, the `benchperm` volume, and potentially port 8080. Run one benchmark/diagnostic session at a time per daemon or use a separate daemon/VM. A different output directory alone does not isolate Docker resources.

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `RESULTS_DIR` | `<repo>/results` | Base directory for generated shared outputs and default run directories. Set it explicitly for a new replication. |
| `TRIVY_CACHE_DIR` | `<repo>/.cache/trivy` | Scanner database cache. Set a new path with a new results directory. |
| `NODE_VERSION` | `22.22.0` | Debian/Alpine tags, dependency stages, and stub image. Distroless uses its own tag. |
| `CPUS` | `1` | Application container CPU quota. |
| `MEMORY` | `256m` | Application container memory limit: 256 MiB. |
| `HOST_PORT` | `8080` | Published application port; container port remains 3000. |
| `CONNS` | `32` | Autocannon connections. |
| `ENDPOINT` | `/compute` | Load-test endpoint. |

The application reads these container environment variables:

| Variable | Contract |
|---|---|
| `APP_MODE` | Mandatory and nonempty; image default is `bench`. Missing/empty causes exit code 1. |
| `PORT` | Listening port; default `3000`. |
| `TEST_FILE` | Fixture path; default `/data/sample.txt`. |
| `UPSTREAM_URL` | Upstream endpoint; default `http://stub:4000/ping`. |

Host exports of application variables are not automatically passed into containers. The Dockerfiles set defaults; `run_app` accepts additional Docker arguments such as `-e APP_MODE=bench`. Freeze workload and resource settings after the pilot.

## Build images and validate functionality

With replication variables exported:

```bash
bash scripts/build.sh
bash scripts/functional.sh
cat "$RESULTS_DIR/functional.csv"
```

Builds use `app/` as their context and produce `bench-debian:latest`, `bench-alpine:latest`, `bench-distroless:latest`, and `bench-distroless-debug:latest`. Review actual image IDs and Node.js versions in `$RESULTS_DIR/build_info.csv`.

Expect `PASS` for all four variants. The functional script starts the stub and checks five endpoints. It records failures in the CSV but does not itself return a failing exit code; inspect the CSV. The pipeline also validates it explicitly. Startup errors can terminate the script before all variants are recorded.

For an already running application and stub:

```bash
node app/test.js http://localhost:8080
```

This standalone check returns a nonzero exit code on failure. It does not start services. No new API tests were executed during this audit; the four PASS records describe the historical run.

## Tool inventory and security scans

After building:

```bash
bash scripts/inspect_images.sh
bash scripts/scan.sh
```

The inventory exports container filesystems and checks selected tool paths, including shell and package-management commands. It is a path inventory, not proof that every listed tool executes correctly.

Syft writes `$RESULTS_DIR/sbom/`; Trivy writes `$RESULTS_DIR/trivy/`. A fresh results/cache pair downloads one database snapshot, records checksums and metadata, and verifies the database around each primary image scan with `--skip-db-update`. A cache database without a corresponding results manifest is refused to avoid replacing an untracked snapshot.

**A fresh clone does not contain the historical Trivy database.** If the selected results directory contains a manifest but its matching cache binary is absent, scanning stops with an explanation. Restore the exact historical snapshot for historical reproduction, or select new results/cache paths for a new scan. Never download a new database and label its findings as the historical findings.

The analysis key is `(VulnerabilityID, PkgName, InstalledVersion)`. It deduplicates within OS, project (`/app/node_modules/`), other-language, and unknown-path scopes, retains the highest severity for conflicting duplicates within a scope, and counts identities globally once. Scope totals can overlap in other datasets. These identities are not counts of unique CVEs. No conflicting duplicate severities were found in this archived dataset.

## Pilot and main experiments

Do not run these commands merely to inspect the repository. They rebuild shared Docker tags and create new measurements.

```bash
# Use the replication results/cache variables set above.
bash scripts/run_all.sh pilot "$RESULTS_DIR/pilot"

# Review the pilot before starting the main experiment.
bash scripts/run_all.sh main "$RESULTS_DIR/main"
```

| Mode | Repetitions per primary image | Warm-up | Measured interval |
|---|---|---|---|
| Pilot | 3 | 15 s | 20 s |
| Main | 10 | 30 s | 60 s |

Each run directory must be new. The pipeline builds, checks functionality, inventories tools, scans, records environment/settings/code changes, measures startup/load, and summarizes performance. Pilot and main can share the **new replication's** cache to use the same database snapshot. Builds/scans regenerate the selected replication's shared outputs; per-run metadata and security copies preserve each run's evidence.

Startup readiness requires HTTP 200 and JSON `status=ok`, without following redirects. Load warm-up and measured requests are separate. Logs, exit status, OOM/restart state, container inspection, and resource samples are retained. CPU and memory are averaged **within each run** before summarizing across runs. The run is the experimental repetition, not an individual resource sample.

The audited pipeline now refuses to write a completion timestamp if quality issues exist or expected successful trial counts are missing. This quality gate and filesystem-isolation controls were added after the historical measurements. Syntax checks and the user-provided fresh pilot transcript support the successful execution path; injected failure paths were not freshly exercised.

## Fault injection and recovery

Run diagnostics sequentially, outside a measurement session. The supported scenarios are `config`, `permissions`, and `connectivity`; primary variants are `debian`, `alpine`, and `distroless`.

```bash
variant=distroless
bash scripts/fault.sh config "$variant"
docker logs app
docker inspect app
```

For configuration or connectivity recovery, recreate the container with the image's correct defaults:

```bash
source scripts/common.sh
cleanup_app app
run_app "$variant" app -e APP_MODE=bench -e UPSTREAM_URL=http://stub:4000/ping
wait_ready
node app/test.js "http://localhost:$HOST_PORT"
cleanup_app app
```

For a permissions scenario, after injection and evidence capture, repair the volume with a helper container while leaving the application non-root:

```bash
source scripts/common.sh
docker run --rm -v benchperm:/d "node:${NODE_VERSION}-alpine" sh -c 'chmod 0644 /d/sample.txt'
node app/test.js "http://localhost:$HOST_PORT"
cleanup_app app
```

The automated preparatory script supports six Alpine/Distroless combinations and requires a new output directory:

```bash
bash scripts/validate_faults.sh "$RESULTS_DIR/diagnostics-new"
```

These commands run functional checks and are for a deliberately chosen new diagnostic session. The archived study contains three assisted manual Debian combinations, six automated Alpine/Distroless combinations, and Edison's separately classified assisted orientation. The originally planned independent Donart session did not take place. Do not report diagnosis times, blinded operators, or productivity comparisons.

## Main results independently recomputed from archived evidence

| Metric | Debian Slim | Alpine | Distroless |
|---|---:|---:|---:|
| Docker local image size, MB | 331.684087 | 234.609317 | 209.329755 |
| Median startup, ms | 501 | 540.5 | 557 |
| Median throughput, requests/s | 280.945 | 254.695 | 284.065 |
| Median per-run p99 latency, ms | 223.5 | 250 | 223.5 |
| Median run-mean CPU, % | 96.243 | 96.324 | 96.190 |
| Median run-mean memory, MiB | 31.278 | 29.817 | 32.601 |
| SBOM component records | 372 | 302 | 81 |
| OS finding identities | 290 | 73 | 71 |
| Project finding identities | 7 | 7 | 7 |
| Other-language finding identities | 51 | 51 | 0 |
| Unknown-path finding identities | 0 | 0 | 0 |
| Global finding identities | 348 | 131 | 78 |
| Unique application name-version pairs | 69 | 69 | 69 |

MB is decimal bytes / 1,000,000; MiB is bytes / 1,048,576. Docker-reported local image size is not compressed registry transfer size. Docker `stats` memory is not process RSS. The reported p99 is the median of ten per-run percentiles, not a global percentile over all requests. Quartiles use the inclusive method and are not confidence intervals. Failed-run evidence and outliers are not removed to improve summaries.

Distroless has the smallest recorded local image and fewest reported finding identities; all three share the same seven project findings. Debian has the lowest median startup time, Alpine the lowest median memory, and Distroless the highest median throughput in this particular dataset. These descriptive comparisons do not establish statistical significance or a universal ranking.

Random ordering did not balance load positions: Debian was first in 7/10 rounds, Alpine in 1/10, and Distroless in 2/10. Host state, sequence, libc, and runtime builds were not independently isolated as causes. All archived completed measured responses were HTTP 200, without reported transport errors, timeouts, OOM, or restarts.

## Paper, presentation, and LaTeX sources

The authors report that the final documentation and presentation are finished. At their instruction, those artifacts are outside this code-focused audit. No final IEEE paper, full LaTeX manuscript, presentation, or original professor's seminar plan was located in this repository copy; no paths or compliance checks are invented.

The selected written submission is the **7-page IEEE conference-format version**. A 10-page single-column professor-style version is supplementary and does not satisfy the stated 6–8-page IEEE requirement. Attach or link the actual final files separately when submitting.

Existing `analysis/Analiza_e_rezultateve.pdf` is an explanatory analysis report, not the final IEEE paper. `analysis/tables/ieee_tables.tex` contains table snippets, not a complete manuscript. Original analysis figures have English labels. Historical Albanian documents remain unchanged except for edits made earlier in this working session.

## Troubleshooting

| Symptom | Action |
|---|---|
| Docker socket permission denied | Reopen Ubuntu after installation or run `newgrp docker`; confirm your group membership. |
| Docker daemon unavailable | Start the intended Docker Engine with `sudo systemctl start docker` or the appropriate service command. Avoid mixing daemons between runs. |
| Preflight rejects `/mnt/c` | Copy the audited working tree into the Linux filesystem before measuring. |
| WSL uses Windows Node/npm | Check `command -v node npm autocannon` and `node -p process.platform`. Use Linux-installed tools; the platform should be `linux`. |
| Host port already allocated | Stop only the known conflicting service or export a free `HOST_PORT`; record the change consistently. |
| Trivy manifest exists but database is missing | Restore the exact snapshot, or choose a new `RESULTS_DIR` and `TRIVY_CACHE_DIR` for a new replication. |
| Output directory already exists | Choose a new path; preserve previous evidence. |
| Reanalysis exact hashes fail on Windows | Inspect CRLF conversion and compare with the original archive. A normalized-content match is not exact-byte verification. |
| Bash reports a carriage-return or `bash\r` error | Use a Linux checkout of the published audited revision with LF source endings. The new .gitattributes rules apply to source on checkout; do not blanket-convert archived evidence to repair a script. |
| Image tag/pull fails | Inspect registry access and tag availability; any change of runtime/image belongs to a new recorded replication. |

The measurement/fault scripts clean up the application container; the stub, network, and permissions volume can remain. Do not use broad Docker pruning commands on a shared daemon.

## Reproducibility limits and AI assistance

The original `trivy.db` binary and source ZIP are absent from this checkout, so their checksums cannot be independently reverified. The full original Windows build and WSL program version are not archived. A single JavaScript application, host, workload, and limited repetitions constrain generalization. Findings are scanner reports, not exploit demonstrations. Mutable image tags and unpinned installer defaults can change a new replication.

ChatGPT/Codex assisted with code/procedure preparation, interpretation, assisted recovery, analysis, documentation, and the current technical audit. The authors retain responsibility for checking correctness, sources, claims, reproducibility, and submission compliance. AI assistance is not an independent human operator study.

## Final submission checklist

- [x] Implementation, lockfile, image definitions, and execution instructions are present.
- [x] Pilot and main evidence are retained separately; main results were independently recomputed.
- [x] Authors, student IDs, equal contributions, limitations, and AI assistance are declared.
- [ ] Review the two exact-byte integrity failures and obtain byte-faithful source evidence if exact reproduction is required.
- [x] User-provided console evidence confirms fresh builds, four-variant functional success, scans, and a complete pilot with no quality issues; this does not certify every failure branch.
- [ ] Attach/link the authors' final 7-page IEEE PDF, LaTeX sources, and PDF/PPTX presentation; final-document compliance is outside this audit.
- [ ] Publish the intended repository revision or provide a ZIP containing these local corrections; verify recipient access.
- [ ] Confirm professor-specific acceptance of the reduced operator-study scope and other formal requirements.

The CTF is a separate course activity. This repository does not establish its completion. See [FINAL_AUDIT.md](docs/FINAL_AUDIT.md) for exact checks, findings, and remaining actions.
