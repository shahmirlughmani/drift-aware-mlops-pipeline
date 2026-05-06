from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Boot the API with a tiny model planted in the local artifact path."""
    import os

    from src.models import build_model
    from src.utils.config import EXPERIMENTS_DIR

    rng = np.random.default_rng(0)
    X = rng.standard_normal((400, 8)).astype(np.float32)
    y = (X[:, 0] + X[:, 1] > 0).astype(np.int8)
    m = build_model("sgd_logistic")
    m.partial_fit(X, y)

    artifact_dir: Path = EXPERIMENTS_DIR / "models"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(m, artifact_dir / "sgd_logistic.joblib")

    # Force MLflow path off.
    os.environ["MLFLOW_TRACKING_URI"] = "http://127.0.0.1:1"
    from src.api.main import app  # late import after env set

    with TestClient(app) as c:
        yield c


def test_health_returns_ok(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in {"ok", "degraded"}


def test_predict_returns_label_and_probability(client: TestClient) -> None:
    r = client.post("/predict", json={"features": [0.0] * 8})
    assert r.status_code == 200
    body = r.json()
    assert body["prediction"] in (0, 1)
    assert 0.0 <= body["probability"] <= 1.0


def test_predict_with_label_updates_model(client: TestClient) -> None:
    r = client.post("/predict", json={"features": [1.0] * 8, "label": 1})
    assert r.status_code == 200


def test_metrics_endpoint(client: TestClient) -> None:
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"ml_predictions_total" in r.content
