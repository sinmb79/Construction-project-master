from __future__ import annotations

from unittest.mock import MagicMock

from civilplan_mcp.tools.project_parser import parse_project


def _sample_project_spec(tmp_path) -> dict:
    project_spec = parse_project(
        description="도로 신설 L=890m B=6m 아스콘 2차선 상하수도 경기도 화성시 2026~2028"
    )
    project_spec["project_id"] = "PRJ-20260404-001"
    project_spec["output_dir"] = str(tmp_path)
    return project_spec


def test_generate_birdseye_view_returns_both_images(monkeypatch, tmp_path) -> None:
    from civilplan_mcp.tools import birdseye_generator

    mock_service = MagicMock()
    mock_service.generate_image.side_effect = lambda **kwargs: {
        "status": "success",
        "path": kwargs["output_path"],
    }

    monkeypatch.setattr(
        birdseye_generator,
        "get_settings",
        lambda: MagicMock(gemini_api_key="test-key", output_dir=tmp_path),
    )
    monkeypatch.setattr(
        birdseye_generator,
        "GeminiImageService",
        lambda **kwargs: mock_service,
    )

    result = birdseye_generator.generate_birdseye_view(
        project_summary="경기도 화성시 도로 신설 890m",
        project_spec=_sample_project_spec(tmp_path),
    )

    assert result["status"] == "success"
    assert result["birdseye_view"]["status"] == "success"
    assert result["perspective_view"]["status"] == "success"
    assert mock_service.generate_image.call_count == 2
    assert "validity_disclaimer" in result


def test_generate_birdseye_view_uses_svg_reference(monkeypatch, tmp_path) -> None:
    from civilplan_mcp.tools import birdseye_generator

    reference_path = tmp_path / "reference.png"
    reference_path.write_bytes(b"png")

    mock_service = MagicMock()
    mock_service.generate_image.return_value = {"status": "success", "path": str(tmp_path / "out.png")}

    monkeypatch.setattr(
        birdseye_generator,
        "get_settings",
        lambda: MagicMock(gemini_api_key="test-key", output_dir=tmp_path),
    )
    monkeypatch.setattr(
        birdseye_generator,
        "GeminiImageService",
        lambda **kwargs: mock_service,
    )
    monkeypatch.setattr(
        birdseye_generator,
        "svg_to_png",
        lambda svg_content, output_path: str(reference_path),
    )

    result = birdseye_generator.generate_birdseye_view(
        project_summary="경기도 화성시 도로 신설 890m",
        project_spec=_sample_project_spec(tmp_path),
        svg_drawing="<svg></svg>",
    )

    assert result["status"] == "success"
    for call in mock_service.generate_image.call_args_list:
        assert call.kwargs["reference_image_path"] == str(reference_path)


def test_generate_birdseye_view_requires_gemini_key(monkeypatch, tmp_path) -> None:
    from civilplan_mcp.tools import birdseye_generator

    monkeypatch.setattr(
        birdseye_generator,
        "get_settings",
        lambda: MagicMock(gemini_api_key="", output_dir=tmp_path),
    )

    result = birdseye_generator.generate_birdseye_view(
        project_summary="경기도 화성시 도로 신설 890m",
        project_spec=_sample_project_spec(tmp_path),
    )

    assert result["status"] == "error"
    assert "GEMINI_API_KEY" in result["error"]


def test_generate_birdseye_view_returns_partial_if_one_view_fails(monkeypatch, tmp_path) -> None:
    from civilplan_mcp.tools import birdseye_generator

    mock_service = MagicMock()
    mock_service.generate_image.side_effect = [
        {"status": "success", "path": str(tmp_path / "birdseye.png")},
        {"status": "error", "error": "rate limit"},
    ]

    monkeypatch.setattr(
        birdseye_generator,
        "get_settings",
        lambda: MagicMock(gemini_api_key="test-key", output_dir=tmp_path),
    )
    monkeypatch.setattr(
        birdseye_generator,
        "GeminiImageService",
        lambda **kwargs: mock_service,
    )

    result = birdseye_generator.generate_birdseye_view(
        project_summary="경기도 화성시 도로 신설 890m",
        project_spec=_sample_project_spec(tmp_path),
    )

    assert result["status"] == "partial"
    assert result["birdseye_view"]["status"] == "success"
    assert result["perspective_view"]["status"] == "error"


def test_domain_to_project_type_mapping() -> None:
    from civilplan_mcp.tools.birdseye_generator import _domain_to_project_type

    assert _domain_to_project_type("토목_도로") == "road"
    assert _domain_to_project_type("건축") == "building"
    assert _domain_to_project_type("토목_상하수도") == "water"
    assert _domain_to_project_type("토목_하천") == "river"
    assert _domain_to_project_type("조경") == "landscape"
    assert _domain_to_project_type("복합") == "mixed"
    assert _domain_to_project_type("unknown") == "mixed"
