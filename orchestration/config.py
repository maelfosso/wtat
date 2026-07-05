from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # env_prefix="WTAT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    db_path: str = str(PROJECT_ROOT / "warehouse.duckdb")
    raw_root: Path = PROJECT_ROOT / "data" / "raw"
    export_dir: Path = PROJECT_ROOT / "data" / "exports"

    nats_url: str = "nats://localhost:4222"

    max_extraction_attempts: int = 3
    in_flight_timeout_minutes: int = 60
    db_batch_size: int = 50

    llm_api_base: str
    llm_api_key: str
    llm_model: str
    llm_timeout: int = 300
    llm_max_concurrent_requests: int = 5
    llm_batch_size: int

settings = Settings()
