from __future__ import annotations

from typing import Any

from civilplan_mcp.db.bootstrap import load_json_data
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def fetch_guideline_summary(*, guideline_id: str) -> dict[str, Any]:
    guidelines = load_json_data("guidelines_catalog.json")["guidelines"]
    summary = next(item for item in guidelines if item["id"] == guideline_id)
    return wrap_response(
        {
            "summary": {
                "id": summary["id"],
                "title": summary["title"],
                "ministry": summary["ministry"],
                "content": summary["summary"],
            },
            "source": "local catalog",
        },
        ProjectDomain(summary["domain"]) if summary["domain"] != "복합" else ProjectDomain.복합,
    )
