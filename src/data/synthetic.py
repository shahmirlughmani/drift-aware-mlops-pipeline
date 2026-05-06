"""Synthetic streams with injected concept drift, used for controlled detector evaluation.

We implement two classics from the drift literature:

* SEA concepts (Street & Kim, 2001) - 4 concepts with abrupt switches.
* Rotating hyperplane (Hulten et al., 2001) - gradual rotational drift.

These are injected with **known** drift points so we can compute detection delay
and false-positive rate analytically (impossible on real data).
"""

from __future__ import annotations

import numpy as np

from src.utils.config import settings


def sea_stream(
    n_samples: int = 40_000,
    drift_points: tuple[int, ...] = (10_000, 20_000, 30_000),
    noise: float = 0.10,
    seed: int = settings.random_seed,
) -> tuple[np.ndarray, np.ndarray, list[int]]:
    """Four SEA concepts with thresholds {8, 9, 7, 9.5} on x1+x2."""
    rng = np.random.default_rng(seed)
    thresholds = [8.0, 9.0, 7.0, 9.5]
    X = rng.uniform(0.0, 10.0, size=(n_samples, 3)).astype(np.float32)

    boundaries = (0, *drift_points, n_samples)
    y = np.empty(n_samples, dtype=np.int8)
    for i in range(len(boundaries) - 1):
        a, b = boundaries[i], boundaries[i + 1]
        thr = thresholds[i % len(thresholds)]
        seg = (X[a:b, 0] + X[a:b, 1]) <= thr
        flip = rng.random(b - a) < noise
        y[a:b] = np.where(flip, ~seg, seg).astype(np.int8)
    return X, y, list(drift_points)


def hyperplane_stream(
    n_samples: int = 40_000,
    n_features: int = 10,
    drift_speed: float = 0.001,
    drift_points: tuple[int, ...] = (15_000, 30_000),
    noise: float = 0.05,
    seed: int = settings.random_seed,
) -> tuple[np.ndarray, np.ndarray, list[int]]:
    """Hyperplane normal w drifts continuously; magnitude resets at drift points."""
    rng = np.random.default_rng(seed)
    X = rng.uniform(0.0, 1.0, size=(n_samples, n_features)).astype(np.float32)
    w = rng.uniform(-1.0, 1.0, size=n_features).astype(np.float32)
    threshold = 0.5 * w.sum()
    y = np.empty(n_samples, dtype=np.int8)
    drift_set = set(drift_points)
    for t in range(n_samples):
        if t in drift_set:
            w = rng.uniform(-1.0, 1.0, size=n_features).astype(np.float32)
            threshold = 0.5 * w.sum()
        w += drift_speed * rng.standard_normal(n_features).astype(np.float32)
        score = X[t] @ w
        label = int(score > threshold)
        if rng.random() < noise:
            label ^= 1
        y[t] = label
    return X, y, list(drift_points)
