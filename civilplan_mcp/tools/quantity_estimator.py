from __future__ import annotations

from typing import Any

from civilplan_mcp.db.bootstrap import load_json_data
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


TERRAIN_FACTORS = {
    "평지": {"cut_section_m2": 5, "fill_section_m2": 3, "cut_ratio": 0.3, "fill_ratio": 0.3},
    "구릉": {"cut_section_m2": 18, "fill_section_m2": 12, "cut_ratio": 0.5, "fill_ratio": 0.5},
    "산지": {"cut_section_m2": 35, "fill_section_m2": 22, "cut_ratio": 0.6, "fill_ratio": 0.4},
}


def estimate_quantities(
    *,
    road_class: str,
    length_m: float,
    width_m: float,
    terrain: str,
    pavement_type: str,
    include_water_supply: bool,
    include_sewage: bool,
    include_retaining_wall: bool,
    include_bridge: bool,
    bridge_length_m: float,
) -> dict[str, Any]:
    road_standards = load_json_data("road_standards.json")
    standard = road_standards[road_class]
    terrain_factor = TERRAIN_FACTORS[terrain]
    pavement_area = round(length_m * width_m, 1)
    surface_volume = pavement_area * (standard["ascon_surface_mm"] / 1000)
    base_volume = pavement_area * (standard["ascon_base_mm"] / 1000)

    quantities = {
        "토공": {
            "절토_m3": round(length_m * terrain_factor["cut_section_m2"] * terrain_factor["cut_ratio"]),
            "성토_m3": round(length_m * terrain_factor["fill_section_m2"] * terrain_factor["fill_ratio"]),
            "사토_m3": round(length_m * 2),
        },
        "포장": {
            "아스콘표층_t": round(surface_volume * 2.35),
            "아스콘기층_t": round(base_volume * 2.35),
            "보조기층_m3": round(pavement_area * (standard["subbase_mm"] / 1000)),
            "동상방지층_m3": round(pavement_area * (standard["frost_mm"] / 1000)),
        },
        "배수": {
            "L형측구_m": round(length_m * 2),
            "횡단암거D800_m": round(length_m / (150 if terrain == "구릉" else 100 if terrain == "산지" else 200)) * 10,
            "집수정_ea": max(2, round(length_m / 75)),
        },
        "교통안전": {
            "차선도색_m": round(length_m * max(1, width_m / 2)),
            "표지판_ea": max(4, round(length_m / 100)),
            "가드레일_m": round(length_m * 0.2),
        },
    }

    if include_water_supply:
        quantities["상수도"] = {"PE관DN100_m": round(length_m), "제수밸브_ea": 3, "소화전_ea": 3}
    if include_sewage:
        quantities["하수도"] = {
            "오수관VR250_m": round(length_m),
            "우수관D400_m": round(length_m),
            "오수맨홀_ea": round(length_m / 50) + 1,
            "우수맨홀_ea": round(length_m / 50),
        }
    if include_retaining_wall:
        quantities["구조물"] = {"L형옹벽H2m_m": round(length_m * 0.22), "씨드스프레이_m2": round(length_m * 1.12)}
    if include_bridge:
        quantities.setdefault("구조물", {})["교량상부공_m"] = round(bridge_length_m)

    result = {
        "disclaimer": "개략 산출 (±20~30% 오차). 실시설계 대체 불가.",
        "road_spec": {
            "length_m": length_m,
            "width_m": width_m,
            "carriage_m": width_m - standard["shoulder"] * 2,
            "pavement_area_m2": pavement_area,
        },
        "quantities": quantities,
        "calculation_basis": {
            "아스콘표층": f"{pavement_area}m² × {standard['ascon_surface_mm'] / 1000:.2f}m × 2.35t/m³",
            "오수맨홀": f"{round(length_m)}m ÷ 50m + 1",
        },
        "inputs": {"pavement_type": pavement_type},
    }
    return wrap_response(result, ProjectDomain.토목_도로)
