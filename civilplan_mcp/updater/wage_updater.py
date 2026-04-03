from __future__ import annotations

from pathlib import Path
from typing import Any

from civilplan_mcp.config import get_settings
from civilplan_mcp.updater.common import (
    build_log_entry,
    check_update_flags,
    clear_update_flag,
    extract_marker,
    fetch_source_text,
    flag_manual_update_required,
    write_update_log,
)


WAGE_SOURCE_URL = "https://gwangju.cak.or.kr/lay1/bbs/S1T41C42/A/14/list.do"
WAGE_MARKER_PATTERNS = [
    r"20\d{2}년\s*(상반기|하반기)\s*적용\s*건설업\s*임금실태조사",
    r"20\d{2}년\s*건설업\s*임금실태조사",
]


def update_wage_rates(period: str = "상반기") -> dict[str, Any]:
    data_dir = get_settings().data_dir
    try:
        text = fetch_source_text(WAGE_SOURCE_URL)
        marker = extract_marker(text, WAGE_MARKER_PATTERNS)
        if not marker:
            detail = f"Fetched wage source, but no recognizable wage bulletin marker was found for {period}."
            flag_manual_update_required("wage", detail, data_dir=data_dir)
            write_update_log(
                build_log_entry(
                    update_type="wage",
                    period=period,
                    status="pending_manual_review",
                    source_url=WAGE_SOURCE_URL,
                    detail=detail,
                ),
                data_dir=data_dir,
            )
            return {"status": "pending_manual_review", "period": period, "source_url": WAGE_SOURCE_URL}

        clear_update_flag("wage", data_dir=data_dir)
        write_update_log(
            build_log_entry(
                update_type="wage",
                period=period,
                status="fetched",
                source_url=WAGE_SOURCE_URL,
                detail="Recognized wage bulletin marker from source page.",
                marker=marker,
            ),
            data_dir=data_dir,
        )
        return {
            "status": "fetched",
            "period": period,
            "marker": marker,
            "source_url": WAGE_SOURCE_URL,
        }
    except Exception as exc:
        detail = f"Wage update fetch failed for {period}: {exc}"
        flag_manual_update_required("wage", detail, data_dir=data_dir)
        write_update_log(
            build_log_entry(
                update_type="wage",
                period=period,
                status="pending_manual_review",
                source_url=WAGE_SOURCE_URL,
                detail=detail,
            ),
            data_dir=data_dir,
        )
        return {
            "status": "pending_manual_review",
            "period": period,
            "message": detail,
            "source_url": WAGE_SOURCE_URL,
        }


__all__ = ["check_update_flags", "flag_manual_update_required", "update_wage_rates"]
