from __future__ import annotations

import numpy as np

from src.drift.base import DriftEvent
from src.pipelines.metrics import detection_metrics, latency_summary, throughput


def _ev(idx: int, name: str = "X") -> DriftEvent:
    return DriftEvent(index=idx, severity=1.0, detector=name)


def test_detection_metrics_perfect_match() -> None:
    truths = [1000, 2000, 3000]
    events = [_ev(1010), _ev(2050), _ev(3100)]
    m = detection_metrics(events, truths, tolerance=500)
    assert m.true_positives == 3
    assert m.false_positives == 0
    assert m.missed == 0
    assert 0 < m.mean_delay < 200


def test_detection_metrics_with_false_positives() -> None:
    truths = [1000]
    events = [_ev(50), _ev(1050), _ev(9000)]
    m = detection_metrics(events, truths, tolerance=200)
    assert m.true_positives == 1
    assert m.false_positives == 2


def test_latency_summary_empty() -> None:
    s = latency_summary(np.array([], dtype=np.int64))
    assert s["p99_us"] == 0.0


def test_throughput_basic() -> None:
    assert throughput(1000, 2.0) == 500.0
    assert np.isnan(throughput(1000, 0.0))
