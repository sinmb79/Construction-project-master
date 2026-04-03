from __future__ import annotations

from typing import Any

from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def get_phase_checklist(
    *,
    domain: ProjectDomain | str,
    phase: str,
    project_type: str,
    total_cost_billion: float,
    has_building: bool,
    has_bridge: bool,
) -> dict[str, Any]:
    resolved_domain = domain if isinstance(domain, ProjectDomain) else ProjectDomain(domain)
    if resolved_domain == ProjectDomain.조경:
        return wrap_response(
            {"status": "not_ready", "message": "조경 분야는 현재 지원 준비 중입니다."},
            ProjectDomain.조경,
        )

    checklist = [
        {
            "seq": 1,
            "category": "신고·허가",
            "task": "착공신고" if phase == "공사" else f"{phase} 단계 검토회의",
            "mandatory": True,
            "applicable": True,
            "law": "건설산업기본법 제39조",
            "authority": "발주청/인허가청",
            "deadline": "착공 전" if phase == "공사" else "단계 시작 전",
            "penalty": "행정상 제재 가능",
            "template_available": True,
            "note": f"{project_type} 사업의 {phase} 단계 기본 업무",
        }
    ]
    return wrap_response(
        {
            "phase": phase,
            "description": f"{phase} 단계 의무 이행 사항",
            "total_tasks": len(checklist),
            "mandatory_applicable": 1,
            "optional_applicable": 0,
            "checklist": checklist,
            "key_risks": [f"{phase} 단계 핵심 일정 지연"],
            "inputs": {
                "total_cost_billion": total_cost_billion,
                "has_building": has_building,
                "has_bridge": has_bridge,
            },
        },
        resolved_domain,
    )
