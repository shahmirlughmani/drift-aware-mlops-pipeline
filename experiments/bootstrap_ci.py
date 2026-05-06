"""Bootstrap 95% CIs on the headline metrics across detectors.

Reads `experiments/results/results.csv`, resamples per-detector with
replacement (10k iterations) and reports mean + 95% CI for accuracy,
false-positive rate, and mean detection delay.

Output: `experiments/results/bootstrap_ci.json`.

Usage:
    python -m experiments.bootstrap_ci
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

RESULTS_DIR = Path("experiments/results")
N_BOOT = 10_000
RNG_SEED = 42


def load_rows() -> list[dict[str, Any]]:
    path = RESULTS_DIR / "results.csv"
    with path.open() as f:
        return list(csv.DictReader(f))


def to_float(v: str) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def bootstrap_ci(values: list[float], n_boot: int = N_BOOT,
                 rng: np.random.Generator | None = None,
                 alpha: float = 0.05) -> tuple[float, float, float]:
    if not values:
        return float("nan"), float("nan"), float("nan")
    rng = rng or np.random.default_rng(RNG_SEED)
    arr = np.asarray(values, dtype=float)
    means = []
    n = len(arr)
    for _ in range(n_boot):
        sample = rng.choice(arr, size=n, replace=True)
        means.append(float(sample.mean()))
    means_arr = np.asarray(means)
    lo = float(np.percentile(means_arr, 100 * alpha / 2))
    hi = float(np.percentile(means_arr, 100 * (1 - alpha / 2)))
    return float(arr.mean()), lo, hi


def main() -> None:
    rows = load_rows()

    grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        det = r["detector"]
        for col in ("accuracy", "false_positive_rate", "mean_detection_delay", "miss_rate"):
            v = to_float(r.get(col))
            if v is not None and not np.isnan(v):
                grouped[det][col].append(v)

    rng = np.random.default_rng(RNG_SEED)
    out: dict[str, Any] = {"n_bootstrap": N_BOOT, "alpha": 0.05, "detectors": {}}
    for det, metrics in grouped.items():
        out["detectors"][det] = {}
        for metric, values in metrics.items():
            mean, lo, hi = bootstrap_ci(values, rng=rng)
            out["detectors"][det][metric] = {
                "mean": mean, "ci_lo": lo, "ci_hi": hi, "n": len(values),
            }

    json_path = RESULTS_DIR / "bootstrap_ci.json"
    with json_path.open("w") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote {json_path}\n")
    print(f"{'detector':14s}  {'metric':24s}  {'mean':>7s}  {'95% CI':>20s}  n")
    print("-" * 80)
    for det, metrics in out["detectors"].items():
        for metric, d in metrics.items():
            ci = f"[{d['ci_lo']:.3f}, {d['ci_hi']:.3f}]"
            print(f"{det:14s}  {metric:24s}  {d['mean']:7.3f}  {ci:>20s}  {d['n']}")


if __name__ == "__main__":
    main()
