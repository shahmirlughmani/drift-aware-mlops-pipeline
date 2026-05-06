"""Concept-drift detectors.

Wraps `river` implementations of the canonical detectors and adds a novel
**HybridDriftDetector** that combines a performance-based signal (DDM) with a
distribution-based signal (KSWIN) under a consensus-or-confidence rule.

References:
- Bifet & Gavalda (2007). Learning from time-changing data with adaptive
  windowing. *SDM*. (ADWIN)
- Gama et al. (2004). Learning with drift detection. *SBIA*. (DDM)
- Baena-Garcia et al. (2006). Early drift detection method. *ECML PKDD WS*. (EDDM)
- Raab et al. (2020). Reactive Soft Prototype Computing for Concept Drift Streams.
  *Neurocomputing*. (KSWIN)
- Page (1954). Continuous inspection schemes. *Biometrika*. (Page-Hinkley)
"""

from __future__ import annotations

from typing import Any

import numpy as np
from river import drift

from src.drift.base import DriftDetector, DriftEvent
from src.utils.config import settings

# ---------------- Performance-based wrappers (operate on errors) ---------------- #


class _RiverPerfDetector(DriftDetector):
    """Adapter for any river detector that accepts a binary/continuous stat per step."""

    def __init__(self, impl: Any, name: str) -> None:
        self.impl = impl
        self.name = name
        self._t = 0

    def update(self, error: int, x: np.ndarray | None = None) -> DriftEvent | None:
        self.impl.update(error)
        self._t += 1
        if self.impl.drift_detected:
            ev = DriftEvent(index=self._t, severity=1.0, detector=self.name)
            return ev
        return None

    def reset(self) -> None:
        self.impl._reset() if hasattr(self.impl, "_reset") else None
        self._t = 0


class ADWINDetector(_RiverPerfDetector):
    def __init__(self, delta: float = 0.002) -> None:
        super().__init__(drift.ADWIN(delta=delta), name="ADWIN")


class DDMDetector(_RiverPerfDetector):
    def __init__(
        self, warm_start: int = 30, warning_threshold: float = 2.0, drift_threshold: float = 3.0
    ) -> None:
        super().__init__(
            drift.binary.DDM(
                warm_start=warm_start,
                warning_threshold=warning_threshold,
                drift_threshold=drift_threshold,
            ),
            name="DDM",
        )


class EDDMDetector(_RiverPerfDetector):
    def __init__(self, warm_start: int = 30, alpha: float = 0.95, beta: float = 0.9) -> None:
        super().__init__(
            drift.binary.EDDM(warm_start=warm_start, alpha=alpha, beta=beta),
            name="EDDM",
        )


class PageHinkleyDetector(_RiverPerfDetector):
    def __init__(
        self,
        min_instances: int = 30,
        delta: float = 0.005,
        threshold: float = 50.0,
        alpha: float = 1 - 1e-4,
    ) -> None:
        super().__init__(
            drift.PageHinkley(
                min_instances=min_instances,
                delta=delta,
                threshold=threshold,
                alpha=alpha,
            ),
            name="PageHinkley",
        )


# ---------------- Distribution-based detector (operates on a univariate stat) ---------------- #


class KSWINDetector(DriftDetector):
    """Kolmogorov-Smirnov windowing test on a univariate streaming statistic.

    For multivariate `x`, we collapse to a stable scalar (L2 norm of the
    standardized feature vector). This is a common practical reduction.
    """

    name = "KSWIN"

    def __init__(
        self,
        alpha: float = 0.005,
        window_size: int = 100,
        stat_size: int = 30,
        seed: int = settings.random_seed,
    ) -> None:
        self.impl = drift.KSWIN(
            alpha=alpha, window_size=window_size, stat_size=stat_size, seed=seed
        )
        self._t = 0
        # Running mean / std for standardization (Welford's algorithm).
        self._mean = 0.0
        self._m2 = 0.0
        self._n = 0

    def _scalar(self, x: np.ndarray | None, error: int) -> float:
        if x is None:
            return float(error)
        # Welford update on L2 norm of x.
        v = float(np.linalg.norm(x))
        self._n += 1
        delta = v - self._mean
        self._mean += delta / self._n
        self._m2 += delta * (v - self._mean)
        var = self._m2 / max(1, self._n - 1)
        std = float(np.sqrt(var)) or 1.0
        return (v - self._mean) / std

    def update(self, error: int, x: np.ndarray | None = None) -> DriftEvent | None:
        s = self._scalar(x, error)
        self.impl.update(s)
        self._t += 1
        if self.impl.drift_detected:
            return DriftEvent(index=self._t, severity=1.0, detector=self.name)
        return None

    def reset(self) -> None:
        self.impl = drift.KSWIN(
            alpha=0.005, window_size=100, stat_size=30, seed=settings.random_seed
        )
        self._t = 0
        self._mean = self._m2 = 0.0
        self._n = 0


# ---------------- Novel contribution: HybridDriftDetector ---------------- #


class HybridDriftDetector(DriftDetector):
    """Hybrid performance + distribution detector with consensus voting.

    Rationale:
        - Performance-based detectors (DDM, EDDM, Page-Hinkley) react quickly
          to drifts that *hurt accuracy*, but miss "virtual" drifts (P(X) shifts
          without P(y|X) shifts) and are blind during cold-start when ground
          truth is sparse.
        - Distribution-based detectors (KSWIN) flag P(X) shifts but generate
          false positives on harmless covariate fluctuations.

    Decision rule (this work):
        Maintain DDM warning/drift state and KSWIN drift state. Emit a HARD
        drift event when (a) BOTH sub-detectors fire within `consensus_window`
        steps, OR (b) DDM enters drift state with a posterior error rate
        above `confidence_threshold`. The cooldown suppresses re-firings for
        `cooldown` steps to avoid retraining storms.

    This combines low false-positive rate (consensus) with fast reaction to
    high-impact accuracy drops (confidence override).
    """

    name = "Hybrid"

    def __init__(
        self,
        consensus_window: int = 200,
        confidence_threshold: float = 0.35,
        cooldown: int = 500,
        ddm_drift_threshold: float = 3.0,
        kswin_alpha: float = 0.005,
    ) -> None:
        self.ddm = DDMDetector(drift_threshold=ddm_drift_threshold)
        self.kswin = KSWINDetector(alpha=kswin_alpha)
        self.consensus_window = consensus_window
        self.confidence_threshold = confidence_threshold
        self.cooldown = cooldown

        self._t = 0
        self._last_drift_t = -(10**9)
        self._last_ddm_signal = -(10**9)
        self._last_kswin_signal = -(10**9)
        self._err_window: list[int] = []
        self._err_window_size = 200

    def _posterior_error(self) -> float:
        if not self._err_window:
            return 0.0
        return sum(self._err_window) / len(self._err_window)

    def update(self, error: int, x: np.ndarray | None = None) -> DriftEvent | None:
        self._t += 1
        self._err_window.append(int(error))
        if len(self._err_window) > self._err_window_size:
            self._err_window.pop(0)

        ddm_event = self.ddm.update(error, x)
        kswin_event = self.kswin.update(error, x)

        if ddm_event is not None:
            self._last_ddm_signal = self._t
        if kswin_event is not None:
            self._last_kswin_signal = self._t

        # Cooldown -> suppress.
        if self._t - self._last_drift_t < self.cooldown:
            return None

        consensus = (
            abs(self._last_ddm_signal - self._last_kswin_signal) <= self.consensus_window
            and max(self._last_ddm_signal, self._last_kswin_signal) == self._t
        )
        confidence_override = (
            ddm_event is not None and self._posterior_error() >= self.confidence_threshold
        )

        if consensus or confidence_override:
            self._last_drift_t = self._t
            severity = self._posterior_error()
            return DriftEvent(index=self._t, severity=severity, detector=self.name)
        return None

    def reset(self) -> None:
        self.ddm.reset()
        self.kswin.reset()
        self._t = 0
        self._last_drift_t = -(10**9)
        self._last_ddm_signal = self._last_kswin_signal = -(10**9)
        self._err_window.clear()
