#!/usr/bin/env python3
"""Prepare an operator session without starting any timed trial."""
import csv
from datetime import datetime, timezone
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = (
    Path(sys.argv[1]) if len(sys.argv) > 1
    else ROOT / "results/operator_diagnostics"
)

if OUT.exists():
    raise SystemExit(f"STOP: session directory already exists: {OUT}")

def answer(question):
    while True:
        value = input(question).strip()
        if value:
            return value
        print("Shkruani nje pergjigje; mos e lini bosh.")

experience = answer("Pervoje e Donartit me Docker: ")
exposure = answer(
    "A i ka pare Donarti zgjidhjet pergatitore? Shpjegoni: "
)

cases = list(itertools.product(
    ("config", "permissions", "connectivity"),
    ("debian", "alpine", "distroless"),
))
rng = random.SystemRandom()

for _ in range(10000):
    rng.shuffle(cases)
    if all(
        cases[i][0] != cases[i - 1][0]
        for i in range(1, len(cases))
    ):
        break
else:
    raise SystemExit("Could not generate the trial order.")

commit = subprocess.check_output(
    ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
).strip()

profile = {
    "operator": "Donart",
    "preparer": "Edison",
    "docker_experience": experience,
    "prior_exposure": exposure,
    "trial_timeout_seconds": 900,
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "code_commit_at_preparation": commit,
    "trial_count": len(cases),
    "timing_started": False,
}

OUT.mkdir(parents=True, exist_ok=False)
(OUT / "operator_profile.json").write_text(
    json.dumps(profile, indent=2, ensure_ascii=False) + "\n"
)

with (OUT / "preparer_plan.csv").open("w", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["trial_id", "order", "scenario", "variant"])
    for index, (scenario, variant) in enumerate(cases, 1):
        writer.writerow([
            f"trial{index:02d}", index, scenario, variant
        ])

(OUT / "README.txt").write_text(
    "Operator session; no timed trials have started.\n"
    "preparer_plan.csv is for the preparer only until all trials finish.\n"
    "Do not show injection commands or future causes to the operator.\n"
)

print("Sesioni u pergatit me 9 prova. Matja e kohes nuk ka filluar.")
print("Mos ia shfaqni Donartit preparer_plan.csv.")
