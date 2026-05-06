from __future__ import annotations

from src.models.base import OnlineModel
from src.models.online import HoeffdingTreeAdapter, LogisticBaseline, _StandardizedSGD

_REGISTRY: dict[str, type[OnlineModel]] = {
    "sgd_logistic": _StandardizedSGD,
    "logistic_batch": LogisticBaseline,
    "hoeffding_tree": HoeffdingTreeAdapter,
}


def build_model(name: str, **kwargs) -> OnlineModel:
    key = name.lower()
    if key not in _REGISTRY:
        raise ValueError(f"Unknown model '{name}'. Available: {sorted(_REGISTRY)}")
    return _REGISTRY[key](**kwargs)


def list_models() -> list[str]:
    return sorted(_REGISTRY)
