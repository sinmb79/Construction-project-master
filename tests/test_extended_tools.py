from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools.bid_type_selector import select_bid_type
from civilplan_mcp.tools.guideline_fetcher import fetch_guideline_summary
from civilplan_mcp.tools.guideline_resolver import get_applicable_guidelines
from civilplan_mcp.tools.waste_estimator import estimate_waste_disposal


def test_get_applicable_guidelines_returns_matches() -> None:
    result = get_applicable_guidelines(
        domain=ProjectDomain.토목_도로,
        procedure_ids=["PER-01"],
        project_type="도로",
    )

    assert result["guidelines"]


def test_fetch_guideline_summary_returns_catalog_summary() -> None:
    result = fetch_guideline_summary(guideline_id="GL-001")

    assert result["summary"]["id"] == "GL-001"


def test_select_bid_type_chooses_comprehensive_for_large_cost() -> None:
    result = select_bid_type(total_cost_billion=350.0, domain=ProjectDomain.건축)

    assert result["recommended_type"] == "종합심사낙찰제"


def test_estimate_waste_disposal_returns_cost() -> None:
    result = estimate_waste_disposal(
        project_type="도로",
        waste_items={"폐콘크리트": 100, "폐아스팔트콘크리트": 50},
    )

    assert result["summary"]["total_cost_won"] > 0
