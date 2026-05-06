# ADR 0002 — MLflow with a Postgres backend, artefact volume

**Status:** Accepted (2026-04)
**Deciders:** Zaid · Shahmir Asif · AbuBakr Shahid

## Context

MLflow needs a tracking store (parameters, metrics, run metadata) and an
artefact store (model files, plots, logs). The default file-based backend
is fine for a single user but breaks under any concurrent writer — and we
have at least three: the trainer container, the drift monitor (logging
`drift-triggered` runs), and CI smoke runs.

## Decision

Run the MLflow tracking server with **Postgres 16** as the backend store and
a Docker named volume (`mlflow_artifacts`) as the artefact store.

```yaml
mlflow:
  command: >
    mlflow server
    --backend-store-uri postgresql://mlflow:mlflow@postgres:5432/mlflow
    --artifacts-destination /mlflow/artifacts
    --host 0.0.0.0
```

Postgres has its own healthcheck; MLflow waits on `postgres: condition: service_healthy`.

## Alternatives considered

| Option | Rejected because |
|---|---|
| File backend (`./mlruns`) | Race conditions under concurrent writers |
| SQLite backend | Single-writer only; same problem as file |
| S3 artefacts | Pulls in AWS credentials at evaluation time; out of scope for the local demo. The codebase keeps the artefact path configurable via `MLFLOW_ARTIFACT_ROOT` so the production deployment can switch in S3 without code changes. |
| Self-hosted MinIO | Adds a service for negligible benefit at our scale |

## Consequences

**Positive**
- Reproducibility: any container can write runs
- Concurrent CI runs do not corrupt the tracking store
- Postgres dump = full experiment provenance backup

**Negative**
- One more service to start (Postgres)
- Slightly higher cold-start time (~10 s for healthcheck)

## Operational notes

- Tracking URI inside the compose network: `http://mlflow:5000`
- From the host: `http://localhost:5000`
- Backup: `pg_dump -U mlflow mlflow > mlflow-$(date +%F).sql`
