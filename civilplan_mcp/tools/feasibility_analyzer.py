from __future__ import annotations

from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def analyze_feasibility(
    *,
    land_area_m2: float,
    land_price_per_m2: float,
    land_price_multiplier: float = 1.3,
    construction_cost_total: float,
    other_costs_million: float = 0,
    revenue_type: str,
    building_floor_area_m2: float,
    sale_price_per_m2: float | None = None,
    monthly_rent_per_m2: float | None = None,
    vacancy_rate_pct: float = 10.0,
    operating_expense_pct: float = 20.0,
    equity_ratio_pct: float = 30.0,
    loan_rate_pct: float = 5.5,
    loan_term_years: int = 10,
    construction_months: int = 24,
    sale_months: int = 12,
) -> dict:
    land_cost = round(land_area_m2 * land_price_per_m2 * land_price_multiplier)
    soft_cost = round(construction_cost_total * 0.12 + other_costs_million * 1_000_000)
    debt_ratio = 1 - (equity_ratio_pct / 100)
    debt = round((land_cost + construction_cost_total + soft_cost) * debt_ratio)
    equity = round((land_cost + construction_cost_total + soft_cost) - debt)
    financing_cost = round(debt * (loan_rate_pct / 100) * (construction_months / 12) * 0.5)
    total_investment = land_cost + construction_cost_total + soft_cost + financing_cost

    if revenue_type == "임대":
        gross_annual_rent = round(building_floor_area_m2 * float(monthly_rent_per_m2 or 0) * 12)
        net_annual_rent = round(gross_annual_rent * (1 - vacancy_rate_pct / 100) * (1 - operating_expense_pct / 100))
        stabilized_value = round(net_annual_rent / 0.06)
        revenue_total = stabilized_value
    elif revenue_type == "분양":
        revenue_total = round(building_floor_area_m2 * float(sale_price_per_m2 or 0))
        gross_annual_rent = 0
        net_annual_rent = 0
        stabilized_value = revenue_total
    else:
        revenue_total = total_investment
        gross_annual_rent = 0
        net_annual_rent = 0
        stabilized_value = total_investment

    profit = revenue_total - total_investment
    monthly_payment = round(debt * ((loan_rate_pct / 100) / 12 + 1 / (loan_term_years * 12)))
    dscr = round((net_annual_rent / max(monthly_payment * 12, 1)), 2) if monthly_payment else 0
    irr_pct = round((profit / max(total_investment, 1)) * 100 / max((construction_months + sale_months) / 12, 1), 1)
    npv_won = round(profit / 1.06)
    payback_years = round(total_investment / max(net_annual_rent, 1), 1) if net_annual_rent else 0
    equity_multiple = round(revenue_total / max(equity, 1), 2)

    return wrap_response(
        {
            "cost_structure": {
                "land_cost": land_cost,
                "construction_cost": construction_cost_total,
                "soft_cost": soft_cost,
                "financing_cost": financing_cost,
                "total_investment": total_investment,
            },
            "revenue_projection": {
                "type": revenue_type,
                "gross_annual_rent": gross_annual_rent,
                "net_annual_rent": net_annual_rent,
                "stabilized_value": stabilized_value,
            },
            "returns": {
                "profit": profit,
                "profit_margin_pct": round((profit / max(total_investment, 1)) * 100, 1),
                "irr_pct": irr_pct,
                "npv_won": npv_won,
                "payback_years": payback_years,
                "equity_multiple": equity_multiple,
            },
            "loan_structure": {
                "equity": equity,
                "debt": debt,
                "monthly_payment": monthly_payment,
                "dscr": dscr,
            },
            "sensitivity": {
                "rent_down_10pct": "IRR sensitivity check required",
                "rate_up_100bp": "Financing sensitivity check required",
                "cost_up_10pct": "Cost sensitivity check required",
            },
            "verdict": "투자 검토 가능" if profit > 0 else "재검토 필요",
        },
        ProjectDomain.복합,
    )
