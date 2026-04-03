from __future__ import annotations

from typing import Any

from civilplan_mcp.models import ProjectDomain


DOMAIN_DISCLAIMER = {
    ProjectDomain.건축: "건축 기준 결과입니다. 다른 공종이 섞이면 추가 절차가 필요합니다.",
    ProjectDomain.토목_도로: "도로 기준 결과입니다. 교량, 터널, 하천 포함 시 추가 검토가 필요합니다.",
    ProjectDomain.토목_상하수도: "상하수도 기준 결과입니다. 별도 사업인가 검토가 필요합니다.",
    ProjectDomain.토목_하천: "하천 기준 결과입니다. 점용허가 및 수리 검토가 추가될 수 있습니다.",
    ProjectDomain.조경: "조경 분야는 현재 지원 준비 중입니다.",
    ProjectDomain.복합: "복합 사업입니다. 각 분야별 절차를 별도로 확인하세요.",
}

VALIDITY_DISCLAIMER = "참고용 개략 자료 - 공식 제출 불가"


def wrap_response(result: dict[str, Any], domain: ProjectDomain) -> dict[str, Any]:
    wrapped = dict(result)
    wrapped["domain_note"] = DOMAIN_DISCLAIMER.get(domain, "")
    wrapped["validity_disclaimer"] = VALIDITY_DISCLAIMER
    wrapped["data_as_of"] = "2026년 4월 기준"
    return wrapped
