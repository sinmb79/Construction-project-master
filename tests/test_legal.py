from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools.legal_procedures import get_legal_procedures
from civilplan_mcp.tools.phase_checklist import get_phase_checklist


def test_get_legal_procedures_returns_domain_specific_items() -> None:
    result = get_legal_procedures(
        domain=ProjectDomain.토목_도로,
        project_type="도로",
        total_cost_billion=10.67,
        road_length_m=890,
        development_area_m2=5340,
        region="경기도",
        has_farmland=False,
        has_forest=False,
        has_river=False,
        is_public=True,
    )

    assert result["summary"]["total_procedures"] >= 2
    assert "인허가" in result["phases"]


def test_get_phase_checklist_returns_preparing_message_for_landscape() -> None:
    result = get_phase_checklist(
        domain=ProjectDomain.조경,
        phase="기획",
        project_type="조경",
        total_cost_billion=3.0,
        has_building=False,
        has_bridge=False,
    )

    assert result["status"] == "not_ready"
