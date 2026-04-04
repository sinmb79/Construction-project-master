from __future__ import annotations

from pathlib import Path

from civilplan_mcp import setup_keys


def test_main_prompts_and_saves_gemini_api_key(monkeypatch, tmp_path: Path) -> None:
    prompted_values = iter(["data-key", "vworld-key", "gemini-key"])
    saved_payload: dict[str, str] = {}

    monkeypatch.setattr(setup_keys, "_prompt_value", lambda name, current="": next(prompted_values))
    monkeypatch.setattr(
        setup_keys,
        "save_api_keys",
        lambda payload: saved_payload.update(payload) or tmp_path / "api-keys.dpapi.json",
    )

    exit_code = setup_keys.main([])

    assert exit_code == 0
    assert saved_payload == {
        "DATA_GO_KR_API_KEY": "data-key",
        "VWORLD_API_KEY": "vworld-key",
        "GEMINI_API_KEY": "gemini-key",
    }
