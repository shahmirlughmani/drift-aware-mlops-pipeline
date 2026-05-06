"""Preprocess ELEC2 into a deterministic train/stream split for prequential evaluation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.data.download import LOCAL_NAME, download
from src.utils.config import PROCESSED_DIR, RAW_DIR
from src.utils.logging import get_logger

log = get_logger(__name__)

FEATURE_COLS = [
    "date",
    "day",
    "period",
    "nswprice",
    "nswdemand",
    "vicprice",
    "vicdemand",
    "transfer",
]
TARGET_COL = "class"


def _load_raw() -> pd.DataFrame:
    src = RAW_DIR / LOCAL_NAME
    if not src.exists():
        download()
    df = pd.read_csv(src)
    return df


def _binarize_target(s: pd.Series) -> np.ndarray:
    if s.dtype == object:
        return (s.astype(str).str.lower() == "up").astype(np.int8).to_numpy()
    return s.astype(np.int8).to_numpy()


def preprocess(warmup: int = 5000) -> dict[str, Path]:
    """Produce X_warmup / y_warmup (initial fit) and X_stream / y_stream (prequential)."""
    df = _load_raw()
    log.info("Loaded ELEC2: %s", df.shape)

    missing = [c for c in [*FEATURE_COLS, TARGET_COL] if c not in df.columns]
    if missing:
        raise ValueError(f"ELEC2 schema mismatch, missing columns: {missing}")

    X = df[FEATURE_COLS].astype(np.float32).to_numpy()
    y = _binarize_target(df[TARGET_COL])

    if warmup >= len(X):
        raise ValueError("warmup window must be < dataset length")

    X_warmup, y_warmup = X[:warmup], y[:warmup]
    X_stream, y_stream = X[warmup:], y[warmup:]

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "X_warmup": PROCESSED_DIR / "X_warmup.npy",
        "y_warmup": PROCESSED_DIR / "y_warmup.npy",
        "X_stream": PROCESSED_DIR / "X_stream.npy",
        "y_stream": PROCESSED_DIR / "y_stream.npy",
        "features": PROCESSED_DIR / "features.txt",
    }
    np.save(paths["X_warmup"], X_warmup)
    np.save(paths["y_warmup"], y_warmup)
    np.save(paths["X_stream"], X_stream)
    np.save(paths["y_stream"], y_stream)
    paths["features"].write_text("\n".join(FEATURE_COLS))

    log.info("warmup=%s stream=%s -> %s", X_warmup.shape, X_stream.shape, PROCESSED_DIR)
    return paths


def load_processed() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    X_w = np.load(PROCESSED_DIR / "X_warmup.npy")
    y_w = np.load(PROCESSED_DIR / "y_warmup.npy")
    X_s = np.load(PROCESSED_DIR / "X_stream.npy")
    y_s = np.load(PROCESSED_DIR / "y_stream.npy")
    return X_w, y_w, X_s, y_s


if __name__ == "__main__":
    preprocess()
