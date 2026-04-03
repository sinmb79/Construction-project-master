from __future__ import annotations

from collections import defaultdict
from typing import Any

from civilplan_mcp.db.bootstrap import load_json_data
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def _to_domain(value: ProjectDomain | str) -> ProjectDomain:
    return value if isinstance(value, ProjectDomain) else ProjectDomain(value)


def _preparing_response(message: str) -> dict[str, Any]:
    return wrap_response({"status": "not_ready", "message": message}, ProjectDomain.조경)


def get_legal_procedures(
    *,
    domain: ProjectDomain | str,
    project_type: str,
    total_cost_billion: float,
    road_length_m: float | None,
    development_area_m2: float | None,
    region: str,
    has_farmland: bool,
    has_forest: bool,
    has_river: bool,
    is_public: bool,
) -> dict[str, Any]:
    resolved_domain = _to_domain(domain)
    if resolved_domain == ProjectDomain.조경:
        return _preparing_response("조경 분야는 현재 지원 준비 중입니다.")

    procedures = load_json_data("legal_procedures.json")["procedures"]
    filtered = [
        item
        for item in procedures
        if item["domain"] in {resolved_domain.value, ProjectDomain.복합.value}
    ]
    phases: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in filtered:
        phases[item["category"]].append(item)

    mandatory_count = sum(1 for item in filtered if item["mandatory"])
    summary = {
        "total_procedures": len(filtered),
        "mandatory_count": mandatory_count,
        "optional_count": len(filtered) - mandatory_count,
        "estimated_prep_months": max((item["duration_max_months"] for item in filtered), default=0),
        "critical_path": [item["name"] for item in filtered[:3]],
        "cost_impact_note": f"총사업비 {total_cost_billion:.2f}억 기준 검토 결과",
    }
    result = {
        "summary": summary,
        "phases": dict(phases),
        "timeline_estimate": {
            "인허가완료목표": "착공 18개월 전",
            "설계완료목표": "착공 6개월 전",
            "주의사항": "핵심 인허가 일정이 전체 사업 기간을 지배할 수 있습니다.",
        },
        "inputs": {
            "project_type": project_type,
            "region": region,
            "road_length_m": road_length_m,
            "development_area_m2": development_area_m2,
            "has_farmland": has_farmland,
            "has_forest": has_forest,
            "has_river": has_river,
            "is_public": is_public,
        },
    }
    return wrap_response(result, resolved_domain)
