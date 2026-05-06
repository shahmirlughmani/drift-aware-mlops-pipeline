from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXPERIMENTS_DIR = ROOT / "experiments" / "results"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "drift-aware-mlops"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    model_name: str = "elec2-online"
    model_stage: str = "Production"

    drift_detector: str = "hybrid"
    drift_warmup: int = 200
    drift_retrain_cooldown_s: int = 60

    random_seed: int = 42


settings = Settings()
