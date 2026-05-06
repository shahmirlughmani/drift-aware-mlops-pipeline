from __future__ import annotations

from src.data.synthetic import sea_stream
from src.drift import build_detector
from src.models import build_model
from src.pipelines.prequential import prequential_run


def test_prequential_runs_end_to_end() -> None:
    X, y, _ = sea_stream(n_samples=2000, drift_points=(800,), noise=0.05, seed=7)
    model = build_model("sgd_logistic")
    detector = build_detector("ddm")
    res = prequential_run(model, detector, X, y, warmup=200, accuracy_window=200)

    assert res.n_samples == 2000
    assert 0.0 <= res.accuracy <= 1.0
    assert res.accuracy_curve.shape == (2000,)
    assert res.inference_latency_ns.size > 0


def test_adaptive_retrain_triggers() -> None:
    """Sharp, low-noise drifts with a permissive hybrid config should fire.

    The point of the test is the prequential->retrain control path, not the
    detector calibration; we choose a synthetic stream where the spike above
    a low confidence threshold is unambiguous.
    """
    X, y, _ = sea_stream(n_samples=6000, drift_points=(2000, 4000), noise=0.0, seed=11)
    model = build_model("sgd_logistic")
    detector = build_detector(
        "hybrid",
        cooldown=200,
        confidence_threshold=0.15,
        consensus_window=500,
        ddm_drift_threshold=2.5,
    )
    res = prequential_run(model, detector, X, y, warmup=200, adaptive=True, accuracy_window=200)
    assert (
        len(res.drift_events) >= 1
    ), f"hybrid did not fire on sharp drift; events={res.drift_events}"
    assert res.retrains >= 1
