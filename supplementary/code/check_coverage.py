#!/usr/bin/env python3
"""Recompute the platform-coverage matrix (main paper, Fig. 2) from data/datasets_extended.csv.

Diagonal: datasets that include the platform.
Off-diagonal: datasets that record both platforms jointly.
Run from the archive root:  python3 code/check_coverage.py
"""
import csv
import itertools
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "data" / "datasets_extended.csv"
PLATFORMS = {"Ego": "Ego", "Infra.": "Infrastructure", "Aerial": "Aerial", "Traces": "Traces"}
EXPECTED = {("Ego", "Ego"): 21, ("Ego", "Infra."): 3, ("Ego", "Aerial"): 1, ("Ego", "Traces"): 1,
            ("Infra.", "Infra."): 3, ("Infra.", "Aerial"): 0, ("Infra.", "Traces"): 0,
            ("Aerial", "Aerial"): 4, ("Aerial", "Traces"): 0, ("Traces", "Traces"): 3}

rows = list(csv.DictReader(open(CSV, newline="", encoding="utf-8")))
assert len(rows) == 26, len(rows)
ok = True
for a, b in itertools.combinations_with_replacement(PLATFORMS, 2):
    names = [r["Dataset"] for r in rows if r[PLATFORMS[a]] == "1" and r[PLATFORMS[b]] == "1"]
    match = len(names) == EXPECTED[(a, b)]
    ok &= match
    print(f"{a:7s} x {b:7s} {len(names):3d}  {'ok' if match else 'MISMATCH'}  {', '.join(names)}")
print("All cells match Fig. 2." if ok else "Some cells differ from Fig. 2.")
