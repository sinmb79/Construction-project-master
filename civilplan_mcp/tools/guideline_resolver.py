from __future__ import annotations

from typing import Any

from civilplan_mcp.db.bootstrap import load_json_data
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def get_applicable_guidelines(*, domain: ProjectDomain | str, procedure_ids: list[str], project_type: str) -> dict[str, Any]:
    resolved_domain = domain if isinstance(domain, ProjectDomain) else ProjectDomain(domain)
    guidelines = load_json_data("guidelines_catalog.json")["guidelines"]
    matched = [
        item
        for item in guidelines
        if item["domain"] in {resolved_domain.value, ProjectDomain.복합.value}
    ]
    return wrap_response(
        {
            "project_type": project_type,
            "procedure_ids": procedure_ids,
            "guidelines": matched,
        },
        resolved_domain,
    )
