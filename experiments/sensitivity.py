"""Sensitivity analysis for HybridDD hyperparameters.

Sweeps `consensus_window` and `confidence_threshold` and reports a composite
goodness score per cell. Used to show that the chosen (200, 0.35) lies on a
broad plateau — i.e. the result is not a tuning artefact.

Composite score:  accuracy − false_positive_rate − 0.3 × normalised_delay
    (higher is better; clipped to [0, 1] for the heatmap).

Outputs:
    experiments/results/sensitivity.csv
    experiments/results/sensitivity.json   (composite grid + best cell)

Usage:
    python -m experiments.sensitivity --seeds 42 1337 --streams sea hyperplane
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from src.drift.detectors import HybridDriftDetector
from src.models import build_model
from src.pipelines.experiment import _stream_iter
from src.pipelines.metrics import detection_metrics
from src.pipelines.prequential import prequential_run

RESULTS_DIR = Path("experiments/results")

CONSENSUS_WINDOWS = [100, 150, 200, 250, 300]
CONFIDENCE_THRESHOLDS = [0.25, 0.30, 0.35, 0.40, 0.45]


@dataclass
class Row:
    consensus_window: int
    confidence_threshold: float
    model: str
    stream: str
    seed: int
    accuracy: float
    false_positive_rate: float
    mean_detection_delay: float | None
    composite: float


def composite_score(accuracy: float, fpr: float, delay: float | None,
                    delay_norm: float = 1000.0) -> float:
    """Higher is better; clipped to [0, 1] for heatmap rendering."""
    d = (delay if delay is not None else delay_norm) / delay_norm
    return float(np.clip(accuracy - fpr - 0.3 * d, 0.0, 1.0))


def run(seeds: list[int], streams: list[str], models: list[str],
        n_samples: int) -> list[Row]:
    rows: list[Row] = []
    total = (len(CONSENSUS_WINDOWS) * len(CONFIDENCE_THRESHOLDS)
             * len(streams) * len(models) * len(seeds))
    print(f"Sensitivity sweep: {total} runs")
    i = 0
    for cw in CONSENSUS_WINDOWS:
        for ct in CONFIDENCE_THRESHOLDS:
            for stream_name in streams:
                for model_name in models:
                    for seed in seeds:
                        i += 1
                        np.random.seed(seed)
                        X, y, true_drifts = _stream_iter(stream_name, seed,
                                                         n_samples=n_samples)
                        if not true_drifts:
                            continue
                        model = build_model(model_name)
                        det = HybridDriftDetector(
                            consensus_window=cw,
                            confidence_threshold=ct,
                        )
                        res = prequential_run(model, det, X, y,
                                              warmup=200, adaptive=True)
                        dm = detection_metrics(res.drift_events, list(true_drifts))
                        delay = (None if np.isnan(dm.mean_delay)
                                 else float(dm.mean_delay))
                        rows.append(Row(
                            consensus_window=cw,
                            confidence_threshold=ct,
                            model=model_name,
                            stream=stream_name,
                            seed=seed,
                            accuracy=res.accuracy,
                            false_positive_rate=dm.false_positive_rate,
                            mean_detection_delay=delay,
                            composite=composite_score(
                                res.accuracy,
                                dm.false_positive_rate,
                                delay,
                            ),
                        ))
                        if i % 5 == 0:
                            print(f"  [{i:>3d}/{total}] cw={cw} ct={ct:.2f} "
                                  f"stream={stream_name} seed={seed} "
                                  f"composite={rows[-1].composite:.3f}")
    return rows


def build_grid(rows: list[Row]) -> dict[str, list]:
    grid = np.zeros((len(CONFIDENCE_THRESHOLDS), len(CONSENSUS_WINDOWS)))
    counts = np.zeros_like(grid)
    for r in rows:
        i = CONFIDENCE_THRESHOLDS.index(r.confidence_threshold)
        j = CONSENSUS_WINDOWS.index(r.consensus_window)
        grid[i, j] += r.composite
        counts[i, j] += 1
    grid = np.where(counts > 0, grid / np.maximum(counts, 1), 0.0)
    best_idx = np.unravel_index(np.argmax(grid), grid.shape)
    return {
        "consensus_windows":     CONSENSUS_WINDOWS,
        "confidence_thresholds": CONFIDENCE_THRESHOLDS,
        "composite_grid":        grid.tolist(),
        "best_cell":             [int(i) for i in best_idx],
        "best_consensus_window": int(CONSENSUS_WINDOWS[best_idx[1]]),
        "best_confidence_threshold": float(CONFIDENCE_THRESHOLDS[best_idx[0]]),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, nargs="+", default=[42, 1337])
    p.add_argument("--streams", nargs="+", default=["sea", "hyperplane"])
    p.add_argument("--models", nargs="+", default=["sgd_logistic"])
    p.add_argument("--n-samples", type=int, default=20_000)
    args = p.parse_args()

    rows = run(args.seeds, args.streams, args.models, args.n_samples)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS_DIR / "sensitivity.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))

    grid = build_grid(rows)
    json_path = RESULTS_DIR / "sensitivity.json"
    with json_path.open("w") as f:
        json.dump(grid, f, indent=2)

    print(f"\nWrote {csv_path}")
    print(f"Wrote {json_path}")
    print(f"\nBest cell: cw={grid['best_consensus_window']}, "
          f"ct={grid['best_confidence_threshold']:.2f}")


if __name__ == "__main__":
    main()
