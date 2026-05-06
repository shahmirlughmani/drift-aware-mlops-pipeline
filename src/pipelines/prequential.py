"""Prequential (test-then-train) evaluation loop.

This is the core experimental harness. For each step t in a stream:
  1. Predict y_hat_t using the current model.
  2. Observe y_t, compute error = (y_hat_t != y_t).
  3. Feed error to the drift detector.
  4. partial_fit the model on (x_t, y_t).
  5. On a drift event, optionally reset the model (adaptive retrain).

Returns a per-stream `RunResult` with the time series of accuracy, latency,
and detection events. Detection delay vs. ground-truth drift points is
computed downstream by `experiments/metrics.py`.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from src.drift.base import DriftDetector, DriftEvent
from src.models.base import OnlineModel


@dataclass
class RunResult:
    detector: str
    model: str
    n_samples: int
    accuracy: float
    accuracy_curve: np.ndarray
    drift_events: list[DriftEvent] = field(default_factory=list)
    inference_latency_ns: np.ndarray = field(default_factory=lambda: np.empty(0))
    train_latency_ns: np.ndarray = field(default_factory=lambda: np.empty(0))
    retrains: int = 0
    elapsed_s: float = 0.0


def prequential_run(
    model: OnlineModel,
    detector: DriftDetector,
    X: np.ndarray,
    y: np.ndarray,
    *,
    warmup: int = 200,
    adaptive: bool = True,
    accuracy_window: int = 500,
) -> RunResult:
    """Run a single prequential evaluation. Returns RunResult."""
    n = X.shape[0]
    correct_window: list[int] = []
    accuracy_curve = np.zeros(n, dtype=np.float32)
    pred_latency = np.zeros(n, dtype=np.int64)
    train_latency = np.zeros(n, dtype=np.int64)
    drifts: list[DriftEvent] = []
    n_retrain = 0

    # Warmup fit on the first `warmup` samples in mini-batches of 1.
    if warmup > 0:
        model.partial_fit(X[:warmup], y[:warmup])

    t0 = time.perf_counter()
    for t in range(warmup, n):
        x_t = X[t : t + 1]
        y_t = int(y[t])

        pt = time.perf_counter_ns()
        y_hat = int(model.predict(x_t)[0])
        pred_latency[t] = time.perf_counter_ns() - pt

        err = int(y_hat != y_t)
        correct_window.append(1 - err)
        if len(correct_window) > accuracy_window:
            correct_window.pop(0)
        accuracy_curve[t] = sum(correct_window) / len(correct_window)

        ev = detector.update(err, x_t[0])
        if ev is not None:
            drifts.append(ev)
            if adaptive:
                model.reset()
                n_retrain += 1

        tt = time.perf_counter_ns()
        model.partial_fit(x_t, np.array([y_t]))
        train_latency[t] = time.perf_counter_ns() - tt

    elapsed = time.perf_counter() - t0
    valid = accuracy_curve[warmup:]
    overall_acc = float(valid.mean()) if valid.size else 0.0

    return RunResult(
        detector=detector.name,
        model=model.name,
        n_samples=n,
        accuracy=overall_acc,
        accuracy_curve=accuracy_curve,
        drift_events=drifts,
        inference_latency_ns=pred_latency[warmup:],
        train_latency_ns=train_latency[warmup:],
        retrains=n_retrain,
        elapsed_s=elapsed,
    )
