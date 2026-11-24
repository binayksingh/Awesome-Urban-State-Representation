#!/usr/bin/env python3
"""Reference implementation of the USR-5 aggregate score (main paper, Eq. 3).

    USR-5 = ( prod_{i=1..5} min(s_i / s_i_ref, 2) ) ** (1/5)

s_i     : score of the shared Urban State Representation on test i (higher is better, > 0)
s_i_ref : score of the single-platform, single-task reference on the same data (> 0)
T2 (Read) is already a mean of per-head relative scores, so s_2_ref = 1.

Bytes sent (T1) and unknown-object recall (T4) are reported as diagnostics,
not as ratios, because a reference can score zero on them.

USR-5 is a proposal: no published system has been scored on all five tests.
The profiles in `demo()` are hypothetical and only illustrate the arithmetic.
"""
from __future__ import annotations

import math
from typing import Mapping, Optional

TESTS = ("T1_write", "T2_read", "T3_persistence", "T4_calibration", "T5_transfer")
CAP = 2.0


def ratio(s: float, s_ref: float, cap: float = CAP) -> float:
    """Capped per-test ratio min(s / s_ref, cap)."""
    if s <= 0 or s_ref <= 0:
        raise ValueError("USR-5 needs strictly positive scores (use 1-ECE for T4).")
    return min(s / s_ref, cap)


def usr5(scores: Mapping[str, float], refs: Mapping[str, float], cap: float = CAP,
         allow_partial: bool = False) -> Optional[float]:
    """Geometric mean of capped ratios over the five tests.

    If a test is missing, USR-5 is undefined (None) unless allow_partial=True,
    in which case the geometric mean over the available tests is returned and
    should be reported as USR-k with the tests listed.
    """
    present = [t for t in TESTS if t in scores and t in refs]
    if len(present) < len(TESTS) and not allow_partial:
        return None
    if not present:
        return None
    logs = [math.log(ratio(scores[t], refs[t], cap)) for t in present]
    return math.exp(sum(logs) / len(logs))


def worked_example() -> None:
    """T1 from published numbers: Where2comm on DAIR-V2X (AP, LiDAR, V2I)."""
    for metric, coop, solo in (("AP@0.5", 63.7, 50.0), ("AP@0.7", 48.9, 43.6)):
        print(f"T1 ratio on DAIR-V2X {metric}: {coop}/{solo} = {ratio(coop, solo):.2f}")


def demo() -> None:
    """Hypothetical ratio profiles (NOT results) comparing aggregation rules."""
    profiles = {
        "A balanced gain": [1.10, 1.10, 1.10, 1.10, 1.10],
        "B one large gain": [2.50, 0.90, 0.90, 0.90, 0.90],
        "C one failure": [1.30, 1.30, 1.30, 1.30, 0.30],
    }
    print(f"{'profile':18s} {'arith.':>7s} {'geo.':>7s} {'geo.+cap':>9s}")
    for name, r in profiles.items():
        arith = sum(r) / len(r)
        geo = math.exp(sum(math.log(x) for x in r) / len(r))
        geo_cap = math.exp(sum(math.log(min(x, CAP)) for x in r) / len(r))
        print(f"{name:18s} {arith:7.3f} {geo:7.3f} {geo_cap:9.3f}")


if __name__ == "__main__":
    worked_example()
    print()
    demo()
