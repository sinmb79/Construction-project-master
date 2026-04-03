from __future__ import annotations

from typing import Any

from civilplan_mcp.db.bootstrap import load_json_data
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def get_unit_prices(*, category: str | None = None, item_name: str | None = None, region: str = "경기도", year: int = 2026) -> dict[str, Any]:
    prices = load_json_data("unit_prices_2026.json")["items"]
    region_factors = load_json_data("region_factors.json")
    factor = region_factors[region]["factor"]

    filtered = []
    for item in prices:
        if category and item["category"] != category:
            continue
        if item_name and item_name not in item["item"]:
            continue
        filtered.append(
            {
                "category": item["category"],
                "item": item["item"],
                "spec": item["spec"],
                "unit": item["unit"],
                "base_price": item["base_price"],
                "region_factor": factor,
                "adjusted_price": round(item["base_price"] * factor),
                "source": item["source"],
                "note": f"{region} 지역계수 {factor:.2f} 적용",
                "year": year,
            }
        )

    return wrap_response(
        {
            "query": {"category": category, "item_name": item_name, "region": region, "year": year},
            "results": filtered,
            "region_factor_note": f"{region}: {factor:.2f}",
        },
        ProjectDomain.복합,
    )
