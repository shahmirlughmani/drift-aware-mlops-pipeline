"""Ablation study for the HybridDriftDetector.

Disables one component at a time (consensus, confidence override, cooldown)
and re-runs the prequential benchmark to attribute the contribution of each
ingredient.

Outputs:
    experiments/results/ablation.csv
    experiments/results/ablation.json   (per-variant aggregates)

Usage:
    python -m experiments.ablation                # default seeds × streams
    python -m experiments.ablation --seeds 42 1337 2024 --streams sea hyperplane
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from src.drift.base import DriftEvent
from src.drift.detectors import HybridDriftDetector
from src.models import build_model
from src.pipelines.experiment import _stream_iter
from src.pipelines.metrics import detection_metrics
from src.pipelines.prequential import prequential_run

RESULTS_DIR = Path("experiments/results")


# ---------------------------------------------------------------------------
# Variants of HybridDD with one component disabled at a time
# ---------------------------------------------------------------------------

class HybridNoCooldown(HybridDriftDetector):
    """Cooldown disabled — measures how often the detector would re-fire."""
    name = "Hybrid-noCooldown"

    def __init__(self) -> None:
        super().__init__(cooldown=0)


class HybridNoConsensus(HybridDriftDetector):
    """Consensus disabled — fires whenever DDM enters drift, ignoring KSWIN."""
    name = "Hybrid-noConsensus"

    def update(self, error: int, x: np.ndarray | None = None) -> DriftEvent | None:
        self._t += 1
        self._err_window.append(int(error))
        if len(self._err_window) > self._err_window_size:
            self._err_window.pop(0)

        ddm_event = self.ddm.update(error, x)
        # Cooldown is preserved so we isolate just the consensus component.
        if self._t - self._last_drift_t < self.cooldown:
            return None

        if ddm_event is not None:
            self._last_drift_t = self._t
            return DriftEvent(
                index=self._t,
                severity=self._posterior_error(),
                detector=self.name,
            )
        return None


class HybridNoOverride(HybridDriftDetector):
    """Confidence-override disabled — pure two-detector consensus."""
    name = "Hybrid-noOverride"

    def update(self, error: int, x: np.ndarray | None = None) -> DriftEvent | None:
        self._t += 1
        self._err_window.append(int(error))
        if len(self._err_window) > self._err_window_size:
            self._err_window.pop(0)

        ddm_event = self.ddm.update(error, x)
        kswin_event = self.kswin.update(error, x)

        if ddm_event is not None:
            self._last_ddm_signal = self._t
        if kswin_event is not None:
            self._last_kswin_signal = self._t

        if self._t - self._last_drift_t < self.cooldown:
            return None

        consensus = (
            abs(self._last_ddm_signal - self._last_kswin_signal) <= self.consensus_window
            and max(self._last_ddm_signal, self._last_kswin_signal) == self._t
        )
        if consensus:
            self._last_drift_t = self._t
            return DriftEvent(
                index=self._t,
                severity=self._posterior_error(),
                detector=self.name,
            )
        return None


VARIANTS: dict[str, type[HybridDriftDetector]] = {
    "Full":         HybridDriftDetector,
    "noCooldown":   HybridNoCooldown,
    "noConsensus":  HybridNoConsensus,
    "noOverride":   HybridNoOverride,
}


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

@dataclass
class Row:
    variant: str
    model: str
    stream: str
    seed: int
    accuracy: float
    n_drift_events: int
    mean_detection_delay: float | None
    false_positive_rate: float
    miss_rate: float


def run_variants(seeds: list[int], streams: list[str], models: list[str],
                 n_samples: int) -> list[Row]:
    rows: list[Row] = []
    total = len(VARIANTS) * len(streams) * len(models) * len(seeds)
    i = 0
    for variant_name, variant_cls in VARIANTS.items():
        for stream_name in streams:
            for model_name in models:
                for seed in seeds:
                    i += 1
                    np.random.seed(seed)
                    X, y, true_drifts = _stream_iter(stream_name, seed, n_samples=n_samples)
                    if not true_drifts:
                        # ELEC2 has no ground-truth drift points — skip for the
                        # detection-quality ablation.
                        continue
                    model = build_model(model_name)
                    detector = variant_cls()

                    res = prequential_run(model, detector, X, y, warmup=200, adaptive=True)
                    dm = detection_metrics(res.drift_events, list(true_drifts))

                    rows.append(Row(
                        variant=variant_name,
                        model=model_name,
                        stream=stream_name,
                        seed=seed,
                        accuracy=res.accuracy,
                        n_drift_events=len(res.drift_events),
                        mean_detection_delay=(
                            None if np.isnan(dm.mean_delay) else float(dm.mean_delay)
                        ),
                        false_positive_rate=dm.false_positive_rate,
                        miss_rate=dm.miss_rate,
                    ))
                    print(f"[{i:>3d}/{total}] {variant_name:14s}  {stream_name:10s}  "
                          f"{model_name:14s}  seed={seed}  "
                          f"acc={res.accuracy:.3f}  "
                          f"events={len(res.drift_events):>3d}  "
                          f"fpr={dm.false_positive_rate:.2f}")
    return rows


def aggregate(rows: list[Row]) -> dict[str, dict[str, float]]:
    by_variant: dict[str, list[Row]] = {}
    for r in rows:
        by_variant.setdefault(r.variant, []).append(r)

    out: dict[str, dict[str, float]] = {}
    for v, rs in by_variant.items():
        accs = [r.accuracy for r in rs]
        fprs = [r.false_positive_rate for r in rs]
        delays = [r.mean_detection_delay for r in rs if r.mean_detection_delay is not None]
        out[v] = {
            "accuracy_mean": float(np.mean(accs)),
            "accuracy_std":  float(np.std(accs)),
            "fpr_mean":      float(np.mean(fprs)),
            "fpr_std":       float(np.std(fprs)),
            "delay_mean":    float(np.mean(delays)) if delays else float("nan"),
            "delay_std":     float(np.std(delays)) if delays else float("nan"),
            "n_runs":        float(len(rs)),
        }
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, nargs="+", default=[42, 1337, 2024])
    p.add_argument("--streams", nargs="+", default=["sea", "hyperplane"])
    p.add_argument("--models", nargs="+", default=["sgd_logistic"])
    p.add_argument("--n-samples", type=int, default=20_000,
                   help="Stream length per run. 20k keeps the ablation fast.")
    args = p.parse_args()

    rows = run_variants(args.seeds, args.streams, args.models, args.n_samples)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS_DIR / "ablation.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))

    summary = aggregate(rows)
    json_path = RESULTS_DIR / "ablation.json"
    with json_path.open("w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nWrote {csv_path}")
    print(f"Wrote {json_path}")
    print("\nSummary (mean across runs):")
    print(f"  {'variant':14s}  {'acc':>6s}  {'fpr':>6s}  {'delay':>8s}  n")
    for v, s in summary.items():
        delay = f"{s['delay_mean']:.0f}" if not np.isnan(s["delay_mean"]) else "  ---"
        print(f"  {v:14s}  {s['accuracy_mean']:6.3f}  {s['fpr_mean']:6.2f}  "
              f"{delay:>8s}  {int(s['n_runs'])}")


if __name__ == "__main__":
    main()
