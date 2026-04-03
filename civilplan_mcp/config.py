from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import os

from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    app_name: str = "civilplan_mcp"
    version: str = "1.0.0"
    host: str = "127.0.0.1"
    port: int = 8765
    http_path: str = "/mcp"
    db_path: Path = Field(default_factory=lambda: BASE_DIR / "civilplan.db")
    output_dir: Path = Field(default_factory=lambda: BASE_DIR / "output")
    data_dir: Path = Field(default_factory=lambda: BASE_DIR / "civilplan_mcp" / "data")
    data_go_kr_api_key: str = Field(default_factory=lambda: os.getenv("DATA_GO_KR_API_KEY", ""))
    vworld_api_key: str = Field(default_factory=lambda: os.getenv("VWORLD_API_KEY", ""))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    return settings


def check_api_keys() -> list[str]:
    settings = get_settings()
    missing = []
    if not settings.data_go_kr_api_key:
        missing.append("DATA_GO_KR_API_KEY")
    if not settings.vworld_api_key:
        missing.append("VWORLD_API_KEY")
    return missing
