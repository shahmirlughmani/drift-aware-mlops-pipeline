"""Download the ELEC2 streaming-classification benchmark.

ELEC2 (Harries, 1999): NSW electricity market price-trend prediction.
45,312 instances, 8 features, binary label UP/DOWN. Real concept drift
caused by changing market dynamics over time.
"""

from __future__ import annotations

from pathlib import Path

import requests

from src.utils.config import RAW_DIR
from src.utils.logging import get_logger

log = get_logger(__name__)

# Mirror with a stable schema; column names match Harries' original.
ELEC2_URL = "https://www.openml.org/data/get_csv/2419/electricity-normalized.arff"
LOCAL_NAME = "elec2.csv"


def download(force: bool = False) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    target = RAW_DIR / LOCAL_NAME
    if target.exists() and not force:
        log.info("ELEC2 already present at %s", target)
        return target

    log.info("Downloading ELEC2 from %s", ELEC2_URL)
    resp = requests.get(ELEC2_URL, timeout=60)
    resp.raise_for_status()
    target.write_bytes(resp.content)
    log.info("Saved %d bytes to %s", len(resp.content), target)
    return target


if __name__ == "__main__":
    download()
