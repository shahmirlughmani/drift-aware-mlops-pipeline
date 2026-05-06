from __future__ import annotations

from src.drift.base import DriftDetector
from src.drift.detectors import (
    ADWINDetector,
    DDMDetector,
    EDDMDetector,
    HybridDriftDetector,
    KSWINDetector,
    PageHinkleyDetector,
)

_REGISTRY: dict[str, type[DriftDetector]] = {
    "adwin": ADWINDetector,
    "ddm": DDMDetector,
    "eddm": EDDMDetector,
    "kswin": KSWINDetector,
    "page_hinkley": PageHinkleyDetector,
    "hybrid": HybridDriftDetector,
}


def build_detector(name: str, **kwargs) -> DriftDetector:
    key = name.lower().replace("-", "_")
    if key not in _REGISTRY:
        raise ValueError(f"Unknown drift detector '{name}'. Available: {sorted(_REGISTRY)}")
    return _REGISTRY[key](**kwargs)


def list_detectors() -> list[str]:
    return sorted(_REGISTRY)
