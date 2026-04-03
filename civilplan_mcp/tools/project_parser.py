from __future__ import annotations

from datetime import datetime
import re
from typing import Any

from civilplan_mcp.db.bootstrap import load_json_data
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


DOMAIN_KEYWORDS = {
    ProjectDomain.건축: ["건축", "청사", "센터", "병원", "학교", "복지관", "신축"],
    ProjectDomain.토목_도로: ["도로", "소로", "중로", "대로", "포장", "진입도로"],
    ProjectDomain.토목_상하수도: ["상수도", "하수도", "오수", "우수", "정수장"],
    ProjectDomain.토목_하천: ["하천", "제방", "호안", "배수"],
    ProjectDomain.조경: ["조경", "공원", "녹지", "식재", "수목", "정원"],
}

TERRAIN_MAP = {
    "평지": ("평지", 1.0),
    "구릉": ("구릉", 1.4),
    "둔턱": ("구릉", 1.4),
    "산지": ("산지", 2.0),
}


def _match_number(pattern: str, description: str) -> float | None:
    matched = re.search(pattern, description, flags=re.IGNORECASE)
    return float(matched.group(1)) if matched else None


def _detect_domain(description: str) -> tuple[ProjectDomain, list[str]]:
    detected: list[ProjectDomain] = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(keyword in description for keyword in keywords):
            detected.append(domain)

    if not detected:
        return ProjectDomain.복합, []
    if ProjectDomain.토목_도로 in detected and ProjectDomain.토목_상하수도 in detected and len(detected) == 2:
        return ProjectDomain.토목_도로, [ProjectDomain.토목_상하수도.value]
    if len(detected) == 1:
        return detected[0], []
    return ProjectDomain.복합, [item.value for item in detected]


def parse_project(*, description: str) -> dict[str, Any]:
    region_factors = load_json_data("region_factors.json")
    domain, sub_domains = _detect_domain(description)

    road_length = _match_number(r"L\s*=\s*([0-9]+(?:\.[0-9]+)?)m", description)
    road_width = _match_number(r"B\s*=\s*([0-9]+(?:\.[0-9]+)?)m", description)
    lanes = int(_match_number(r"([0-9]+)\s*차선", description) or 2)
    years = re.search(r"(20[0-9]{2})\s*[~\-]\s*(20[0-9]{2})", description)

    terrain = "평지"
    terrain_factor = 1.0
    for keyword, (terrain_name, factor) in TERRAIN_MAP.items():
        if keyword in description:
            terrain = terrain_name
            terrain_factor = factor
            break

    region = next((name for name in region_factors if name in description), "경기도")
    year_start = int(years.group(1)) if years else datetime.now().year
    year_end = int(years.group(2)) if years else year_start
    utilities = [utility for utility in ("상수도", "하수도") if utility in description]
    pavement = "아스콘" if "아스콘" in description else "콘크리트" if "콘크리트" in description else None
    road_class = "소로" if "소로" in description else "중로" if "중로" in description else "대로" if "대로" in description else None

    result = {
        "project_id": f"PRJ-{datetime.now():%Y%m%d}-001",
        "domain": domain.value,
        "sub_domains": sub_domains,
        "project_type": [item for item in ["도로", "건축", "상수도", "하수도"] if item in description] or [domain.value],
        "road": {
            "class": road_class,
            "length_m": road_length,
            "width_m": road_width,
            "lanes": lanes,
            "pavement": pavement,
        },
        "terrain": terrain,
        "terrain_factor": terrain_factor,
        "region": region,
        "region_factor": region_factors[region]["factor"],
        "year_start": year_start,
        "year_end": year_end,
        "duration_years": year_end - year_start + 1,
        "utilities": utilities,
        "has_farmland": None,
        "has_forest": None,
        "has_river": None,
        "parsed_confidence": 0.92 if road_length and road_width else 0.72,
        "ambiguities": [],
        "warnings": [],
    }

    if sub_domains:
        result["domain_warning"] = f"복합 사업 감지: {', '.join(sub_domains)}"

    return wrap_response(result, domain)
