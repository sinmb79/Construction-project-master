from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def test_project_domain_contains_expected_values() -> None:
    assert ProjectDomain.건축.value == "건축"
    assert ProjectDomain.토목_도로.value == "토목_도로"
    assert ProjectDomain.복합.value == "복합"


def test_wrap_response_adds_required_disclaimers() -> None:
    wrapped = wrap_response({"status": "ok"}, ProjectDomain.토목_도로)

    assert wrapped["status"] == "ok"
    assert "domain_note" in wrapped
    assert "validity_disclaimer" in wrapped
    assert wrapped["data_as_of"] == "2026년 4월 기준"
