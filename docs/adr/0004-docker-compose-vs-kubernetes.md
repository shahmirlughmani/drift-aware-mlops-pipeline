# ADR 0004 — Docker Compose for evaluation, Kubernetes for production

**Status:** Accepted (2026-04)
**Deciders:** Zaid · Shahmir Asif · AbuBakr Shahid

## Context

The course rubric calls for a **fully reproducible** end-to-end pipeline.
"Fully reproducible" means a single command from a clean clone brings up
seven services in a defined order (Postgres → MLflow → trainer → API →
drift monitor → Prometheus → Grafana).

Kubernetes would be production-correct but adds a 30-minute setup cost for
graders without a cluster on hand. Docker Compose covers the same orchestration
contract for a single host with zero infrastructure friction.

## Decision

- **Evaluation / demo target:** `docker-compose.yml` at the repo root.
  Healthchecks and `depends_on: condition: service_healthy` enforce
  ordering. One command (`docker compose up -d --build`) brings everything up.
- **Production target:** Kubernetes via Helm chart (sketched, not shipped).
  Each compose service maps to a Deployment + Service. MLflow → StatefulSet
  with PVC for artefacts. Prometheus + Grafana → kube-prometheus-stack.

The four GHA workflows (`docker.yml`, `deploy.yml`) push images to GHCR
and re-tag them into AWS ECR for the production path. Re-using the same
images means Compose-tested code is what ships.

## Alternatives considered

| Option | Rejected because |
|---|---|
| Kubernetes only | High floor on grading time; cluster requirement |
| Bare metal `pip install` | Misses the rubric's containerisation requirement |
| Nomad / Swarm | Niche orchestrators; little graders' familiarity |

## Consequences

**Positive**
- Reproducibility from a clean clone: one command, ~60 s to healthy stack
- The same image set deploys to ECS via `deploy.yml`
- Easy to extend to k8s later — services already match Deployment-shape

**Negative**
- No native horizontal scaling on the Compose target — the API runs as
  a single replica. For the workloads in our benchmarks (single-stream
  prequential evaluation) this is not a bottleneck.
- No service mesh / mTLS — the trust boundary is the Docker network

## Migration path to Kubernetes

1. `kompose convert -f docker-compose.yml` to seed the manifests.
2. Replace named volumes with PVCs (Postgres + MLflow artefacts).
3. Replace healthchecks with readiness/liveness probes.
4. Move secrets from `.env` to Kubernetes Secrets.
5. Adopt kube-prometheus-stack for the monitoring plane.

A 1–2 day port. Out of scope for this submission.
