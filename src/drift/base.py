"""Common interface for concept-drift detectors.

A detector consumes a sequence of *errors* (1 if the model misclassified
the most recent sample, 0 otherwise) and optionally a feature vector for
distribution-based detectors.

We standardize on a `update(error, x=None) -> DriftEvent | None` API so that
performance-based and distribution-based detectors are interchangeable
inside the prequential loop and the streaming monitor.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DriftEvent:
    index: int  # sample index in the stream when drift fired
    severity: float  # detector-specific score (>= 0)
    detector: str  # name of the detector that fired


class DriftDetector(ABC):
    name: str = "base"

    @abstractmethod
    def update(self, error: int, x: np.ndarray | None = None) -> DriftEvent | None: ...

    @abstractmethod
    def reset(self) -> None: ...

    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.name}>"
