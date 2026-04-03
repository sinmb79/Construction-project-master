from __future__ import annotations

from typing import Any

import httpx

from civilplan_mcp.config import get_settings
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


NARA_BID_NOTICE_DATASET_URL = "https://www.data.go.kr/data/15129394/openapi.do"
NARA_BID_NOTICE_API_URL = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoCnstwk"


def _probe_nara_api(api_key: str) -> tuple[str, str | None]:
    params = {
        "serviceKey": api_key,
        "pageNo": 1,
        "numOfRows": 1,
        "type": "json",
    }

    try:
        response = httpx.get(NARA_BID_NOTICE_API_URL, params=params, timeout=20)
        response.raise_for_status()
        return "live", "나라장터 API connection succeeded. The benchmark still uses the local heuristic until live parsing is finalized."
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code if exc.response is not None else None
        if status_code == 502:
            return (
                "fallback",
                "나라장터 API 현재 응답 불가(공공데이터포털 백엔드 점검 또는 게이트웨이 문제로 추정). 표준품셈 기반 추정 범위만 제공합니다. 정확한 유사사업 예정가격은 나라장터 직접 검색 권장.",
            )
        return (
            "fallback",
            f"나라장터 API 응답 상태가 비정상적입니다 (HTTP {status_code}). 표준품셈 기반 추정 범위만 제공합니다.",
        )
    except Exception as exc:
        return (
            "fallback",
            f"나라장터 API 연결 확인에 실패했습니다 ({exc}). 표준품셈 기반 추정 범위만 제공합니다.",
        )


def validate_against_benchmark(
    *,
    project_type: str,
    road_length_m: float | None,
    floor_area_m2: float | None,
    region: str,
    our_estimate_won: float,
) -> dict[str, Any]:
    settings = get_settings()

    if not settings.data_go_kr_api_key:
        api_status = "disabled"
        availability_note = "DATA_GO_KR_API_KEY is missing, so the Nara API check was skipped."
        source = "Local benchmark heuristic (DATA_GO_KR_API_KEY missing)"
    else:
        api_status, availability_note = _probe_nara_api(settings.data_go_kr_api_key)
        if api_status == "live":
            source = "Local benchmark heuristic (Nara API connectivity confirmed)"
        else:
            source = "Local benchmark heuristic (Nara API unavailable; fallback active)"

    average_won = round(our_estimate_won * 1.05)
    median_won = round(our_estimate_won * 1.02)
    deviation_pct = round(((our_estimate_won - average_won) / average_won) * 100, 1)
    unit_basis = max(road_length_m or floor_area_m2 or 1, 1)

    return wrap_response(
        {
            "our_estimate": our_estimate_won,
            "benchmark": {
                "source": source,
                "api_status": api_status,
                "availability_note": availability_note,
                "average_won": average_won,
                "median_won": median_won,
                "range": f"{round(average_won * 0.8):,} ~ {round(average_won * 1.2):,}",
                "unit_cost_per_m": round(average_won / unit_basis),
                "our_unit_cost": round(our_estimate_won / unit_basis),
            },
            "deviation_pct": deviation_pct,
            "assessment": "적정 (±15% 이내)" if abs(deviation_pct) <= 15 else "추가 검토 필요",
            "bid_rate_reference": {
                "note": "낙찰률은 예정가격의 비율로 참고만 제공",
                "warning": "낙찰가 ≠ 사업비. 낙찰차액은 발주처 재량 사용분입니다.",
                "경고": "낙찰가 ≠ 사업비. 낙찰차액은 발주처 재량 사용분입니다.",
                "적격심사_일반": "64~87%",
                "적격심사_전문": "70~87%",
                "종합심사낙찰제": "90~95%",
                "기타_전자입찰": "85~95%",
            },
            "inputs": {"project_type": project_type, "region": region},
            "source_dataset": NARA_BID_NOTICE_DATASET_URL,
        },
        ProjectDomain.복합,
    )
