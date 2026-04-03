from __future__ import annotations

import argparse
from getpass import getpass
from pathlib import Path

from civilplan_mcp.secure_store import default_key_store_path, save_api_keys


def _parse_env_file(path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        parsed[key.strip()] = value.strip().strip("'").strip('"')
    return parsed


def _prompt_value(name: str, current: str = "") -> str:
    prompt = f"{name}"
    if current:
        prompt += " [press Enter to keep imported value]"
    prompt += ": "
    entered = getpass(prompt).strip()
    return entered or current


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Store CivilPlan API keys in Windows DPAPI encrypted local storage.")
    parser.add_argument(
        "--from-env-file",
        type=Path,
        help="Import API keys from an existing .env file before prompting.",
    )
    args = parser.parse_args(argv)

    imported: dict[str, str] = {}
    if args.from_env_file:
        imported = _parse_env_file(args.from_env_file)

    data_go_kr_api_key = _prompt_value("DATA_GO_KR_API_KEY", imported.get("DATA_GO_KR_API_KEY", ""))
    vworld_api_key = _prompt_value("VWORLD_API_KEY", imported.get("VWORLD_API_KEY", ""))

    target = save_api_keys(
        {
            "DATA_GO_KR_API_KEY": data_go_kr_api_key,
            "VWORLD_API_KEY": vworld_api_key,
        }
    )

    print("CivilPlan API keys were saved to encrypted local storage.")
    print(f"Path: {target}")
    print("The file is protected with Windows DPAPI and can only be read by the same Windows user on this machine.")
    return 0
