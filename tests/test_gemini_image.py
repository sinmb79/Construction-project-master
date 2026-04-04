from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PIL import Image as PILImage


def test_service_defaults_to_nano_banana_pro_model() -> None:
    from civilplan_mcp.services.gemini_image import GeminiImageService

    service = GeminiImageService(api_key="test-key", client=MagicMock())

    assert service.api_key == "test-key"
    assert service.model == "gemini-3-pro-image-preview"


def test_service_requires_sdk_or_client() -> None:
    from civilplan_mcp.services import gemini_image
    from civilplan_mcp.services.gemini_image import GeminiImageService

    original_genai = gemini_image.genai
    gemini_image.genai = None
    try:
        with pytest.raises(RuntimeError):
            GeminiImageService(api_key="test-key")
    finally:
        gemini_image.genai = original_genai


def test_generate_image_calls_api_and_saves_output(tmp_path) -> None:
    from civilplan_mcp.services.gemini_image import GeminiImageService

    mock_client = MagicMock()
    mock_image = MagicMock()
    mock_part = MagicMock()
    mock_part.inline_data = MagicMock()
    mock_part.text = None
    mock_part.as_image.return_value = mock_image
    mock_client.models.generate_content.return_value = MagicMock(parts=[mock_part])

    service = GeminiImageService(api_key="test-key", client=mock_client)
    output_path = tmp_path / "generated.png"

    result = service.generate_image(
        prompt="Generate a bird's-eye render of a Korean road project.",
        output_path=str(output_path),
        aspect_ratio="16:9",
        image_size="2K",
    )

    assert result["status"] == "success"
    assert result["path"] == str(output_path)
    mock_image.save.assert_called_once_with(str(output_path))
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "gemini-3-pro-image-preview"
    assert call_kwargs["contents"] == ["Generate a bird's-eye render of a Korean road project."]
    assert call_kwargs["config"] is not None


def test_generate_image_with_reference_includes_image_content(tmp_path) -> None:
    from civilplan_mcp.services.gemini_image import GeminiImageService

    reference_path = tmp_path / "reference.png"
    PILImage.new("RGB", (8, 8), "gray").save(reference_path)

    mock_client = MagicMock()
    mock_image = MagicMock()
    mock_part = MagicMock()
    mock_part.inline_data = MagicMock()
    mock_part.text = None
    mock_part.as_image.return_value = mock_image
    mock_client.models.generate_content.return_value = MagicMock(parts=[mock_part])

    service = GeminiImageService(api_key="test-key", client=mock_client)
    output_path = tmp_path / "generated.png"

    result = service.generate_image(
        prompt="Generate a road perspective render.",
        output_path=str(output_path),
        reference_image_path=str(reference_path),
    )

    assert result["status"] == "success"
    contents = mock_client.models.generate_content.call_args.kwargs["contents"]
    assert len(contents) == 2
    assert contents[0] == "Generate a road perspective render."


def test_generate_image_returns_error_on_api_failure(tmp_path) -> None:
    from civilplan_mcp.services.gemini_image import GeminiImageService

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("API error")
    service = GeminiImageService(api_key="test-key", client=mock_client)

    result = service.generate_image(
        prompt="Generate a river project render.",
        output_path=str(tmp_path / "generated.png"),
    )

    assert result["status"] == "error"
    assert "API error" in result["error"]


def test_generate_image_returns_error_when_response_has_no_image(tmp_path) -> None:
    from civilplan_mcp.services.gemini_image import GeminiImageService

    mock_client = MagicMock()
    mock_part = MagicMock()
    mock_part.inline_data = None
    mock_part.text = "No image available."
    mock_client.models.generate_content.return_value = MagicMock(parts=[mock_part])
    service = GeminiImageService(api_key="test-key", client=mock_client)

    result = service.generate_image(
        prompt="Generate a building render.",
        output_path=str(tmp_path / "generated.png"),
    )

    assert result["status"] == "error"
    assert "no image" in result["error"].lower()
