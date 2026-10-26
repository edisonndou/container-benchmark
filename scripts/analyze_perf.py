#!/usr/bin/env python3
"""Aggregates startup.csv and load/ac_*.json + stats_*.csv into perf_summary.csv (median and IQR over repetitions)."""
import csv, json, pathlib, re, statistics as st, sys, collections
d = pathlib.Path(sys.argv[1])
def q(xs):
    xs = sorted(xs)
    if len(xs) < 2: return (xs[0], xs[0]) if xs else (0, 0)
    c = st.quantiles(xs, n=4, method="inclusive"); return c[0], c[2]
def mem_mib(s):
    m = re.match(r"([\d.]+)\s*([KMG]i?B)", s.split("/")[0].strip()); v = float(m[1]); u = m[2][0]
    return v / 1024 if u == "K" else v * 1024 if u == "G" else v
data = collections.defaultdict(lambda: collections.defaultdict(list))
for r in csv.DictReader(open(d / "startup.csv")):
    if r["ok"] == "1": data[r["variant"]]["startup_ms"].append(float(r["startup_ms"]))
    else: data[r["variant"]]["startup_fail"].append(1)
for f in sorted((d / "load").glob("ac_*.json")):
    v = f.stem.split("_", 2)[2]; j = json.load(open(f))
    data[v]["rps"].append(j["requests"]["average"]); data[v]["p50_ms"].append(j["latency"]["p50"])
    data[v]["p97_5_ms"].append(j["latency"]["p97_5"]); data[v]["p99_ms"].append(j["latency"]["p99"])
    data[v]["errors"].append(j["errors"] + j["non2xx"])
for f in sorted((d / "load").glob("stats_*.csv")):
    v = f.stem.split("_", 2)[2]
    for line in open(f):
        cpu, mem = line.strip().split(",", 1)
        data[v]["cpu_pct"].append(float(cpu.rstrip("%"))); data[v]["mem_mib"].append(mem_mib(mem))
metrics = ["startup_ms", "rps", "p50_ms", "p97_5_ms", "p99_ms", "cpu_pct", "mem_mib", "errors"]
with open(d / "perf_summary.csv", "w", newline="") as o:
    w = csv.writer(o); w.writerow(["variant", "metric", "n", "median", "q1", "q3", "min", "max"])
    for v in ("debian", "alpine", "distroless"):
        for m in metrics:
            xs = data[v][m]
            if xs:
                a, b = q(xs); w.writerow([v, m, len(xs), round(st.median(xs), 2), round(a, 2), round(b, 2), round(min(xs), 2), round(max(xs), 2)])
print(open(d / "perf_summary.csv").read())
