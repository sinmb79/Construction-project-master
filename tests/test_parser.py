from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools.project_parser import parse_project


def test_parse_project_extracts_core_road_fields() -> None:
    result = parse_project(
        description="소로 신설 L=890m B=6m 아스콘 2차선 상하수도 경기도 둔턱지역 2026~2028"
    )

    assert result["road"]["length_m"] == 890
    assert result["road"]["width_m"] == 6.0
    assert result["road"]["lanes"] == 2
    assert result["region"] == "경기도"
    assert result["domain"] == ProjectDomain.토목_도로.value


def test_parse_project_marks_composite_domain_warning() -> None:
    result = parse_project(description="복지관 신축 및 진입도로 개설")

    assert result["domain"] == ProjectDomain.복합.value
    assert "domain_warning" in result
