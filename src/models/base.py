"""Unified online model interface.

We deliberately wrap heterogeneous backends (scikit-learn, river) behind a
single `partial_fit` / `predict_proba` contract so the prequential loop is
backend-agnostic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class OnlineModel(ABC):
    name: str = "base"

    @abstractmethod
    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> None: ...

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray: ...

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray: ...

    @abstractmethod
    def reset(self) -> None: ...
