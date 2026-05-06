"""Full benchmark: every (model, detector) pair on every stream, with stats.

Runs prequential evaluation across:
    - Models:    sgd_logistic, hoeffding_tree, logistic_batch
    - Detectors: adwin, ddm, eddm, kswin, page_hinkley, hybrid
    - Streams:   ELEC2 (real), SEA (synthetic abrupt), Hyperplane (synthetic gradual)

Logs every run to MLflow with metrics + artifacts. Aggregates across seeds and
computes Friedman + Nemenyi post-hoc tests over detection-delay and accuracy.
"""

from __future__ import annotations

import argparse
import json
from itertools import product

import mlflow
import numpy as np
import pandas as pd

from src.data.preprocess import load_processed
from src.data.synthetic import hyperplane_stream, sea_stream
from src.drift import build_detector
from src.models import build_model
from src.pipelines.metrics import detection_metrics, latency_summary, throughput
from src.pipelines.prequential import prequential_run
from src.utils.config import EXPERIMENTS_DIR, settings
from src.utils.logging import get_logger

log = get_logger(__name__)


def _stream_iter(name: str, seed: int, n_samples: int = 40_000):
    if name == "elec2":
        _, _, X, y = load_processed()
        return X[:n_samples], y[:n_samples], []
    if name == "sea":
        # Scale drift points proportionally to n_samples.
        ratios = (0.25, 0.5, 0.75)
        drifts = tuple(int(r * n_samples) for r in ratios)
        X, y, drifts = sea_stream(n_samples=n_samples, drift_points=drifts, seed=seed)
        return X, y, drifts
    if name == "hyperplane":
        ratios = (0.375, 0.75)
        drifts = tuple(int(r * n_samples) for r in ratios)
        X, y, drifts = hyperplane_stream(n_samples=n_samples, drift_points=drifts, seed=seed)
        return X, y, drifts
    raise ValueError(name)


def run_one(
    model_name: str, detector_name: str, stream_name: str, seed: int, n_samples: int = 40_000
) -> dict:
    X, y, true_drifts = _stream_iter(stream_name, seed, n_samples=n_samples)
    model = build_model(model_name)
    detector = build_detector(detector_name)

    res = prequential_run(model, detector, X, y, warmup=200, adaptive=True)

    dm = detection_metrics(res.drift_events, true_drifts) if true_drifts else None
    lat = latency_summary(res.inference_latency_ns)
    tput = throughput(res.n_samples, res.elapsed_s)

    record = {
        "model": model_name,
        "detector": detector_name,
        "stream": stream_name,
        "seed": seed,
        "accuracy": res.accuracy,
        "retrains": res.retrains,
        "n_drift_events": len(res.drift_events),
        "throughput_samples_per_s": tput,
        "elapsed_s": res.elapsed_s,
        **{f"latency_{k}": v for k, v in lat.items()},
    }
    if dm is not None:
        record.update(
            {
                "true_drifts": dm.n_true,
                "true_positives": dm.true_positives,
                "false_positives": dm.false_positives,
                "missed": dm.missed,
                "mean_detection_delay": dm.mean_delay,
                "false_positive_rate": dm.false_positive_rate,
                "miss_rate": dm.miss_rate,
            }
        )
    return record


def aggregate(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(EXPERIMENTS_DIR / "results.csv", index=False)
    df.to_json(EXPERIMENTS_DIR / "results.json", orient="records", indent=2)
    return df


def friedman_nemenyi(df: pd.DataFrame, metric: str, lower_is_better: bool) -> dict:
    """Friedman test + Nemenyi post-hoc on detector ranks across (stream,seed) blocks."""
    from scipy.stats import friedmanchisquare

    pivot = df.pivot_table(index=["stream", "seed"], columns="detector", values=metric)
    pivot = pivot.dropna(how="any")
    if pivot.shape[0] < 3 or pivot.shape[1] < 3:
        return {"applicable": False, "reason": "insufficient blocks/groups"}

    ranks = pivot.rank(axis=1, ascending=lower_is_better, method="average")
    avg_ranks = ranks.mean(axis=0).sort_values()

    samples = [pivot[c].to_numpy() for c in pivot.columns]
    stat, p = friedmanchisquare(*samples)

    k, n = pivot.shape[1], pivot.shape[0]
    # Critical-difference (Nemenyi, alpha=0.05) for k methods, n datasets.
    q_alpha_table = {
        2: 1.960,
        3: 2.343,
        4: 2.569,
        5: 2.728,
        6: 2.850,
        7: 2.949,
        8: 3.031,
        9: 3.102,
        10: 3.164,
    }
    q = q_alpha_table.get(k)
    cd = float(q * np.sqrt(k * (k + 1) / (6 * n))) if q else float("nan")

    return {
        "applicable": True,
        "metric": metric,
        "lower_is_better": lower_is_better,
        "n_blocks": int(n),
        "k_methods": int(k),
        "friedman_stat": float(stat),
        "friedman_p": float(p),
        "average_ranks": avg_ranks.to_dict(),
        "critical_difference": cd,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", nargs="+", type=int, default=[42, 1337, 2024])
    p.add_argument("--models", nargs="+", default=["sgd_logistic", "hoeffding_tree"])
    p.add_argument(
        "--detectors",
        nargs="+",
        default=["adwin", "ddm", "eddm", "kswin", "page_hinkley", "hybrid"],
    )
    p.add_argument("--streams", nargs="+", default=["elec2", "sea", "hyperplane"])
    p.add_argument("--no-mlflow", action="store_true")
    p.add_argument(
        "--n-samples", type=int, default=40_000, help="Length of each stream. Default 40000."
    )
    args = p.parse_args()

    if not args.no_mlflow:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(settings.mlflow_experiment_name + "-bench")

    rows: list[dict] = []
    combos = list(product(args.models, args.detectors, args.streams, args.seeds))
    for i, (m, d, s, seed) in enumerate(combos, 1):
        log.info("[%d/%d] model=%s detector=%s stream=%s seed=%s", i, len(combos), m, d, s, seed)
        try:
            rec = run_one(m, d, s, seed, n_samples=args.n_samples)
            rows.append(rec)
            if not args.no_mlflow:
                with mlflow.start_run(run_name=f"{m}-{d}-{s}-{seed}", nested=False):
                    mlflow.log_params({"model": m, "detector": d, "stream": s, "seed": seed})
                    mlflow.log_metrics(
                        {
                            k: v
                            for k, v in rec.items()
                            if isinstance(v, int | float) and not np.isnan(v)
                        }
                    )
        except Exception as e:
            log.exception("run failed: %s", e)

    df = aggregate(rows)
    log.info("Aggregated %d runs -> %s", len(df), EXPERIMENTS_DIR / "results.csv")

    stats = {
        "accuracy": friedman_nemenyi(df, "accuracy", lower_is_better=False),
        "mean_detection_delay": friedman_nemenyi(
            df[df["stream"] != "elec2"], "mean_detection_delay", lower_is_better=True
        ),
        "false_positive_rate": friedman_nemenyi(
            df[df["stream"] != "elec2"], "false_positive_rate", lower_is_better=True
        ),
    }
    (EXPERIMENTS_DIR / "stats.json").write_text(json.dumps(stats, indent=2, default=str))
    log.info("Statistical tests written to %s", EXPERIMENTS_DIR / "stats.json")


if __name__ == "__main__":
    main()
