from civilplan_mcp import __version__
from civilplan_mcp.config import Settings, get_settings


def test_package_version_present() -> None:
    assert __version__ == "2.0.0"


def test_settings_have_expected_defaults() -> None:
    settings = Settings()

    assert settings.host == "127.0.0.1"
    assert settings.port == 8765
    assert settings.http_path == "/mcp"


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
