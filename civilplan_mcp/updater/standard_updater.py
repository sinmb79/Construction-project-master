from __future__ import annotations

from typing import Any

from civilplan_mcp.config import get_settings
from civilplan_mcp.updater.common import (
    build_log_entry,
    clear_update_flag,
    extract_marker,
    fetch_source_text,
    flag_manual_update_required,
    write_update_log,
)


STANDARD_SOURCE_URL = "https://www.molit.go.kr/portal.do"
STANDARD_MARKER_PATTERNS = [
    r"표준시장단가",
    r"제비율",
    r"20\d{2}년",
]


def update_standard_prices(period: str = "상반기") -> dict[str, Any]:
    data_dir = get_settings().data_dir
    try:
        text = fetch_source_text(STANDARD_SOURCE_URL)
        marker = extract_marker(text, STANDARD_MARKER_PATTERNS)
        if not marker:
            detail = f"Fetched standard-cost source, but no recognizable bulletin marker was found for {period}."
            flag_manual_update_required("standard", detail, data_dir=data_dir)
            write_update_log(
                build_log_entry(
                    update_type="standard",
                    period=period,
                    status="pending_manual_review",
                    source_url=STANDARD_SOURCE_URL,
                    detail=detail,
                ),
                data_dir=data_dir,
            )
            return {"status": "pending_manual_review", "period": period, "source_url": STANDARD_SOURCE_URL}

        clear_update_flag("standard", data_dir=data_dir)
        write_update_log(
            build_log_entry(
                update_type="standard",
                period=period,
                status="fetched",
                source_url=STANDARD_SOURCE_URL,
                detail="Recognized standard-cost bulletin marker from source page.",
                marker=marker,
            ),
            data_dir=data_dir,
        )
        return {
            "status": "fetched",
            "period": period,
            "marker": marker,
            "source_url": STANDARD_SOURCE_URL,
        }
    except Exception as exc:
        detail = f"Standard update fetch failed for {period}: {exc}"
        flag_manual_update_required("standard", detail, data_dir=data_dir)
        write_update_log(
            build_log_entry(
                update_type="standard",
                period=period,
                status="pending_manual_review",
                source_url=STANDARD_SOURCE_URL,
                detail=detail,
            ),
            data_dir=data_dir,
        )
        return {
            "status": "pending_manual_review",
            "period": period,
            "message": detail,
            "source_url": STANDARD_SOURCE_URL,
        }
