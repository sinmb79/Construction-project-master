from __future__ import annotations


def test_build_birdseye_prompt_for_road() -> None:
    from civilplan_mcp.prompts.birdseye_templates import build_prompt

    prompt = build_prompt(
        view_type="birdseye",
        project_type="road",
        project_summary="경기도 지방도 890m, 폭 6m, 2차선 아스팔트 포장 도로",
        details={"length_m": 890, "width_m": 6, "lanes": 2, "pavement": "아스팔트"},
    )

    assert "bird's-eye view" in prompt.lower()
    assert "890" in prompt
    assert "road" in prompt.lower()


def test_build_perspective_prompt_for_building() -> None:
    from civilplan_mcp.prompts.birdseye_templates import build_prompt

    prompt = build_prompt(
        view_type="perspective",
        project_type="building",
        project_summary="서울시 강남구 5층 오피스 빌딩",
        details={"floors": 5, "use": "오피스"},
    )

    assert "perspective" in prompt.lower()
    assert "building" in prompt.lower()


def test_all_project_types_have_templates() -> None:
    from civilplan_mcp.prompts.birdseye_templates import DOMAIN_PROMPTS

    assert set(DOMAIN_PROMPTS) == {"road", "building", "water", "river", "landscape", "mixed"}


def test_unknown_project_type_falls_back_to_mixed() -> None:
    from civilplan_mcp.prompts.birdseye_templates import build_prompt

    prompt = build_prompt(
        view_type="birdseye",
        project_type="unknown",
        project_summary="복합 개발 프로젝트",
        details={},
    )

    assert isinstance(prompt, str)
    assert len(prompt) > 50
    assert "comprehensive development site" in prompt.lower()
