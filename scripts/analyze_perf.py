#!/usr/bin/env python3
"""Summarize repetitions; CPU/RAM contribute one mean per load run."""
import collections
import csv
import json
import math
from pathlib import Path
import re
import statistics as st
import sys

ROOT = Path(sys.argv[1])
VARIANTS = ("debian", "alpine", "distroless")
data = collections.defaultdict(lambda: collections.defaultdict(list))
issues = []
counts = {
    v: {
        "startup_attempts": 0,
        "startup_failed": 0,
        "load_attempts": 0,
        "load_reports": 0,
    }
    for v in VARIANTS
}

def number(value):
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError("Invalid numeric measurement")
    return value

def memory_mib(value):
    used = value.split("/", 1)[0].strip()
    match = re.fullmatch(r"([\d.]+)\s*(B|[KMGT]i?B)", used)
    if not match:
        raise ValueError(f"Unknown memory format: {used}")
    factors = {
        "B": 1,
        "KB": 1000,
        "MB": 1000**2,
        "GB": 1000**3,
        "TB": 1000**4,
        "KiB": 1024,
        "MiB": 1024**2,
        "GiB": 1024**3,
        "TiB": 1024**4,
    }
    return number(match[1]) * factors[match[2]] / 1024**2

seen = set()
with (ROOT / "startup.csv").open() as stream:
    for row in csv.DictReader(stream):
        variant = row["variant"]
        identity = (row["round"], variant)
        if variant not in VARIANTS or identity in seen:
            raise SystemExit(f"Invalid/duplicate startup row: {identity}")
        seen.add(identity)
        counts[variant]["startup_attempts"] += 1

        if row["ok"] == "1":
            data[variant]["startup_ms"].append(number(row["startup_ms"]))
        else:
            counts[variant]["startup_failed"] += 1
            issues.append(f"startup {identity}: failed")

seen = set()
with (ROOT / "load" / "runs.csv").open() as stream:
    for row in csv.DictReader(stream):
        variant, repeat = row["variant"], row["round"]
        identity = (repeat, variant)
        if variant not in VARIANTS or identity in seen:
            raise SystemExit(f"Invalid/duplicate load row: {identity}")
        seen.add(identity)
        counts[variant]["load_attempts"] += 1

        if row["status"] != "COMPLETED" or row["exit_code"] != "0":
            issues.append(f"load {identity}: {row['status']}")
            continue

        suffix = f"{repeat}_{variant}"
        try:
            report = json.loads(
                (ROOT / "load" / f"ac_{suffix}.json").read_text()
            )
            metrics = {
                "rps": number(report["requests"]["average"]),
                "p50_ms": number(report["latency"]["p50"]),
                "p99_ms": number(report["latency"]["p99"]),
                "transport_errors": number(report["errors"]),
                "non2xx": number(report["non2xx"]),
                "timeouts": number(report["timeouts"]),
            }
            requests_total = number(report["requests"]["total"])
            responses_2xx = number(report["2xx"])
            status_codes = report["statusCodeStats"]
        except (OSError, ValueError, KeyError, TypeError) as error:
            issues.append(f"load {identity}: invalid report: {error}")
            continue

        counts[variant]["load_reports"] += 1
        for metric, value in metrics.items():
            data[variant][metric].append(value)

        if (
            requests_total == 0
            or responses_2xx != requests_total
            or not isinstance(status_codes, dict)
            or set(status_codes) != {"200"}
        ):
            issues.append(
                f"load {identity}: missing or unexpected successful HTTP responses"
            )

        if any(metrics[k] for k in ("transport_errors", "non2xx", "timeouts")):
            issues.append(
                f"load {identity}: request errors; retained in summary"
            )

        try:
            state = json.loads(
                (ROOT / "load" / f"inspect_{suffix}.json").read_text()
            )[0]
            if (
                state["State"]["OOMKilled"]
                or not state["State"]["Running"]
                or state["RestartCount"] != 0
            ):
                issues.append(f"load {identity}: abnormal container state")
        except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
            issues.append(f"load {identity}: invalid state: {error}")

        cpu, memory = [], []
        try:
            with (ROOT / "load" / f"stats_{suffix}.csv").open() as samples:
                clean_lines = (
                    re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", line)
                    for line in samples
                )
                for sample in csv.reader(line for line in clean_lines if line.strip()):
                    if (
                        len(sample) != 2
                        or not sample[0].strip().endswith("%")
                    ):
                        raise ValueError("Invalid resource sample")
                    cpu.append(number(sample[0].strip()[:-1]))
                    memory.append(memory_mib(sample[1]))

            if not cpu:
                raise ValueError("No resource samples")

            data[variant]["cpu_mean_pct"].append(st.mean(cpu))
            data[variant]["mem_mean_mib"].append(st.mean(memory))
        except (OSError, ValueError) as error:
            issues.append(f"load {identity}: invalid resource data: {error}")

with (ROOT / "perf_summary.csv").open("w", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow([
        "variant", "metric", "n_runs",
        "median", "q1", "q3", "min", "max",
    ])

    for variant in VARIANTS:
        for metric, values in data[variant].items():
            if len(values) > 1:
                quartiles = st.quantiles(values, n=4, method="inclusive")
            else:
                quartiles = values * 3

            summary = (
                st.median(values),
                quartiles[0],
                quartiles[2],
                min(values),
                max(values),
            )
            writer.writerow([
                variant, metric, len(values),
                *[round(value, 3) for value in summary],
            ])

quality = {"counts": counts, "issues": issues}
(ROOT / "perf_quality.json").write_text(
    json.dumps(quality, indent=2) + "\n"
)

print((ROOT / "perf_summary.csv").read_text())
print(json.dumps(quality, indent=2))
