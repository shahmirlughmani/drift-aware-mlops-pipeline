from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    features: list[float] = Field(..., min_length=1, max_length=64)
    label: int | None = Field(None, ge=0, le=1, description="Optional ground-truth for online update.")
    request_id: str | None = None


class PredictResponse(BaseModel):
    prediction: int
    probability: float
    model_version: str
    inference_us: float


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    model_loaded: bool
    model_version: str
    uptime_s: float


class ReloadResponse(BaseModel):
    status: Literal["reloaded", "failed"]
    new_version: str
    detail: str | None = None
