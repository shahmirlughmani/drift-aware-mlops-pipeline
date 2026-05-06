"""FastAPI inference service with Prometheus metrics + online updates."""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.metrics import (
    INFERENCE_LATENCY,
    MODEL_VERSION_INFO,
    ONLINE_UPDATE_LATENCY,
    PREDICTION_ERRORS_TOTAL,
    PREDICTIONS_TOTAL,
)
from src.api.model_registry import LoadedModel, load
from src.api.schemas import HealthResponse, PredictRequest, PredictResponse, ReloadResponse
from src.utils.config import settings
from src.utils.logging import get_logger

log = get_logger(__name__)

_state: dict[str, object] = {"model": None, "started_at": time.time(), "lock": asyncio.Lock()}


@asynccontextmanager
async def _lifespan(app: FastAPI):
    try:
        loaded: LoadedModel = load()
        _state["model"] = loaded
        MODEL_VERSION_INFO.labels(version=loaded.version, source=loaded.source).set(1)
        log.info(
            "Service ready (model=%s v=%s src=%s)",
            settings.model_name,
            loaded.version,
            loaded.source,
        )
    except Exception as e:
        log.exception("startup failed: %s", e)
        _state["model"] = None
    yield


app = FastAPI(
    title="Drift-Aware MLOps API",
    version="0.1.0",
    description=(
        "Online inference for ELEC2-style streaming classification. "
        "Predictions update model state when ground truth is supplied."
    ),
    lifespan=_lifespan,
)
Instrumentator().instrument(app).expose(app, endpoint="/metrics-fastapi")


def _require_model() -> LoadedModel:
    m = _state.get("model")
    if m is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return m  # type: ignore[return-value]


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    m = _state.get("model")
    return HealthResponse(
        status="ok" if m is not None else "degraded",
        model_loaded=m is not None,
        model_version=m.version if m is not None else "unknown",  # type: ignore[union-attr]
        uptime_s=time.time() - float(_state["started_at"]),  # type: ignore[arg-type]
    )


@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest) -> PredictResponse:
    loaded = _require_model()
    x = np.asarray(req.features, dtype=np.float32).reshape(1, -1)

    t0 = time.perf_counter()
    proba = loaded.model.predict_proba(x)
    pred = int(np.argmax(proba, axis=1)[0])
    p = float(proba[0, pred])
    elapsed = time.perf_counter() - t0
    INFERENCE_LATENCY.observe(elapsed)
    PREDICTIONS_TOTAL.labels(predicted_label=str(pred)).inc()

    if req.label is not None:
        async with _state["lock"]:  # type: ignore[arg-type]
            t1 = time.perf_counter()
            loaded.model.partial_fit(x, np.array([int(req.label)]))
            ONLINE_UPDATE_LATENCY.observe(time.perf_counter() - t1)
            if pred != int(req.label):
                PREDICTION_ERRORS_TOTAL.inc()

    return PredictResponse(
        prediction=pred,
        probability=p,
        model_version=loaded.version,
        inference_us=elapsed * 1e6,
    )


@app.post("/reload", response_model=ReloadResponse)
async def reload_model() -> ReloadResponse:
    try:
        async with _state["lock"]:  # type: ignore[arg-type]
            loaded = load()
            _state["model"] = loaded
            MODEL_VERSION_INFO.labels(version=loaded.version, source=loaded.source).set(1)
        return ReloadResponse(status="reloaded", new_version=loaded.version)
    except Exception as e:
        log.exception("reload failed")
        return ReloadResponse(status="failed", new_version="unknown", detail=str(e))


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
