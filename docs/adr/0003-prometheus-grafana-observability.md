# ADR 0003 — Prometheus + Grafana for ML-aware observability

**Status:** Accepted (2026-04)
**Deciders:** Zaid · Shahmir Asif · AbuBakr Shahid

## Context

The drift monitor needs a way to expose model-quality signals so they are
**alertable**, **queryable**, and **visualised next to system metrics** —
not buried in application logs.

The team's experience: dashboards built from log scraping go stale. Grafana
panels backed by a PromQL query stay live as long as the metric is being
emitted. We want the same instrumentation toolchain DevOps already uses for
HTTP latency to apply to drift events.

## Decision

Use Prometheus for time-series collection and Grafana for visualisation.
Expose ML-quality metrics as Prometheus primitives directly from the
FastAPI inference service — not via a separate "drift database".

| Metric | Type | Labels |
|---|---|---|
| `ml_predictions_total` | counter | `predicted_label` |
| `ml_prediction_errors_total` | counter | — |
| `ml_drift_events_total` | counter | `detector`, `kind` |
| `ml_retrains_total` | counter | `reason` |
| `ml_rolling_accuracy` | gauge | — |
| `ml_rolling_error_rate` | gauge | — |
| `ml_drift_severity` | gauge | `detector` |
| `ml_model_version_info` | gauge | `version`, `source` |
| `ml_inference_latency_seconds` | histogram | — |
| `ml_online_update_latency_seconds` | histogram | — |

Three Grafana dashboards are provisioned automatically: **Model**, **Drift**,
**Infrastructure**. Four alert rules in `deploy/prometheus/alerts.yml` cover
sustained low accuracy and sustained 5xx error rates.

## Alternatives considered

| Option | Rejected because |
|---|---|
| Push to Datadog / NewRelic | External SaaS; not reproducible from a clean clone |
| Custom drift-events DB | Re-implements time-series storage poorly |
| Log-based metrics (Loki) | Adds a service for what counters do natively |
| StatsD | Older protocol; histograms less expressive than Prometheus' |

## Consequences

**Positive**
- Drift is "just another time series"; same alerting plumbing as latency
- Grafana panels survive container restarts via dashboard provisioning
- The drift monitor's only output channel is `POST /reload` — pure separation
  of concerns: detect → metric → query → adapt

**Negative**
- Pull-based scraping (15 s interval) introduces a small lower bound on
  detection-to-action latency; live we measure ~30 s end-to-end. The system
  is not designed for sub-second drift response, which is fine for our
  classification-streaming use case.

## Operational notes

- Prometheus retention default: 15 days (suitable for the demo; bump for prod)
- Grafana provisioning lives under `deploy/grafana/provisioning/`
- Alert webhooks are not wired by default — add an Alertmanager URL in
  `deploy/prometheus/prometheus.yml` to enable Slack / email / PagerDuty
