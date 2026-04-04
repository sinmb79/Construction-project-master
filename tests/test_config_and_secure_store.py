from __future__ import annotations

from pathlib import Path

import pytest

from civilplan_mcp import config, secure_store


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


def test_secure_store_round_trip_with_stub_crypto(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "api-keys.dpapi.json"

    monkeypatch.setattr(secure_store, "_protect_bytes", lambda raw: raw[::-1])
    monkeypatch.setattr(secure_store, "_unprotect_bytes", lambda raw: raw[::-1])

    secure_store.save_api_keys(
        {
            "DATA_GO_KR_API_KEY": "data-key",
            "VWORLD_API_KEY": "vworld-key",
        },
        path=target,
    )

    loaded = secure_store.load_api_keys(path=target)

    assert loaded == {
        "DATA_GO_KR_API_KEY": "data-key",
        "VWORLD_API_KEY": "vworld-key",
    }


def test_get_settings_uses_secure_store_when_env_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(config, "BASE_DIR", tmp_path)
    monkeypatch.setattr(config, "load_local_env", lambda: None)
    monkeypatch.setattr(
        config,
        "_load_secure_api_keys",
        lambda path: {
            "DATA_GO_KR_API_KEY": "secure-data-key",
            "VWORLD_API_KEY": "secure-vworld-key",
            "GEMINI_API_KEY": "secure-gemini-key",
        },
    )
    monkeypatch.delenv("DATA_GO_KR_API_KEY", raising=False)
    monkeypatch.delenv("VWORLD_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    settings = config.get_settings()

    assert settings.data_go_kr_api_key == "secure-data-key"
    assert settings.vworld_api_key == "secure-vworld-key"
    assert settings.gemini_api_key == "secure-gemini-key"


def test_get_settings_prefers_env_values_over_secure_store(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(config, "BASE_DIR", tmp_path)
    monkeypatch.setattr(config, "load_local_env", lambda: None)
    monkeypatch.setattr(
        config,
        "_load_secure_api_keys",
        lambda path: {
            "DATA_GO_KR_API_KEY": "secure-data-key",
            "VWORLD_API_KEY": "secure-vworld-key",
            "GEMINI_API_KEY": "secure-gemini-key",
        },
    )
    monkeypatch.setenv("DATA_GO_KR_API_KEY", "env-data-key")
    monkeypatch.setenv("VWORLD_API_KEY", "env-vworld-key")
    monkeypatch.setenv("GEMINI_API_KEY", "env-gemini-key")

    settings = config.get_settings()

    assert settings.data_go_kr_api_key == "env-data-key"
    assert settings.vworld_api_key == "env-vworld-key"
    assert settings.gemini_api_key == "env-gemini-key"


def test_settings_has_gemini_api_key(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    settings = config.Settings()

    assert hasattr(settings, "gemini_api_key")
    assert settings.gemini_api_key == ""


def test_check_api_keys_includes_gemini_when_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(config, "BASE_DIR", tmp_path)
    monkeypatch.setattr(config, "load_local_env", lambda: None)
    monkeypatch.setattr(config, "_load_secure_api_keys", lambda path: {})
    monkeypatch.delenv("DATA_GO_KR_API_KEY", raising=False)
    monkeypatch.delenv("VWORLD_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    missing = config.check_api_keys()

    assert "GEMINI_API_KEY" in missing
