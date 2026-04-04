from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from civilplan_mcp.secure_store import default_key_store_path, load_api_keys


BASE_DIR = Path(__file__).resolve().parent.parent


def load_local_env() -> None:
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)


def _load_secure_api_keys(path: Path) -> dict[str, str]:
    try:
        return load_api_keys(path=path)
    except Exception:
        return {}


class Settings(BaseModel):
    app_name: str = "civilplan_mcp"
    version: str = "2.0.0"
    host: str = "127.0.0.1"
    port: int = 8765
    http_path: str = "/mcp"
    db_path: Path = Field(default_factory=lambda: BASE_DIR / "civilplan.db")
    output_dir: Path = Field(default_factory=lambda: BASE_DIR / "output")
    data_dir: Path = Field(default_factory=lambda: BASE_DIR / "civilplan_mcp" / "data")
    key_store_path: Path = Field(default_factory=default_key_store_path)
    data_go_kr_api_key: str = Field(default_factory=lambda: os.getenv("DATA_GO_KR_API_KEY", ""))
    vworld_api_key: str = Field(default_factory=lambda: os.getenv("VWORLD_API_KEY", ""))
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_local_env()
    settings = Settings()
    secure_keys = _load_secure_api_keys(settings.key_store_path)

    if not settings.data_go_kr_api_key:
        settings.data_go_kr_api_key = secure_keys.get("DATA_GO_KR_API_KEY", "")
    if not settings.vworld_api_key:
        settings.vworld_api_key = secure_keys.get("VWORLD_API_KEY", "")
    if not settings.gemini_api_key:
        settings.gemini_api_key = secure_keys.get("GEMINI_API_KEY", "")

    settings.output_dir.mkdir(parents=True, exist_ok=True)
    return settings


def check_api_keys() -> list[str]:
    settings = get_settings()
    missing = []
    if not settings.data_go_kr_api_key:
        missing.append("DATA_GO_KR_API_KEY")
    if not settings.vworld_api_key:
        missing.append("VWORLD_API_KEY")
    if not settings.gemini_api_key:
        missing.append("GEMINI_API_KEY")
    return missing
