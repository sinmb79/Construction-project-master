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


WASTE_SOURCE_URL = "https://www.data.go.kr/data/15052266/fileData.do"
WASTE_MARKER_PATTERNS = [
    r"20\d{2}[-./]\d{2}[-./]\d{2}",
    r"20\d{2}년",
]


def update_waste_prices() -> dict[str, Any]:
    data_dir = get_settings().data_dir
    try:
        text = fetch_source_text(WASTE_SOURCE_URL)
        marker = extract_marker(text, WASTE_MARKER_PATTERNS)
        if not marker:
            detail = "Fetched waste source, but no recognizable release marker was found."
            flag_manual_update_required("waste", detail, data_dir=data_dir)
            write_update_log(
                build_log_entry(
                    update_type="waste",
                    period=None,
                    status="pending_manual_review",
                    source_url=WASTE_SOURCE_URL,
                    detail=detail,
                ),
                data_dir=data_dir,
            )
            return {"status": "pending_manual_review", "source_url": WASTE_SOURCE_URL}

        clear_update_flag("waste", data_dir=data_dir)
        write_update_log(
            build_log_entry(
                update_type="waste",
                period=None,
                status="fetched",
                source_url=WASTE_SOURCE_URL,
                detail="Recognized release marker from waste source page.",
                marker=marker,
            ),
            data_dir=data_dir,
        )
        return {"status": "fetched", "marker": marker, "source_url": WASTE_SOURCE_URL}
    except Exception as exc:
        detail = f"Waste update fetch failed: {exc}"
        flag_manual_update_required("waste", detail, data_dir=data_dir)
        write_update_log(
            build_log_entry(
                update_type="waste",
                period=None,
                status="pending_manual_review",
                source_url=WASTE_SOURCE_URL,
                detail=detail,
            ),
            data_dir=data_dir,
        )
        return {
            "status": "pending_manual_review",
            "message": detail,
            "source_url": WASTE_SOURCE_URL,
        }
