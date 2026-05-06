"""Prometheus metric definitions for the inference + drift services.

Custom metrics (alongside the FastAPI auto-instrumentor) capture the
domain signals we need on the dashboards: predictions, errors, drift events.
"""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

# Counters
PREDICTIONS_TOTAL = Counter(
    "ml_predictions_total",
    "Total predictions served, partitioned by label.",
    ["predicted_label"],
)
PREDICTION_ERRORS_TOTAL = Counter(
    "ml_prediction_errors_total",
    "Total mispredictions confirmed by ground truth.",
)
DRIFT_EVENTS_TOTAL = Counter(
    "ml_drift_events_total",
    "Drift events fired, partitioned by detector.",
    ["detector", "kind"],  # kind in {warning, drift}
)
RETRAINS_TOTAL = Counter(
    "ml_retrains_total",
    "Adaptive retraining triggers executed.",
    ["reason"],
)

# Gauges
MODEL_VERSION_INFO = Gauge(
    "ml_model_version_info",
    "Always 1; the version label carries the deployed model version.",
    ["version", "source"],
)
ROLLING_ACCURACY = Gauge(
    "ml_rolling_accuracy",
    "Rolling-window accuracy reported by the drift monitor.",
)
ROLLING_ERROR_RATE = Gauge(
    "ml_rolling_error_rate",
    "Rolling-window error rate reported by the drift monitor.",
)
DRIFT_SEVERITY = Gauge(
    "ml_drift_severity",
    "Last drift event severity score reported by detectors.",
    ["detector"],
)

# Histograms
INFERENCE_LATENCY = Histogram(
    "ml_inference_latency_seconds",
    "Wall-clock latency of /predict, including pre/post-processing.",
    buckets=(0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)
ONLINE_UPDATE_LATENCY = Histogram(
    "ml_online_update_latency_seconds",
    "Latency of partial_fit on each ground-truth observation.",
    buckets=(0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)
