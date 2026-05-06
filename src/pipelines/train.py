"""Train a baseline model on the warmup window and log to MLflow.

This script produces the *initial* registered model used by the API service.
Online updates and adaptive retraining happen in the streaming runtime.
"""

from __future__ import annotations

import argparse
import json

import joblib
import mlflow
from sklearn.metrics import accuracy_score, f1_score, log_loss, roc_auc_score
from sklearn.model_selection import train_test_split

from src.data.preprocess import load_processed
from src.models import build_model, list_models
from src.utils.config import EXPERIMENTS_DIR, settings
from src.utils.logging import get_logger

log = get_logger(__name__)


def _eval(y_true, y_pred, y_proba) -> dict[str, float]:
    out = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred)),
    }
    try:
        out["auc"] = float(roc_auc_score(y_true, y_proba[:, 1]))
        out["logloss"] = float(log_loss(y_true, y_proba, labels=[0, 1]))
    except (ValueError, IndexError):
        out["auc"] = float("nan")
        out["logloss"] = float("nan")
    return out


def train(model_name: str, register: bool = True) -> dict:
    X_w, y_w, _, _ = load_processed()
    X_tr, X_te, y_tr, y_te = train_test_split(
        X_w, y_w, test_size=0.2, random_state=settings.random_seed, stratify=y_w
    )

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)

    with mlflow.start_run(run_name=f"warmup-{model_name}") as run:
        mlflow.log_params({"model": model_name, "warmup_train_size": len(X_tr)})

        model = build_model(model_name)
        model.partial_fit(X_tr, y_tr)

        proba = model.predict_proba(X_te)
        pred = model.predict(X_te)
        metrics = _eval(y_te, pred, proba)
        mlflow.log_metrics(metrics)
        log.info("Eval %s: %s", model_name, metrics)

        artifact_dir = EXPERIMENTS_DIR / "models"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        path = artifact_dir / f"{model_name}.joblib"
        joblib.dump(model, path)
        mlflow.log_artifact(str(path), artifact_path="model")

        meta = {"model": model_name, "metrics": metrics, "run_id": run.info.run_id}
        meta_path = artifact_dir / f"{model_name}.meta.json"
        meta_path.write_text(json.dumps(meta, indent=2))
        mlflow.log_artifact(str(meta_path), artifact_path="model")

        if register:
            try:
                mlflow.register_model(
                    model_uri=f"runs:/{run.info.run_id}/model",
                    name=settings.model_name,
                )
            except Exception as e:
                log.warning("Model registry not available, skipping: %s", e)

        return meta


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="sgd_logistic", choices=list_models())
    p.add_argument("--no-register", action="store_true")
    args = p.parse_args()
    train(args.model, register=not args.no_register)


if __name__ == "__main__":
    main()
