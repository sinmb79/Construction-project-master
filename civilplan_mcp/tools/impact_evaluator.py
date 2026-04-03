from __future__ import annotations

from typing import Any

from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def evaluate_impact_assessments(
    *,
    domain: str,
    project_type: str,
    road_length_m: float | None,
    development_area_m2: float | None,
    total_cost_billion: float,
    building_floor_area_m2: float | None,
    housing_units: int | None,
    is_urban_area: bool,
    near_cultural_heritage: bool,
    near_river: bool,
    near_protected_area: bool,
) -> dict[str, Any]:
    disaster_result = "BORDERLINE" if (development_area_m2 or 0) >= 5000 else "NOT_APPLICABLE"
    evaluations = [
        {
            "name": "재해영향평가",
            "applicable": disaster_result != "NOT_APPLICABLE",
            "threshold": "도로 연장 2km 이상 또는 개발면적 5,000m² 이상",
            "law": "자연재해대책법 제4조",
            "your_case": f"도로 {road_length_m or 0}m / 개발면적 {development_area_m2 or 0}m²",
            "result": disaster_result,
            "recommendation": "인허가청 사전 협의 필수" if disaster_result == "BORDERLINE" else "일반 검토",
            "authority": "행정안전부 / 지자체",
            "duration_months_est": 2 if disaster_result == "BORDERLINE" else 0,
            "cost_estimate_million": 8 if disaster_result == "BORDERLINE" else 0,
        },
        {
            "name": "매장문화재지표조사",
            "applicable": near_cultural_heritage,
            "threshold": "문화재 인접 또는 조사 필요지역",
            "law": "매장문화재 보호 및 조사에 관한 법률 제6조",
            "your_case": "인접 여부 기반",
            "result": "APPLICABLE" if near_cultural_heritage else "NOT_APPLICABLE",
            "recommendation": "사전 조사 요청" if near_cultural_heritage else "일반 검토",
            "authority": "문화재청",
            "duration_months_est": 1 if near_cultural_heritage else 0,
            "cost_estimate_million": 5 if near_cultural_heritage else 0,
        },
    ]
    applicable = [item for item in evaluations if item["result"] != "NOT_APPLICABLE"]
    return wrap_response(
        {
            "summary": {
                "applicable_count": len(applicable),
                "total_checked": len(evaluations),
                "critical_assessments": [item["name"] for item in applicable],
                "estimated_total_months": sum(item["duration_months_est"] for item in applicable),
                "total_cost_estimate_million": sum(item["cost_estimate_million"] for item in applicable),
            },
            "evaluations": evaluations,
            "inputs": {
                "project_type": project_type,
                "total_cost_billion": total_cost_billion,
                "building_floor_area_m2": building_floor_area_m2,
                "housing_units": housing_units,
                "is_urban_area": is_urban_area,
                "near_river": near_river,
                "near_protected_area": near_protected_area,
            },
        },
        ProjectDomain(domain),
    )
