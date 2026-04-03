from __future__ import annotations

from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def select_bid_type(*, total_cost_billion: float, domain: ProjectDomain | str) -> dict:
    resolved_domain = domain if isinstance(domain, ProjectDomain) else ProjectDomain(domain)
    if total_cost_billion >= 300:
        recommended = "종합심사낙찰제"
    elif total_cost_billion >= 100:
        recommended = "적격심사"
    else:
        recommended = "수의계약 검토"

    return wrap_response(
        {
            "recommended_type": recommended,
            "basis": f"총사업비 {total_cost_billion:.1f}억 기준",
            "references": {
                "적격심사_일반": "64~87%",
                "종합심사낙찰제": "90~95%",
            },
        },
        resolved_domain,
    )
