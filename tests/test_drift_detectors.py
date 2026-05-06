from __future__ import annotations

import numpy as np
import pytest

from src.drift import build_detector
from src.drift.factory import list_detectors


@pytest.mark.parametrize("name", list_detectors())
def test_detector_constructable(name: str) -> None:
    d = build_detector(name)
    assert d.name


@pytest.mark.parametrize("name", list_detectors())
def test_no_drift_on_iid_zeros(name: str) -> None:
    """A detector should not flag drift on a long, perfectly stationary error stream of zeros."""
    d = build_detector(name)
    fired = 0
    rng = np.random.default_rng(0)
    for _ in range(2000):
        x = rng.standard_normal(8).astype(np.float32)
        if d.update(0, x) is not None:
            fired += 1
    # Most detectors should be silent on a flat stream. Distribution-based
    # KSWIN can fire occasionally on synthetic norms; bound liberally.
    assert fired <= 5, f"{name} fired {fired} times on stationary stream"


@pytest.mark.parametrize("name", ["adwin", "ddm", "eddm", "page_hinkley", "hybrid"])
def test_detects_abrupt_error_jump(name: str) -> None:
    """After 1500 zero-error steps, switching to high error should be detected."""
    d = build_detector(name)
    rng = np.random.default_rng(1)
    detected_at = None
    for t in range(3000):
        err = 0 if t < 1500 else int(rng.random() < 0.85)
        ev = d.update(err, rng.standard_normal(8).astype(np.float32))
        if ev is not None and t >= 1500:
            detected_at = t
            break
    assert detected_at is not None, f"{name} failed to detect abrupt drift"
    assert detected_at - 1500 < 800, f"{name} delay too high: {detected_at - 1500}"


def test_hybrid_cooldown_suppresses_storm() -> None:
    d = build_detector("hybrid", cooldown=2000)
    rng = np.random.default_rng(2)
    fires = 0
    for _ in range(3000):
        if d.update(int(rng.random() < 0.9), rng.standard_normal(4).astype(np.float32)):
            fires += 1
    assert fires <= 2, f"hybrid cooldown failed; fired {fires} times"


def test_unknown_detector_raises() -> None:
    with pytest.raises(ValueError):
        build_detector("nonsense")
