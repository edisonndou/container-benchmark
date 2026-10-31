# Project Completion Record

> This earlier closeout note is superseded by [FINAL_AUDIT.md](FINAL_AUDIT.md).
> The final audit records independent reanalysis, remaining byte-integrity
> limitations, and post-measurement code corrections. The group's confirmed
> contribution declaration is equal one-third participation by all three authors.

Repository review date: **31 October 2026**.

The implemented benchmark and recorded analysis are complete for the scope
described below. The user has confirmed that the final documentation and
presentation are complete. Those final submission artifacts were not inspected
during this repository review.

## Completed scope and evidence

| Area | Recorded outcome | Evidence |
|---|---|---|
| Application and images | Same API and four image variants; actual Node.js v22.22.0 recorded for all four in the main run. | [`app/`](../app/), [`docker/`](../docker/), [build metadata](../results/main/metadata/build_info.csv) |
| Functional validation | All four variants recorded as PASS. | [Main-run functional results](../results/main/metadata/functional.csv) |
| Pilot | Three startup and three load trials per primary variant; recorded quality issues list is empty. | [Pilot quality report](../results/pilot/perf_quality.json) |
| Main experiment | Ten successful startup attempts and ten load reports per primary variant: 30 startup and 30 load trials in total. Recorded quality issues list is empty. | [Main quality report](../results/main/perf_quality.json), [performance summary](../results/main/perf_summary.csv) |
| Run provenance | Main run has a recorded code commit, settings, and completion timestamp. | [Run metadata](../results/main/metadata/run.txt), [completion timestamp](../results/main/metadata/completed_utc.txt) |
| Security assessment | SBOM and vulnerability evidence for Debian Slim, Alpine, and Distroless, with separate OS/application categories. | [Main-run security evidence](../results/main/security/), [security summary](../results/main/security/security_summary.csv) |
| Operability | Nine preparatory fault/recovery checks and one assisted orientation; no independent timed diagnosis trials. | [Assessment](operability_assessment.md), [session status](../results/operator_diagnostics/session_status.json) |
| Analysis | Tables, figures, editable analysis, explanatory PDF, and a stored audit reporting 242 passed checks. | [Analysis guide](../analysis/README.md), [stored audit](../analysis/audit.json) |
| Contribution declaration | Edison Ndou, Donart Ajvazi, and Bleron Baftiu declare equal contributions, one third each. | [Contributions](../CONTRIBUTIONS.md) |

These statements describe saved evidence. No tests, benchmarks, fault scenarios,
or executable analysis audits were run during this closeout. The stored audit
describes its original source snapshot, not a fresh audit of the current tree.

## Diagnostic scope decision

The original plan for nine independent timed operator trials was not carried
out. The session record explicitly says no further timed trials are planned.
The delivered assessment therefore covers fault reproduction, recovery, and
available tools. Independent diagnosis time and operator effort remain future
work and must not appear as measured findings.

The assisted orientation is not a tenth independent fault/recovery combination.
Distroless Debug remains separate from the primary three-family security and
performance comparison.

## Reproduction limits

- The source archive did not contain the original `trivy.db` binary. The stored
  hash manifest and metadata do not replace it. Exact historical vulnerability
  scan reproduction requires the matching database snapshot from the original
  measurement machine. A fresh database produces a new scan, not a reproduction
  of the historical counts.
- The archived evidence lacks the full Windows build and WSL program version.
  Do not reconstruct those values from the current machine or present guesses
  as measurements from the original run.
- Base-image tags can move. Recorded image IDs and runtime versions describe
  the historical run; rebuilding today does not guarantee identical images.
- Results concern one application, one host/WSL2 environment, and one primary
  load profile. Vulnerability counts do not demonstrate exploitability, and
  the performance results do not establish a specific underlying cause.

These are disclosed limits of the recorded study, not reasons to replace its
measurements or invent missing evidence.

## Historical documents and final handoff

The proposal outline, dated plans, and pilot-era schedules are retained as
historical material. Their future-tense tasks and original role suggestions
do not supersede this completion record or the current contribution split.
The analysis PDF remains the original empirical report; it is not relabeled as
the final academic paper.

The user's completed final documentation and presentation should accompany
the repository when submitted. Personal contribution claims require the
members' confirmation; the responsibility split is not an authorship audit.

No commits, pushes, merges, tags, or deployments were performed in this closeout.
