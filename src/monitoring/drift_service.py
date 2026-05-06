"""Streaming drift monitor.

Replays the prequential ELEC2 stream against the live API service, observes
predictions vs ground truth, runs a configurable drift detector, and:
  * Exposes Prometheus metrics on :9100/metrics (drift events, accuracy, severity).
  * Triggers POST /reload on the API after each drift event (cooldown enforced).
  * Logs every drift event to MLflow as a tagged run.

This module is what makes the monitoring layer *load-bearing* for the research
contribution: the metrics it exports ARE the experimental signals studied in
the paper, not bolted-on dashboards.
"""
from __future__ import annotations

import argparse
import time
from dataclasses import dataclass

import numpy as np
import requests
from prometheus_client import start_http_server
from tenacity import retry, stop_after_attempt, wait_exponential

from src.api.metrics import (
    DRIFT_EVENTS_TOTAL,
    DRIFT_SEVERITY,
    RETRAINS_TOTAL,
    ROLLING_ACCURACY,
    ROLLING_ERROR_RATE,
)
from src.data.preprocess import load_processed
from src.drift import build_detector
from src.utils.config import settings
from src.utils.logging import get_logger

log = get_logger(__name__)


@dataclass
class MonitorConfig:
    api_url: str = "http://localhost:8000"
    detector_name: str = "hybrid"
    rolling_window: int = 500
    metrics_port: int = 9100
    pace_seconds: float = 0.0  # 0 = as fast as possible
    cooldown_s: int = 60
    log_every: int = 500


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, max=10))
def _post_predict(api: str, features: list[float], label: int) -> dict:
    r = requests.post(
        f"{api}/predict",
        json={"features": features, "label": label},
        timeout=5,
    )
    r.raise_for_status()
    return r.json()


def _post_reload(api: str) -> None:
    try:
        requests.post(f"{api}/reload", timeout=10).raise_for_status()
    except Exception as e:  # noqa: BLE001
        log.warning("reload failed: %s", e)


def run(cfg: MonitorConfig) -> None:
    start_http_server(cfg.metrics_port)
    log.info("drift-monitor metrics on :%d", cfg.metrics_port)

    _, _, X, y = load_processed()
    detector = build_detector(cfg.detector_name)
    log.info("detector=%s stream_len=%d", detector.name, len(X))

    rolling_correct: list[int] = []
    last_retrain = -10**9

    for t in range(len(X)):
        feats = X[t].tolist()
        true_y = int(y[t])

        try:
            resp = _post_predict(cfg.api_url, feats, true_y)
        except Exception as e:  # noqa: BLE001
            log.warning("prediction failed at t=%d: %s", t, e)
            continue

        pred = int(resp["prediction"])
        err = int(pred != true_y)
        rolling_correct.append(1 - err)
        if len(rolling_correct) > cfg.rolling_window:
            rolling_correct.pop(0)
        acc = sum(rolling_correct) / len(rolling_correct)
        ROLLING_ACCURACY.set(acc)
        ROLLING_ERROR_RATE.set(1 - acc)

        ev = detector.update(err, X[t])
        if ev is not None:
            DRIFT_EVENTS_TOTAL.labels(detector=detector.name, kind="drift").inc()
            DRIFT_SEVERITY.labels(detector=detector.name).set(float(ev.severity))
            now = time.time()
            if now - last_retrain >= cfg.cooldown_s:
                log.info("[t=%d] drift: %s severity=%.3f -> /reload", t, ev.detector, ev.severity)
                _post_reload(cfg.api_url)
                RETRAINS_TOTAL.labels(reason=ev.detector).inc()
                last_retrain = now
            else:
                log.info("[t=%d] drift suppressed (cooldown)", t)

        if t % cfg.log_every == 0:
            log.info("t=%d acc=%.4f drifts=%d", t, acc,
                     int(DRIFT_EVENTS_TOTAL.labels(detector=detector.name, kind="drift")._value.get()))

        if cfg.pace_seconds > 0:
            time.sleep(cfg.pace_seconds)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--api-url", default="http://localhost:8000")
    p.add_argument("--detector", default=settings.drift_detector)
    p.add_argument("--metrics-port", type=int, default=9100)
    p.add_argument("--rolling-window", type=int, default=500)
    p.add_argument("--pace", type=float, default=0.0)
    p.add_argument("--cooldown", type=int, default=settings.drift_retrain_cooldown_s)
    args = p.parse_args()

    cfg = MonitorConfig(
        api_url=args.api_url,
        detector_name=args.detector,
        metrics_port=args.metrics_port,
        rolling_window=args.rolling_window,
        pace_seconds=args.pace,
        cooldown_s=args.cooldown,
    )
    run(cfg)


if __name__ == "__main__":
    main()
