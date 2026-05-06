from __future__ import annotations

import numpy as np
import pytest

from src.models import build_model, list_models


@pytest.mark.parametrize("name", list_models())
def test_model_partial_fit_and_predict(name: str) -> None:
    rng = np.random.default_rng(0)
    X = rng.standard_normal((200, 5)).astype(np.float32)
    y = (X[:, 0] + X[:, 1] > 0).astype(np.int8)
    m = build_model(name)
    m.partial_fit(X, y)

    proba = m.predict_proba(X[:10])
    assert proba.shape == (10, 2)
    assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-6)

    pred = m.predict(X[:10])
    assert pred.shape == (10,)
    assert set(np.unique(pred).tolist()).issubset({0, 1})


def test_sgd_reset_clears_state() -> None:
    rng = np.random.default_rng(1)
    X = rng.standard_normal((50, 3)).astype(np.float32)
    y = (X[:, 0] > 0).astype(np.int8)
    m = build_model("sgd_logistic")
    m.partial_fit(X, y)
    m.reset()
    # After reset, scaler is unfit -> calling predict should still work without error.
    m.partial_fit(X, y)
    out = m.predict(X[:1])
    assert out.shape == (1,)
