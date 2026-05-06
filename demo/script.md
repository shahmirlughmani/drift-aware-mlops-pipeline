# Demo video — shooting script

**Target length:** 6–8 minutes.
**Recording:** OBS Studio (or any screen recorder), 1920×1080, 30 fps, system audio + mic.
**Goal:** show the closed loop end-to-end. Drift is injected, HybridDD fires, the model retrains, accuracy recovers — all on Grafana, in real time.

The script is timed. Lines in `> blockquote` are narration. Steps in **`code`** are exact keystrokes / clicks. Numbers in `[brackets]` are seconds.

---

## Setup before you press record

```bash
cd mlops-project
cp .env.example .env
docker compose down -v          # clean slate
docker compose up -d --build
docker compose logs -f trainer  # wait for "warmup training complete"
```

Open four browser tabs in this order:

1. http://localhost:8000/docs       — FastAPI Swagger
2. http://localhost:5000            — MLflow
3. http://localhost:9090            — Prometheus
4. http://localhost:3000            — Grafana (admin / admin), pin the **Drift** dashboard

Open one terminal next to the Grafana tab. Have `scripts/replay_drift.py` ready in the cwd (the demo driver — see `scripts/` README).

Pre-record check: `curl -s http://localhost:8000/health | jq` returns `{"status":"ok","model_version":"v1"}`.

---

## SCENE 1 · Cold open (0:00 – 0:25)

**On screen:** title slide of the deck, then cut to terminal.

> "Production ML models silently age. In this demo we'll watch a classifier degrade under concept drift — and recover automatically, without a human in the loop. The whole stack is in this repo."

[10] cut to terminal, run: **`docker compose ps`**

> "Seven services: API, MLflow with Postgres, the trainer, the drift monitor, Prometheus, and Grafana. All healthy."

[15] zoom on `Up (healthy)` column.

---

## SCENE 2 · The healthy baseline (0:25 – 1:15)

**On screen:** Grafana → Drift dashboard.

> "Here's the live picture. Top-left: predictions per second. Top-right: rolling accuracy — sitting at about 0.82. Bottom row: drift events counter, and current model version — v1."

[20] hover over the rolling-accuracy panel; show the steady line.

> "Predictions are streaming in from the warmup process. Nothing has drifted yet."

Cut to the terminal:

```bash
curl -s -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"features":[1,2,3,4,5,6,7,8],"label":1}' | jq
```

[10] show response: prediction + `model_version: v1`.

> "Each request returns a prediction and the model version that served it. The version label is also a Prometheus gauge — that's how we'll see the swap later."

---

## SCENE 3 · Inject drift (1:15 – 2:00)

**On screen:** terminal next to Grafana.

> "Now I'm going to inject a concept drift. This script replays a synthetic SEA stream with an abrupt boundary change at sample four thousand."

Run: **`python scripts/replay_drift.py --stream sea --drift-at 4000 --rate 50`**

[5] watch the prediction-rate panel pick up.

> "Fifty samples per second going in. For the first eighty seconds the model is fine."

[60] watch the rolling-accuracy panel start to dip.

> "There — accuracy starts to fall. Errors are accumulating in the rolling window."

---

## SCENE 4 · HybridDD fires (2:00 – 2:50)

**On screen:** Drift dashboard, focus on drift-events panel.

[5] point to the moment the counter increments.

> "And there it is. HybridDD just emitted a hard drift event. Looking at the logs—"

Cut to terminal:

```bash
docker compose logs --tail=20 drift_monitor | grep -E "drift|reload"
```

> "You can see the override path triggered: posterior error climbed past 0.35, DDM was already in drift state, the rule fires. The drift monitor immediately POSTs to /reload."

[10] highlight the `severity` and `posterior_error` fields in the log line.

---

## SCENE 5 · The retrain (2:50 – 4:00)

**On screen:** MLflow tab.

> "Here's MLflow. A new run has just appeared — that's the trainer's response to the reload signal."

[10] click into the new run.

> "It logged its parameters, the training loss curve, and registered a new model. Notice the run name — it's tagged `drift-triggered` — versus the warmup runs which are tagged `scheduled`."

Cut back to API tab and run:

```bash
curl -s http://localhost:8000/health | jq
```

> "The API is now reporting model_version v2. The hot-reload swapped the in-memory artefact without dropping a request."

[10] show the version field flipping from v1 to v2.

---

## SCENE 6 · Recovery (4:00 – 4:50)

**On screen:** Grafana dashboard.

> "And this is the payoff."

[5] watch the rolling-accuracy panel start climbing again.

> "Accuracy is recovering — back into the eighties. The drift-events counter has held steady because the cooldown is engaged: HybridDD won't fire again for 500 steps, even if both sub-detectors signal."

[10] hover the model-version panel.

> "Version-info gauge shows v2 in production. The whole loop — detect, retrain, swap, recover — took about 90 seconds, fully unattended."

---

## SCENE 7 · Alerts and dashboards tour (4:50 – 6:00)

**On screen:** Prometheus → Alerts.

> "Drift is just another time series in Prometheus. We've registered four alerts."

[10] read off: `RollingAccuracyLow`, `RollingAccuracyCritical`, `HighDriftRate`, `APIErrorRateHigh`.

> "If we'd run this for longer or the recovery had stalled, RollingAccuracyLow would have fired and posted to Alertmanager."

Cut to Grafana → Model dashboard.

> "Three dashboards: Model — predictions, errors, accuracy, version. Drift — events by detector, severity, retrains. Infrastructure — request rate and p50, p95, p99 latency."

[15] click each dashboard once, ~5 seconds each.

---

## SCENE 8 · MLflow registry tour (6:00 – 6:40)

**On screen:** MLflow → Models.

> "All trained models are registered. Each run carries its parameters, metrics, and the artefact. The trainer promotes a new model only after a smoke validation pass — see the `validation_passed` tag."

[15] open one run, click through to the metrics.

---

## SCENE 9 · Reproducibility (6:40 – 7:30)

**On screen:** terminal at repo root.

> "Everything you've just seen is reproducible from a clean clone. One command to bring up the stack."

```bash
docker compose up -d --build
```

> "One command to regenerate every paper number from raw seeds."

```bash
make reproduce
```

> "And every push to main runs the smoke experiment in CI. The IEEE paper is rebuilt automatically when paper/ changes. The full pipeline — code, infrastructure, observability, paper — is reproducible from this repo."

---

## SCENE 10 · Outro (7:30 – 7:50)

**On screen:** title slide of the deck again, or the conclusion slide.

> "HybridDD: a consensus-plus-confidence drift detector wired into a closed-loop MLOps stack. Top-tier accuracy, zero false positives on consensus, and a 53 percent reduction in detection delay against Page-Hinkley. Thanks for watching. Code, paper, and these dashboards are in the repo."

Cut.

---

## Recording checklist

Before stopping the recording:

- [ ] `model_version` flipped from v1 to v2 on screen
- [ ] Drift-events counter visibly incremented
- [ ] Rolling accuracy dipped then recovered (full V-shape captured)
- [ ] At least one MLflow run shown in detail
- [ ] At least one Prometheus alert page shown
- [ ] All three Grafana dashboards visible at least briefly
- [ ] Final shot is the conclusion slide

After stopping:

- [ ] Trim head/tail to leave 1 second of silence each side
- [ ] Add 1-line lower-third captions for scene transitions (optional, looks polished)
- [ ] Export 1080p H.264, target ≤ 100 MB
- [ ] Save as `demo/drift-aware-mlops-demo.mp4`
- [ ] Commit a YouTube/Drive link to README.md

## Fallback if a step misbehaves on the day

| Symptom | Fix |
|---|---|
| Drift never fires | Increase `--rate` to 200 or `--drift-magnitude 1.5` in the replay script |
| Reload returns 503 | Check trainer container; `docker compose restart trainer` and re-inject |
| Grafana panel empty | Reload the dashboard tab; Prometheus scrape is 15 s |
| MLflow run not appearing | Check `MLFLOW_TRACKING_URI` env var in `.env` matches the docker-compose service name |
| Latency spike during retrain | Expected — note it on screen; the API still serves v1 during reload |
