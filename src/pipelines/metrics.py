"""Drift-detection metrics: detection delay, missed drifts, false-positive rate.

Definitions follow Bifet et al. (2018) "Machine Learning for Data Streams"
and Goncalves et al. (2014) systematic review on drift detector evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.drift.base import DriftEvent


@dataclass
class DetectionMetrics:
    n_true: int
    n_detected: int
    true_positives: int
    false_positives: int
    missed: int
    mean_delay: float  # mean time-to-detect (in samples), TPs only
    false_positive_rate: float  # FP / detections
    miss_rate: float  # missed / true positives possible


def detection_metrics(
    events: list[DriftEvent],
    true_drift_points: list[int],
    *,
    tolerance: int = 1000,
) -> DetectionMetrics:
    """A detected drift at index e is a TRUE positive for the closest unmatched
    ground-truth drift d if d <= e <= d + tolerance. Otherwise it's a FP.
    """
    matched: set[int] = set()
    delays: list[int] = []
    fp = 0

    for ev in events:
        candidate = None
        for i, d in enumerate(true_drift_points):
            if i in matched:
                continue
            if d <= ev.index <= d + tolerance:
                candidate = (i, d)
                break
        if candidate is None:
            fp += 1
        else:
            i, d = candidate
            matched.add(i)
            delays.append(ev.index - d)

    tp = len(matched)
    missed = len(true_drift_points) - tp
    return DetectionMetrics(
        n_true=len(true_drift_points),
        n_detected=len(events),
        true_positives=tp,
        false_positives=fp,
        missed=missed,
        mean_delay=float(np.mean(delays)) if delays else float("nan"),
        false_positive_rate=fp / max(1, len(events)),
        miss_rate=missed / max(1, len(true_drift_points)),
    )


def latency_summary(latencies_ns: np.ndarray) -> dict[str, float]:
    if latencies_ns.size == 0:
        return {"p50_us": 0.0, "p95_us": 0.0, "p99_us": 0.0, "mean_us": 0.0}
    us = latencies_ns / 1_000.0
    return {
        "p50_us": float(np.percentile(us, 50)),
        "p95_us": float(np.percentile(us, 95)),
        "p99_us": float(np.percentile(us, 99)),
        "mean_us": float(us.mean()),
    }


def throughput(n_samples: int, elapsed_s: float) -> float:
    return n_samples / elapsed_s if elapsed_s > 0 else float("nan")
