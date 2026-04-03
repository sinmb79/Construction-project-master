from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any

import httpx

from civilplan_mcp.config import get_settings


LOG_FILE_NAME = "update_log.json"


def flag_manual_update_required(update_type: str, message: str, data_dir: Path | None = None) -> Path:
    target_dir = data_dir or get_settings().data_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    flag_path = target_dir / f".update_required_{update_type}"
    flag_path.write_text(f"{datetime.now():%Y-%m-%d} {message}", encoding="utf-8")
    return flag_path


def clear_update_flag(update_type: str, data_dir: Path | None = None) -> None:
    target_dir = data_dir or get_settings().data_dir
    flag_path = target_dir / f".update_required_{update_type}"
    if flag_path.exists():
        flag_path.unlink()


def check_update_flags(data_dir: Path | None = None) -> list[str]:
    target_dir = data_dir or get_settings().data_dir
    warnings: list[str] = []
    for flag in target_dir.glob(".update_required_*"):
        warnings.append(flag.read_text(encoding="utf-8"))
    return warnings


def read_update_log(data_dir: Path | None = None) -> list[dict[str, Any]]:
    target_dir = data_dir or get_settings().data_dir
    log_path = target_dir / LOG_FILE_NAME
    if not log_path.exists():
        return []
    return json.loads(log_path.read_text(encoding="utf-8"))


def write_update_log(entry: dict[str, Any], data_dir: Path | None = None) -> Path:
    target_dir = data_dir or get_settings().data_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    log_path = target_dir / LOG_FILE_NAME
    log_data = read_update_log(target_dir)
    log_data.append(entry)
    log_path.write_text(json.dumps(log_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return log_path


def fetch_source_text(url: str) -> str:
    response = httpx.get(
        url,
        timeout=30,
        headers={"User-Agent": "CivilPlan-MCP/1.0 (+https://localhost:8765/mcp)"},
    )
    response.raise_for_status()
    return response.text


def extract_marker(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def build_log_entry(
    *,
    update_type: str,
    period: str | None,
    status: str,
    source_url: str,
    detail: str,
    marker: str | None = None,
) -> dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "update_type": update_type,
        "period": period,
        "status": status,
        "source_url": source_url,
        "marker": marker,
        "detail": detail,
    }
