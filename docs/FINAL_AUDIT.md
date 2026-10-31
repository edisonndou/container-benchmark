# Final Technical Audit

**Date:** 31 October 2026.
**Repository:** https://github.com/edisonndou/container-benchmark
**Audited HEAD:** `d5342fd275cbf0341427eb208c862f9501501cd2`, branch `main`.
**Measurement commit:** `f8d6bb95ec183bb5a26825f7833735df4bf61292`.

## Verdict and scope

The code implements the intended three-image benchmark, and independent reanalysis supports the archived main performance/security results. The code corrections in this audit have passed the available shell/JavaScript syntax checks, but **fresh Docker execution has not been validated**. Two exact-byte integrity checks fail in this Windows checkout; all affected historical inputs match their recorded hashes after explicit in-memory newline normalization.

The latest user instruction excludes work on the finished paper, presentation, and final documents. This report therefore focuses on source code, measurement logic, archived evidence, and execution documentation. It does not certify final-document compliance or declare the seminar submission 100% complete. The original professor's seminar plan was not located, so the requirements below are assessed against the supplied requirement list and the repository's method records, not authenticated professor instructions.

Statuses mean: **VERIFIED** = supported within the stated inspection/reanalysis scope; **PARTIAL** = evidence or execution coverage is incomplete; **MISSING** = required evidence is absent from this copy; **NOT APPLICABLE** = outside the narrowed audit scope. A VERIFIED archived outcome does not mean the underlying experiment was rerun.

## Working-tree provenance

The tree was already dirty before this audit. These existing changes were identified and preserved:

```text
 M CONTRIBUTIONS.md
 M README.md
 M analysis/README.md
 M docs/Plani_deri_1_nentor.md
 M docs/Plani_pas_miratimit.md
 M docs/Plani_pilot.md
 M docs/pilot_report.md
 M docs/proposal.md
 M results/operator_diagnostics/README.txt
?? docs/PROJECT_STATUS.md
```

No benchmark-source changes were present initially. README and contributions were subsequently revised under the new explicit attribution instructions. The earlier completion note was marked superseded and its contribution row corrected. Existing paper/report binaries, historical operator identities, raw result data, original analysis tables/figures, and scanner evidence were not rewritten. No commit, push, merge, tag, or deployment was performed.

The authoritative new reanalysis output is [`analysis/audit-2026-10-31-reviewed/`](../analysis/audit-2026-10-31-reviewed/). Its `audit.json` records the audited HEAD, actual Node version, per-check outcomes, working-tree state at execution, and current input hashes. Earlier `audit-2026-10-31/` and `audit-2026-10-31-final/` directories are retained as intermediate audit attempts. During the intermediate attempt, temporary Git attribute rules made some unchanged evidence files appear dirty to Git; those rules were removed. No raw input bytes were changed by those rules. The reviewed run records the corrected working-tree classification.

## Requirement-to-evidence matrix

| Requirement | Status | Evidence and boundary |
|---|---|---|
| Focused question, literature, justified gap | PARTIAL | Research questions and `docs/Faza1_Literatura_dhe_Metoda.docx` exist. The final literature/gap argument and professor's requirements are outside the narrowed review or unavailable. |
| Technical implementation and defined method | VERIFIED | `app/server.js`, lockfile, four Dockerfiles, shared settings, and measurement scripts inspected. Verification is static plus archived evidence, not fresh execution. |
| Pilot before main experiment | VERIFIED | Pilot completed `2026-10-26T22:48:39Z`; main began `2026-10-27T09:08:59Z`. Separate pilot/main metadata and results exist. |
| Results, interpretation, limitations | VERIFIED | Main raw inputs independently recomputed; original analysis and English figure captions distinguish descriptive results and limitations. Final paper claims were not checked. |
| 6–8-page IEEE PDF / selected 7-page version | NOT APPLICABLE | User excluded final documents. No final IEEE PDF or full LaTeX manuscript was located in this repository copy; their compliance is not certified. The 10-page single-column variant must remain supplementary. |
| PDF/PPTX presentation | NOT APPLICABLE | User reports it complete and excludes it from this work. No final presentation was located in the repository copy. |
| Source and technical material | VERIFIED | Application, Dockerfiles, scripts, raw records, metadata, analysis, and dependency lockfile are present locally. |
| Final repository link or ZIP submission | PARTIAL | A GitHub remote is configured. Current changes are local; publication, recipient access, and formal submission are not verified. |
| README environment/configuration/execution | VERIFIED | Root README now separates archived reanalysis from new replication and describes actual interfaces and limits. Installation/Docker examples are statically verified, not newly executed. |
| All authors and contributions | VERIFIED | README and CONTRIBUTIONS contain exact supplied names/IDs, shared one-third declaration, and AI disclosure. This verifies the declaration, not individual hours or percentages. |
| Same Express application/dependencies | VERIFIED | Express 4.21.2 agrees across manifest/lockfile. Same `app/` context and lockfile used by all Dockerfiles. Archived SBOMs contain the same 69 application name-version pairs. |
| Mandatory APP_MODE and five endpoints | VERIFIED | `app/server.js:10` and endpoint handlers inspected; archived functional results contain four PASS records. |
| 2,000 chained SHA-256 operations | VERIFIED | `app/server.js:35–40` inspected; application behavior was not freshly exercised. |
| Separate local upstream service | VERIFIED | `stub/stub.js`, network/stub setup in `scripts/common.sh`, and archived /upstream functional evidence. |
| Non-root and runtime controls | VERIFIED | Dockerfile USER declarations plus all 30 measured container inspection records: `node`/`nonroot`, 1 CPU, 268435456-byte memory limit. All four recorded Node runtimes are v22.22.0. |
| Main workload/counts | VERIFIED | 30 unique startup attempts, 30 load trials, /compute, 32 connections, 30-second warm-up setting, approximately 60-second measured reports. |
| Run-level resource aggregation | VERIFIED | Both analysis implementations aggregate 120 samples per run before cross-run summaries; 3,600 samples total. |
| Fresh operation of corrected scripts | PARTIAL | Shell syntax passes. New orchestration/cache paths and Python snippets have not been executed in Linux/Docker. |
| Historical Trivy database binary | MISSING | `.cache/trivy/db/trivy.db` is absent. Its original checksum cannot be independently verified. |
| Nine fault/recovery combinations | VERIFIED | Three assisted manual Debian and six automated Alpine/Distroless combinations independently checked against archived before/after records and successful recovery logs. |
| Independent human diagnosis-time study | MISSING | Original method proposed an independent operator. Session records show zero independent timed trials. This remains a deviation from the original plan, not a completed experiment. |
| CTF course activity | NOT APPLICABLE | Separate course activity; no completion claim follows from this repository. |

The missing independent operator study is a research-scope limitation and potential course-requirement issue. It is not an application implementation blocker. Only the instructor can confirm acceptance of the reduced assessment if the original requirement was mandatory.

## Implementation and trust boundaries

The project is a small synthetic benchmark, not a production service. Express serves a fixed dataset, CPU hashing, file reads, and a configured HTTP upstream. The fixture path and upstream URL come from environment configuration, not request-supplied paths or URLs. Docker scripts provide the build, network, resource quotas, and local measurement workflow. There is no database or production authentication layer to assess.

The direct application structure is proportionate to its purpose; introducing repository/service/interface layers would not improve the experiment. Shared execution behavior has one owner in `scripts/common.sh`. Scanner classification and performance aggregation are separate analysis responsibilities.

All image definitions use the same package files and `npm ci --omit=dev`, exclude development dependencies, copy the same application/fixture, and use a non-root runtime user. Distroless dependencies are built on Debian/glibc; Alpine uses musl. Runtime-build and libc differences were not independently isolated. No native add-on, ARM, exploitation, isolation-strength, or production-readiness claim is established here. Dependencies were not upgraded during the audit because that would change the measured treatment; recorded findings remain historical scanner observations rather than a current advisory assessment.

## Measurement-script review

| Concern | Status | Observation |
|---|---|---|
| Startup/load numeric arguments | VERIFIED | `startup.sh` and `load.sh` reject non-positive integer counts/durations/connections. Docker validates resource arguments. |
| Fault arguments | VERIFIED | Corrected to validate arity, scenario, and variant before network setup or removing `app`. |
| Readiness | VERIFIED | Host-side Python requires HTTP 200 and JSON object with `status=ok`, rejects redirects, and has an overall deadline. |
| Warm-up separation | VERIFIED | `load.sh` invokes Autocannon separately for warm-up and measured JSON output. Archived measured reports confirm duration/profile; this does not independently prove every instant of warm-up. |
| Error and failure preservation | VERIFIED | Load runner records start/readiness/warm-up/Autocannon statuses and retains logs/inspect/state evidence. Existing functional-runner caveat is documented below. |
| Cleanup | PARTIAL | Startup/load have cleanup traps; load stops/waits for its sampler. Inventory now cleans exported containers on failure. The functional runner still lacks an EXIT trap. |
| OOM/restart checks | VERIFIED | Raw inspect/state records independently agree; analyzer flags abnormal states. No historical OOM/restart evidence was observed. |
| Resource parsing | VERIFIED | ANSI escape sequences and blank lines removed in memory; unit parsing checked; all 3,600 samples finite. |
| Aggregation/outliers | VERIFIED | Run means precede cross-run medians/quartiles; ten trials per metric; archived min/max and all outliers retained. |
| Order | VERIFIED | Each round is randomized using shuf; actual saved sequence is not position-balanced. |
| Output protection | PARTIAL | Per-run directories/startup/load refuse existing destinations. Original Python reanalysis now exclusively creates new output. Shared outputs in the selected RESULTS_DIR are intentionally regenerated. |
| Completion semantics | VERIFIED statically | New gate requires empty quality issues and expected successful counts before writing completed_utc.txt. A fresh execution check is still required. |

### Actual variant positions

Counts in first / second / third position over ten rounds:

| Variant | Startup positions | Load positions |
|---|---|---|
| Debian Slim | 1 / 4 / 5 | 7 / 1 / 2 |
| Alpine | 5 / 4 / 1 | 1 / 4 / 5 |
| Distroless | 4 / 2 / 4 | 2 / 5 / 3 |

This limits causal interpretation. There was no balanced Latin-square design. No measurements were reordered or removed to compensate.

## Independently recomputed results

The new standard-library Node analyzer is separate from the original Python calculation. It checks raw records, expected configurations, successful HTTP status evidence, image identities, resource state, per-run aggregation, and archived summary agreement.

All 27 performance metric/variant summaries agree with archived medians, inclusive quartiles, minima, and maxima within the archive's 0.000501 rounding tolerance. CPU/memory sample means are computed within each run. The median per-run p99 is not a pooled percentile of individual requests. No significance or causal conclusion is inferred.

| Metric | Debian Slim | Alpine | Distroless |
|---|---:|---:|---:|
| Docker local size, decimal MB | 331.684087 | 234.609317 | 209.329755 |
| Median startup, ms | 501 | 540.5 | 557 |
| Median throughput, requests/s | 280.945 | 254.695 | 284.065 |
| Median per-run p99, ms | 223.5 | 250 | 223.5 |
| Median run-mean memory, MiB | 31.278 | 29.817 | 32.601 |
| SBOM records | 372 | 302 | 81 |
| OS finding identities | 290 | 73 | 71 |
| Project finding identities | 7 | 7 | 7 |
| Other-language identities | 51 | 51 | 0 |
| Global finding identities | 348 | 131 | 78 |

No discrepancy was found against the comparison table supplied in the audit request. Docker image size is local uncompressed accounting, not registry transfer size. Docker stats memory is not process RSS. The resource samples are not independent experimental repetitions.

### Security identity and provenance

Both implementations use `(VulnerabilityID, PkgName, InstalledVersion)`, deduplicate within each scope, and count global identities once. Within-scope conflicting severity duplicates retain the highest known severity. The independent pass found zero such conflicts in this dataset. Unknown-path scope totals are zero. Scope totals happen to sum to the global totals here, but are not guaranteed to do so for other inputs.

All three application package sets contain exactly the same 69 name-version pairs. All three project-finding sets contain the same seven identities. These are not seven unique CVEs by definition, and no exploitation was demonstrated.

SBOM configuration digests verify, and SBOM/Trivy uncompressed layer identities agree. The scan reports refer to the measured image IDs. Pilot/main checksum manifests agree byte for byte; original scan logs record database checks around the scans. Because the binary is absent, same-database execution is supported by the archived logs/manifests rather than a fresh verification of the original binary.

### Integrity findings

The reviewed audit has **185 VERIFIED checks and two FAILED exact-byte checks**, exits with code 1, and retains all reports. The failed labels are:

1. Archived database metadata hash matches manifest exactly.
2. All inputs in the previous analysis audit retain their recorded SHA-256 hashes.

There are **186 byte-mismatching prior input files**, with **zero mismatches unexplained by CRLF-to-LF normalization**. Git's system configuration has `core.autocrlf=true`. Normalization was performed only in memory for a separate content comparison; the raw inputs and their new current-byte hashes were preserved. The metadata's current-byte checksum is `bf44fb6e0b7b6939aa4f9634a884cda0ba7b0d4cd30a7d1235d1240c1944e4f7`; after explicit LF normalization it is the recorded `dc51323bb04f9433a394def2cbcf3f1c8beead09198587bbb34bade74c5d2b51`.

This is evidence of a line-ending transformation, not proof of original archive byte identity. The source ZIP and original trivy.db were unavailable. No raw record was changed to match an expected result. All inputs read by the new analyzer were rehashed before completion and remained unchanged during its execution.

## Findings and corrections

### CB-01 — Medium: new scans lacked safe independent output/cache selection — corrected in code

**Locations:** `scripts/common.sh:5`, `scripts/scan.sh:5–29`, `scripts/analyze_scan.py:19–23`.
**Evidence/impact:** Previously all shared outputs and scanner cache were fixed to historical paths. A clone includes a checksum manifest without its cache binary; separate run directories did not isolate intermediate build/scan outputs. Reusing a cache without a matching manifest could download into an existing untracked snapshot.
**Correction:** Added RESULTS_DIR and TRIVY_CACHE_DIR selection; scan analysis receives the chosen results path; missing snapshots and untracked existing DB directories produce explicit failures. README uses fresh paths.
**Verification:** Bash syntax and static data flow passed. Python change inspected; no Python interpreter available. No scan was executed. **Confidence: high** for the static issue; runtime remediation still requires isolated validation. **Effort: small, implemented.**

### CB-02 — Medium: pipeline could record completion despite performance quality issues — corrected in code

**Locations:** `scripts/run_all.sh` performance quality gate and `scripts/analyze_perf.py` report validation.
**Evidence/impact:** analyze_perf.py writes issues/counts but does not fail the process for every quality issue. The original pipeline then wrote a completion timestamp. Missing/failed trials could therefore reach that marker.
**Correction:** Require empty issues and exact successful per-variant counts before the completion timestamp. The analyzer also requires positive completed request counts, matching 2xx counts, and HTTP 200 status evidence; a successful command alone is insufficient. Failure retains all existing evidence.
**Verification:** Shell syntax passed; embedded Python inspected but not executed. Historical results were produced before this gate; independent reanalysis still confirms their successful counts. **Confidence: high. Effort: small, implemented.**

### CB-03 — Low: fault input errors could mutate the active session — corrected in code

**Location:** `scripts/fault.sh:5–18`.
**Evidence/impact:** Network setup and cleanup previously occurred before scenario/variant validation. A mistyped request could remove the current `app` container.
**Correction:** Validate argument count, scenario, and variant before Docker mutations. **Verification:** Bash syntax/static control flow only; no fault run. **Confidence: high. Effort: small, implemented.**

### CB-04 — Low: inventory failure could leave a temporary container — corrected in code

**Location:** `scripts/inspect_images.sh:4–6` and the export/removal loop.
**Evidence/impact:** An export/tar failure under set -e could exit before docker rm.
**Correction:** Add an EXIT cleanup trap and ensure the selected output directory exists. **Verification:** Bash syntax/static lifecycle review only. **Confidence: high. Effort: small, implemented.**

### CB-05 — Medium: original reanalysis could overwrite prior generated analysis — corrected in code

**Location:** `analysis/scripts/analyze_results.py:39–47`.
**Evidence/impact:** Existing output subdirectories were accepted with exist_ok=True; tables and figures could be replaced.
**Correction:** Reject existing output, reject an output containing the project, and exclusively create the new directory before its subdirectories. The independent Node analyzer also requires a new output. **Verification:** Python change statically inspected; not executed. Node analyzer executed into new directories. **Confidence: high. Effort: small, implemented.**

### CB-06 — Medium: historical byte lineage is incomplete — unresolved evidence limitation

**Locations:** `results/main/security/trivy/DB_SHA256SUMS`, `db_metadata.json`, and `analysis/audit-2026-10-31-reviewed/audit.json`.
**Evidence/impact:** Historical DB binary/source ZIP absent; 186 historical input bytes differ from the stored audit hashes because of line endings. Content comparisons pass after explicit normalization, but exact original bytes cannot be certified.
**Action:** Obtain original byte-faithful evidence/snapshot if exact reproduction is required; preserve current records and disclose the distinction. A fresh database cannot repair historical provenance. **Confidence: high. Effort: external artifact recovery.**

### CB-07 — Medium: independent operator evaluation was not completed — unresolved research limitation

**Locations:** `docs/Faza1_Literatura_dhe_Metoda.docx`, `results/operator_diagnostics/session_status.json`, `operator_profile.json`, `original_planned_operator_profile.json`, `trials/trial01/classification.json`.
**Evidence/impact:** The original method proposed an independent diagnostician; actual records describe nine preparatory combinations and Edison's assisted orientation, with zero independent timed trials.
**Action:** Keep all timing/productivity claims excluded. Obtain course acceptance of the narrower scope if required, or conduct a separately authorized new study with real participants. Do not change historical identities or label the orientation as independent. **Confidence: high. Effort: external decision/new experiment.**

### CB-08 — Low: standalone functional runner has limited failure/cleanup behavior — documented, unchanged

**Location:** `scripts/functional.sh:4–10`.
**Evidence/impact:** A recorded endpoint FAIL does not itself yield a failing shell exit status; abrupt startup failures can leave partial CSV/containers because there is no EXIT trap. The pipeline validates the CSV, but callers of this standalone script must inspect it.
**Action:** README documents this. Existing test sources and the test runner were left unchanged under the user's standing restriction on modifying tests without an explicit test-work request. A dedicated runner correction and validation can be authorized separately. **Confidence: high. Effort: small.**

### CB-09 — Informational: filesystem separation does not isolate Docker resources — documented constraint

**Locations:** `scripts/common.sh`, `scripts/fault.sh`, README replication section.
**Evidence/impact:** Tags, container names, network, permissions volume, and default port are shared by Git worktrees using the same daemon. Concurrent runs can interfere.
**Action:** Serialize runs or use a separate daemon/VM; distinct results/cache paths do not solve daemon-level conflicts. **Confidence: high. Effort: operating procedure.**

### CB-10 — Informational: new execution environment unavailable — unresolved validation coverage

**Evidence:** Node v22.17.0 and Git Bash are available. Python/python3/py and Docker were not found on PATH. `wsl --list --quiet` returned `Wsl/EnumerateDistros/Service/E_ACCESSDENIED`.
**Impact/action:** New container builds, endpoint checks, scanner execution, and Python compilation were not performed. This is an environment/authorization boundary, not evidence of an application failure. Validate the changed paths on an isolated Linux/Docker host when explicitly authorized. **Confidence: high.**

The preliminary lead/exclusive-role attribution was also corrected to the group's explicit equal one-third declaration. This is an attribution correction, not a measured redistribution of historical effort.

Preflight was also corrected to mark environment-recording failure as FAIL instead of allowing READY after that step failed. Its message now reports the selected output path. Shell syntax was checked; the actual recording step was not executed.

## Checks actually executed

| Check | Outcome | Environment / exit status |
|---|---|---|
| git status, rev-parse HEAD, branch, file inventory, targeted source reads | VERIFIED | Windows PowerShell; dirty tree and commit recorded. No hooks or application code executed. |
| Node syntax: app/server.js, app/test.js, stub/stub.js, audit_archived_results.mjs | PASSED | Node v22.17.0, `node --check`; no API tests executed. |
| All scripts/*.sh syntax | PASSED | Git Bash, `bash -n`; no Docker commands or embedded Python executed. |
| Independent archived reanalysis, first attempt | FAILED integrity checks | Node; exit 1; 183 checks passed / 2 failed before normalized-content diagnostics were added. Original failure preserved. |
| Independent archived reanalysis, reviewed attempt | PARTIAL | Node; exit 1; 185 passed / 2 exact-byte failures. 30 startup, 30 load, 3,600 samples; metrics/security agree. |
| Hash diagnosis | VERIFIED | All 186 old hash mismatches explained by in-memory CRLF-to-LF normalization; zero unexplained content mismatches. |
| Current-input hashes before/after reanalysis | PASSED | Raw inputs unchanged during independent computation. |
| Closeout consistency scan | PASSED | 190 current input hashes unchanged; 25 local links resolve; 39 README result values match recomputation; supplied author names/IDs match in both declarations. See closeout_validation.json in the reviewed audit directory. |
| git diff --check | PASSED | No whitespace errors in the tracked diff; Git reports line-ending conversion notices. |
| WSL enumeration | BLOCKED / ENVIRONMENT FAILURE | E_ACCESSDENIED; no experiments attempted through WSL. |
| Python syntax/compilation and original Python/figure regeneration | NOT RUN | Python interpreter unavailable on PATH. Static inspection is not compilation. |
| Build, installer, preflight, functional suite, fault execution, scans, run_all | NOT RUN | Not part of authorized fresh test execution; no shared image tags/cache/raw evidence overwritten. |
| Final paper/presentation/course-submission inspection | NOT APPLICABLE | Excluded by latest user instruction; no compliance verdict invented. |

The shell command used for the syntax sweep enumerates scripts and invokes `C:/Program Files/Git/bin/bash.exe -n` on each. Reanalysis command:

```text
node analysis/scripts/audit_archived_results.mjs --project . --out analysis/audit-2026-10-31-reviewed
```

Supporting outputs are preserved even when the command exits nonzero. An exploratory inline Node hash command initially failed because PowerShell stripped its quotes; the same read-only calculation was corrected using stdin and succeeded. No project behavior is inferred from that tooling error.

## Changed files in this audit

- `.gitattributes`: enforce LF for shell/Python/module source; raw evidence rules were not retained.
- `scripts/common.sh`: configurable results base.
- `scripts/scan.sh`: configurable cache, snapshot safeguards, selected analysis destination.
- `scripts/analyze_scan.py`: optional explicit results-directory argument.
- `scripts/run_all.sh`: record selected paths and gate completion on quality/counts.
- `scripts/fault.sh`: validate before Docker mutations.
- `scripts/inspect_images.sh`: cleanup trap and output-parent creation.
- `scripts/preflight.sh`: report the selected destination and fail readiness if environment recording fails.
- `scripts/analyze_perf.py`: require actual successful HTTP-response evidence in quality checks without changing the summary calculations.
- `analysis/scripts/analyze_results.py`: protect prior output directories.
- `analysis/scripts/audit_archived_results.mjs`: new independent read-only analyzer.
- `README.md`, `CONTRIBUTIONS.md`: current execution guide and confirmed equal contribution declaration.
- `docs/PROJECT_STATUS.md`: mark earlier note superseded and correct contribution row.
- `docs/FINAL_AUDIT.md`: this report.
- `analysis/audit-2026-10-31*/`: new generated audit/reanalysis outputs; historical directories remain intact.

Changes to other historical notes listed in the initial dirty tree predate this audit and were preserved. The original `analysis/README.md`, report PDF, tables/figures, raw measurements, and operator identities were not revised during the code-focused audit.

## Remaining actions and readiness

1. **Code execution coverage:** If fresh assurance is required, explicitly authorize validation of the changed scan/orchestration/fault paths on an isolated Linux/Docker environment. Bash syntax does not validate embedded Python or Docker behavior.
2. **Standalone functional runner:** Its exit/cleanup caveat remains documented; modifying/testing the test runner requires separate explicit test-work authorization under the standing preference.
3. **Historical reproducibility:** Recover the original ZIP and matching Trivy database when exact-byte/scan reproduction is required. Preserve and disclose the existing newline mismatch rather than rewriting it away.
4. **Research scope:** Keep independent diagnosis time and operator productivity outside the reported results. Instructor acceptance of that scope is a formal matter, not something code can establish.
5. **Delivery:** Review the local diff and separately authorize any commit/push or package handoff. Confirm the intended revision or ZIP and access rights at submission time.
6. **Final documents:** The authors' finished 7-page IEEE paper, source, and presentation remain their external submission artifacts. Their format, references, links, IDs, and final consistency have not been certified here at the user's request. Do not substitute the analysis PDF or a 10-page single-column variant for the stated IEEE submission.

**Readiness conclusion:** Source corrections and independently recomputed historical results are available for review. Full fresh execution and formal submission readiness are not verified. No absolute correctness or 100%-completion claim is made.
