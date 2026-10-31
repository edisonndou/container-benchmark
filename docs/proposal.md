# Project Proposal and Method Outline

> Historical proposal outline, retained for provenance. The prompts below are
> planning notes, not the current completion checklist. The implemented method
> and evidence are described in [PROJECT_STATUS.md](PROJECT_STATUS.md),
> [operability_assessment.md](operability_assessment.md), and the
> [analysis guide](../analysis/README.md). The user has confirmed that the final
> documentation and presentation are complete; those deliverables were not
> inspected during this repository closeout.

**Title:** Security and Operability Trade-offs in Minimal Container Images: A Controlled Comparison of Debian Slim, Alpine and Distroless
**Group:** Bleron Baftiu, Donart Ajvazi, Edison Ndou  
**Domain:** Operating-system, container and platform security

## 1. Security problem and why it matters
(What risk do oversized base images create; why minimal images are adopted; what trade-off is unclear.)

## 2. Literature-supported research gap
(From Phase 1 §2–3: debloating studies and scanner-quality studies; what is not covered: controlled comparison of three popular base-image families linking security indicators to debugging effort. State as an intended contribution, not as proof of absence.)

## 3. Research questions
- **Main:** How does the choice between Debian Slim, Alpine and Distroless affect security indicators and operability of the same web application?
- **RQ1:** How do identified components and reported known vulnerabilities differ?
- **RQ2:** Is functionality preserved, and what steps and tools are needed to diagnose identical problems?
- **RQ3:** What differences appear in size, time-to-ready and behaviour under load?

## 4. Planned implementation
(Node.js API with 5 endpoints; three Dockerfiles; scripts for build, SBOM/scan, startup, load, fault injection; analysis scripts. Link to repo folders.)

## 5. Baseline / comparison condition
(Debian Slim is the reference; Alpine and Distroless are compared against it. Distroless debug variant reported separately.)

## 6. Data, testbed and authorised environment
(Single Linux host or WSL2, Docker Engine, local containers, synthetic data, local stub service; no third-party systems.)

## 7. Variables, controls and metrics
| Varied | Held fixed |
|---|---|
| Base image family | code commit, lockfile, Node.js version (documented if different), CPU/RAM limits, non-root user, workload, tool versions, Trivy DB snapshot |

| Metric | Evidence |
|---|---|
| Components | Syft SBOM (OS vs application) |
| Reported vulnerabilities | Trivy, deduplicated, OS vs application |
| Tools present | filesystem inventory |
| Size | local image size |
| Functionality | same test suite |
| Time-to-ready | docker run → first valid /healthz |
| Resources | CPU/RAM under load |
| Performance | req/s, p50/p99 latency, errors |
| Diagnostics | success, time, steps, tools, external help |

## 8. Procedure
(Pilot: 3 repetitions; main: 10 repetitions, 30 s warm-up + 60 s measurement; random order; failures kept; parameters frozen after pilot.)

## 9. Expected limitations and safety constraints
(One application, one environment; vulnerability counts are indicators, not exploitability; diagnostics depend on operator experience; WSL2/VM overhead; all testing local with synthetic data.)

## 10. Parameters to confirm in the pilot
(Load level, connection count, memory limit, final Node.js versions, startup readiness definition.)

## 11. Timeline
(Pilot → main experiments → analysis → paper → presentation → final package.)

## References
(See Phase 1 document.)
