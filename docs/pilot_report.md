# Pilot evaluation report

**Dates:** (from – to)  **Host:** (see results/environment.md)  **Commit:** (git rev-parse --short HEAD)

## 1. What the pilot was meant to check
Functionality, scripts, result collection, diagnostic scenarios (Phase 1 §5.5).

## 2. What was run
| Item | Value |
|---|---|
| Repetitions per image | 3 |
| Load | warm-up (s) / measurement (s) / connections / endpoint |
| Images and real Node.js versions | (from results/build_info.csv) |
| Trivy DB snapshot date | (results/trivy/DB_FROZEN) |
| Tool versions | (results/tool_versions.txt) |

## 3. Problems found and what was changed
| # | Problem | Evidence | Change made | Commit |
|---|---|---|---|---|
| 1 | | | | |

## 4. Pilot observations (not used as final results)
- Functional tests: (PASS/FAIL per image)
- Startup: (median and spread per image, any outliers)
- Load: (CPU saturated? errors? OOM? p50/p99)
- Security counts: (components and reported vulnerabilities per image; anything surprising)
- Diagnostics: (9 trials; success, time, steps, external help)

## 5. Parameters frozen for the main experiment
| Parameter | Final value | Reason |
|---|---|---|
| CPUS / MEMORY | | |
| Connections / endpoint | | |
| Warm-up / measurement time | | |
| Repetitions (main) | | |
| Readiness definition | docker run → first 200 on /healthz | |
| Node.js versions | | |
| Trivy DB snapshot | | |

## 6. Revised procedure (changes to Phase 1 §5)
(List each change to the method with a short reason, so the paper can say "after the pilot we changed X because Y".)

## 7. Limitations discovered
(host noise, WSL2/VM overhead, anything that limits interpretation)
