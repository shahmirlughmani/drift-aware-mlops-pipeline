#!/usr/bin/env bash
# Quick smoke test for the running stack. Run after `docker compose up -d`.
set -euo pipefail

API="${API:-http://localhost:8000}"
PROM="${PROM:-http://localhost:9090}"
GRAFANA="${GRAFANA:-http://localhost:3000}"
MLFLOW="${MLFLOW:-http://localhost:5000}"

echo "==> /health"
curl -fsS "$API/health" | tee /dev/null && echo

echo
echo "==> /predict"
curl -fsS -X POST "$API/predict" \
    -H "Content-Type: application/json" \
    -d '{"features":[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8],"label":1}' | tee /dev/null && echo

echo
echo "==> /metrics (head)"
curl -fsS "$API/metrics" | head -n 12

echo
echo "==> Prometheus targets"
curl -fsS "$PROM/api/v1/targets" | python -c "import json,sys; d=json.load(sys.stdin); [print(t['labels'].get('job','?'), '->', t['health']) for t in d['data']['activeTargets']]"

echo
echo "==> Grafana ping"
curl -fsS -u admin:admin "$GRAFANA/api/health" | tee /dev/null && echo

echo
echo "==> MLflow"
curl -fsS "$MLFLOW/" -o /dev/null && echo "mlflow OK"

echo
echo "all checks passed"
