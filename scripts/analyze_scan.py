#!/usr/bin/env python3
"""Reads Syft + Trivy JSON and writes results/security_summary.csv.
Dedup rule: one vulnerability = (VulnerabilityID, PkgName, InstalledVersion). Counted separately for OS packages and application dependencies."""
import csv, json, pathlib, collections
root = pathlib.Path(__file__).resolve().parent.parent / "results"
rows = []
for v in ["debian", "alpine", "distroless"]:
    sb = json.load(open(root / "sbom" / f"{v}.syft.json"))
    types = collections.Counter(a.get("type", "?") for a in sb.get("artifacts", []))
    tr = json.load(open(root / "trivy" / f"{v}.json"))
    seen, cnt = set(), collections.defaultdict(int)
    for res in tr.get("Results", []):
        cls = "os" if res.get("Class") == "os-pkgs" else "app" if res.get("Class") == "lang-pkgs" else None
        if not cls:
            continue
        for vu in res.get("Vulnerabilities") or []:
            key = (vu["VulnerabilityID"], vu["PkgName"], vu["InstalledVersion"])
            if key in seen:
                continue
            seen.add(key)
            cnt[(cls, vu.get("Severity", "UNKNOWN"))] += 1
    row = {"variant": v, "components_total": len(sb.get("artifacts", [])),
           "components_os": types.get("deb", 0) + types.get("apk", 0),
           "components_npm": types.get("npm", 0), "vulns_unique_total": len(seen)}
    for cls in ("os", "app"):
        for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"):
            row[f"{cls}_{sev.lower()}"] = cnt[(cls, sev)]
    rows.append(row)
with open(root / "security_summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(open(root / "security_summary.csv").read())
