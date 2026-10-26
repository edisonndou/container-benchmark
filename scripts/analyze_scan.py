#!/usr/bin/env python3
"""Summarize existing Syft and Trivy reports.

Components count SBOM records.
Finding identity: (VulnerabilityID, PkgName, InstalledVersion).
Deduplicate within each scope and globally.
If duplicate severities disagree, retain the highest severity.
Scope totals may overlap; global total counts each identity once.
"""
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "results"
VARIANTS = ("debian", "alpine", "distroless")
SCOPES = ("os", "project", "other_lang", "unknown_lang")
SEVERITIES = ("UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL")
RANK = {severity: i for i, severity in enumerate(SEVERITIES)}

rows = []
project_sets = {}

for variant in VARIANTS:
    sbom = json.loads(
        (ROOT / "sbom" / f"{variant}.syft.json").read_text()
    )
    report = json.loads(
        (ROOT / "trivy" / f"{variant}.json").read_text()
    )
    artifacts = sbom.get("artifacts", [])
    types = collections.Counter(p.get("type", "?") for p in artifacts)
    findings = {scope: {} for scope in SCOPES}
    global_seen = set()

    for result in report.get("Results", []):
        package_class = result.get("Class")
        if package_class not in ("os-pkgs", "lang-pkgs"):
            continue

        for vuln in result.get("Vulnerabilities") or []:
            path = vuln.get("PkgPath") or ""
            normalized = "/" + path.lstrip("/")

            if package_class == "os-pkgs":
                scope = "os"
            elif normalized.startswith("/app/node_modules/"):
                scope = "project"
            elif path:
                scope = "other_lang"
            else:
                scope = "unknown_lang"

            key = (
                vuln["VulnerabilityID"],
                vuln["PkgName"],
                vuln["InstalledVersion"],
            )
            severity = vuln.get("Severity", "UNKNOWN")
            if severity not in RANK:
                severity = "UNKNOWN"

            previous = findings[scope].get(key, "UNKNOWN")
            findings[scope][key] = max(
                previous, severity, key=RANK.__getitem__
            )
            global_seen.add(key)

    project_sets[variant] = set(findings["project"])

    row = {
        "variant": variant,
        "components_total": len(artifacts),
        "components_os": types["deb"] + types["apk"],
        "components_npm": types["npm"],
        "vulns_unique_total": len(global_seen),
    }

    for scope in SCOPES:
        counts = collections.Counter(findings[scope].values())
        row[f"{scope}_total"] = len(findings[scope])
        for severity in reversed(SEVERITIES):
            row[f"{scope}_{severity.lower()}"] = counts[severity]

    rows.append(row)

output = ROOT / "security_summary.csv"
with output.open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

baseline = project_sets["debian"]
comparison = {
    "identity_fields": [
        "VulnerabilityID", "PkgName", "InstalledVersion"
    ],
    "baseline": "debian",
    "project_scope": "/app/node_modules/",
    "findings": {
        variant: sorted(project_sets[variant])
        for variant in VARIANTS
    },
    "comparisons": {
        variant: {
            "matches_debian": project_sets[variant] == baseline,
            "missing": sorted(baseline - project_sets[variant]),
            "extra": sorted(project_sets[variant] - baseline),
        }
        for variant in ("alpine", "distroless")
    },
}

audit = ROOT / "project_findings_comparison.json"
audit.write_text(json.dumps(comparison, indent=2) + "\n")

print(output.read_text())
for variant, result in comparison["comparisons"].items():
    print(
        f"{variant}: matches_debian={result['matches_debian']}, "
        f"missing={len(result['missing'])}, "
        f"extra={len(result['extra'])}"
    )
