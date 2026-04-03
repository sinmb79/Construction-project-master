from civilplan_mcp.tools.quantity_estimator import estimate_quantities
from civilplan_mcp.tools.unit_price_query import get_unit_prices


def test_estimate_quantities_returns_expected_pavement_area() -> None:
    result = estimate_quantities(
        road_class="소로",
        length_m=890,
        width_m=6.0,
        terrain="구릉",
        pavement_type="아스콘",
        include_water_supply=True,
        include_sewage=True,
        include_retaining_wall=True,
        include_bridge=False,
        bridge_length_m=0.0,
    )

    assert result["road_spec"]["pavement_area_m2"] == 5340.0
    assert result["quantities"]["포장"]["아스콘표층_t"] > 0


def test_get_unit_prices_applies_region_factor() -> None:
    result = get_unit_prices(category="포장", item_name="아스콘", region="경기도", year=2026)

    assert result["results"]
    assert result["results"][0]["adjusted_price"] > result["results"][0]["base_price"]
