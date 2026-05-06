from __future__ import annotations

import numpy as np

from src.data.synthetic import hyperplane_stream, sea_stream


def test_sea_shape_and_drifts() -> None:
    X, y, drifts = sea_stream(n_samples=1000, drift_points=(300, 600), noise=0.0)
    assert X.shape == (1000, 3)
    assert y.shape == (1000,)
    assert drifts == [300, 600]
    assert set(np.unique(y).tolist()).issubset({0, 1})


def test_sea_concept_changes_at_boundary() -> None:
    """Below threshold should map to 1 in the first concept (thr=8) and 0 in second (thr=7)."""
    X, y, _ = sea_stream(n_samples=4000, drift_points=(2000,), noise=0.0)
    pre = ((X[:2000, 0] + X[:2000, 1]) <= 8.0).astype(np.int8)
    post = ((X[2000:, 0] + X[2000:, 1]) <= 9.0).astype(np.int8)  # second concept thr=9
    assert np.all(y[:2000] == pre)
    assert np.all(y[2000:] == post)


def test_hyperplane_shape() -> None:
    X, y, drifts = hyperplane_stream(n_samples=500, n_features=5, drift_points=(250,), noise=0.0)
    assert X.shape == (500, 5)
    assert len(drifts) == 1
