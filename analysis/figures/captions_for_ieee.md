# Figure captions for the IEEE paper

Use the PDF versions for vector graphics. Wide two-panel figures are intended for a two-column-spanning figure (`figure*`), not a narrow single column.

1. **Size and composition.** Docker-reported local application-image size in decimal MB and Syft OS/npm component records. Component records are not unique application dependencies. Registry transfer size is not measured.
2. **Reported findings.** Distinct reported finding identities grouped by OS, application path `/app/node_modules`, and other language-package paths. Finding identity is (vulnerability ID, package, installed version). Counts describe scanner output, not proven exploitability.
3. **Startup distribution and sequence.** All ten launch-to-readiness attempts per image. The left panel uses a logarithmic vertical scale; the right panel shows the same attempts by round on a linear scale. No points were removed.
4. **Load performance.** Requests/s and per-run p99 latency across ten measured runs per image, each following a 30-second warm-up and lasting approximately 60 seconds. Points are runs, not individual requests. The latency panel is not a pooled-request latency distribution.
5. **Resource usage.** Distribution of per-run mean Docker CPU and memory readings across ten runs per image. Each mean uses 120 recorded samples. The primary summaries retain the initial low CPU sample. Docker MemUsage is not labeled as process RSS.
6. **Session trend.** Requests/s against actual measured-run start time, in minutes since the first load run. Lines connect observations from the same image family; the sequence does not establish a cause for temporal variation.

Boxplots show quartiles and medians with conventional 1.5-IQR whiskers. All observations are overlaid, including points beyond the whiskers. Quartiles are not confidence intervals. The six figure file numbers differ from report figure numbers because the session-trend figure is discussed before resource usage.
