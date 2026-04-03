from __future__ import annotations

from civilplan_mcp.db.bootstrap import load_json_data
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def estimate_waste_disposal(*, project_type: str, waste_items: dict[str, float]) -> dict:
    catalog = load_json_data("waste_disposal_prices_2025.json")["prices"]
    details = []
    total_cost = 0
    for name, quantity in waste_items.items():
        price = catalog[name]["price"]
        amount = round(price * quantity)
        total_cost += amount
        details.append({"item": name, "quantity": quantity, "unit_price": price, "amount": amount})

    return wrap_response(
        {
            "project_type": project_type,
            "details": details,
            "summary": {"total_cost_won": total_cost, "item_count": len(details)},
        },
        ProjectDomain.복합,
    )
