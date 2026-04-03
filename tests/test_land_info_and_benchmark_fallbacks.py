from __future__ import annotations

import httpx

from civilplan_mcp.config import Settings
from civilplan_mcp.tools import benchmark_validator, land_info_query


def _json_response(url: str, payload: dict, *, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code,
        request=httpx.Request("GET", url),
        json=payload,
    )


def test_query_land_info_uses_eum_land_use_endpoint(monkeypatch, tmp_path) -> None:
    settings = Settings(vworld_api_key="test-key", data_go_kr_api_key="public-key", data_dir=tmp_path)
    calls: list[str] = []

    def fake_get(url: str, *, params=None, timeout=None, headers=None):  # type: ignore[no-untyped-def]
        calls.append(url)
        if url == land_info_query.VWORLD_ADDRESS_URL:
            return _json_response(
                url,
                {
                    "response": {
                        "status": "OK",
                        "result": {
                            "point": {"x": "127.061", "y": "37.821"},
                            "items": [
                                {
                                    "id": "4163011600101230000",
                                    "address": {"parcel": "경기도 양주시 덕계동 123"},
                                }
                            ],
                        },
                    }
                },
            )
        if url == land_info_query.VWORLD_DATA_URL:
            return _json_response(
                url,
                {
                    "response": {
                        "status": "OK",
                        "result": {
                            "featureCollection": {
                                "features": [
                                    {
                                        "properties": {
                                            "area": "320.5",
                                            "jimok": "대",
                                        }
                                    }
                                ]
                            }
                        },
                    }
                },
            )
        if url == land_info_query.EUM_LAND_USE_URL:
            return _json_response(
                url,
                {
                    "landUseInfo": {
                        "useDistrict": "제2종일반주거지역",
                        "district2": "고도지구",
                        "bcr": "60",
                        "far": "200",
                        "heightLimit": "16",
                    }
                },
            )
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(land_info_query, "get_settings", lambda: settings)
    monkeypatch.setattr(land_info_query.httpx, "get", fake_get)

    result = land_info_query.query_land_info(address="경기도 양주시 덕계동 123", pnu=None)

    assert result["status"] == "success"
    assert result["zoning"]["use_district"] == "제2종일반주거지역"
    assert result["zoning"]["district_2"] == "고도지구"
    assert result["zoning"]["bcr_pct"] == 60
    assert result["zoning"]["far_pct"] == 200
    assert land_info_query.EUM_LAND_USE_URL in calls
    assert "https://api.vworld.kr/req/wfs" not in calls


def test_validate_against_benchmark_reports_backend_fallback_on_502(monkeypatch) -> None:
    settings = Settings(data_go_kr_api_key="test-key")

    def fake_get(url: str, *, params=None, timeout=None):  # type: ignore[no-untyped-def]
        return httpx.Response(
            502,
            request=httpx.Request("GET", url),
            text="backend unavailable",
        )

    monkeypatch.setattr(benchmark_validator, "get_settings", lambda: settings)
    monkeypatch.setattr(benchmark_validator.httpx, "get", fake_get)

    result = benchmark_validator.validate_against_benchmark(
        project_type="도로_포장",
        road_length_m=890,
        floor_area_m2=None,
        region="경기도",
        our_estimate_won=1_067_000_000,
    )

    assert result["benchmark"]["api_status"] == "fallback"
    assert "나라장터 직접 검색" in result["benchmark"]["availability_note"]
