# Bird's-Eye View Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 3D bird's-eye view and perspective rendering to CivilPlan MCP using Google's Nano Banana Pro (Gemini 3 Pro Image) API, bump version to 2.0.0, and create a polished release with comprehensive documentation.

**Architecture:** New MCP tool `civilplan_generate_birdseye_view` calls the Gemini API via `google-genai` SDK. A service layer wraps API calls; prompt templates are specialized per project domain (road/building/water/river/landscape). SVG drawings from the existing generator can optionally feed in as reference images via `cairosvg`.

**Tech Stack:** google-genai, cairosvg, Pillow, FastMCP 2.0+, Python 3.11+

---

### Task 1: Add GEMINI_API_KEY to Configuration

**Files:**
- Modify: `civilplan_mcp/config.py`
- Modify: `.env.example`
- Test: `tests/test_config_and_secure_store.py`

- [ ] **Step 1: Write failing test for GEMINI_API_KEY in settings**

Add to `tests/test_config_and_secure_store.py`:

```python
def test_settings_has_gemini_api_key():
    from civilplan_mcp.config import Settings
    s = Settings()
    assert hasattr(s, "gemini_api_key")
    assert s.gemini_api_key == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/test_config_and_secure_store.py::test_settings_has_gemini_api_key -v`
Expected: FAIL — `Settings` has no `gemini_api_key` attribute

- [ ] **Step 3: Add gemini_api_key to Settings and get_settings()**

In `civilplan_mcp/config.py`, add field to `Settings` class:

```python
class Settings(BaseModel):
    # ... existing fields ...
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
```

In `get_settings()`, add after the existing vworld block:

```python
    if not settings.gemini_api_key:
        settings.gemini_api_key = secure_keys.get("GEMINI_API_KEY", "")
```

In `check_api_keys()`, add:

```python
    if not settings.gemini_api_key:
        missing.append("GEMINI_API_KEY")
```

- [ ] **Step 4: Update .env.example**

Append to `.env.example`:

```
GEMINI_API_KEY=
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/test_config_and_secure_store.py::test_settings_has_gemini_api_key -v`
Expected: PASS

- [ ] **Step 6: Run full test suite to check nothing broke**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/ -v`
Expected: All existing tests PASS

- [ ] **Step 7: Commit**

```bash
cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2
git add civilplan_mcp/config.py .env.example tests/test_config_and_secure_store.py
git commit -m "feat: add GEMINI_API_KEY to config system"
```

---

### Task 2: Create Gemini Image Service

**Files:**
- Create: `civilplan_mcp/services/__init__.py`
- Create: `civilplan_mcp/services/gemini_image.py`
- Test: `tests/test_gemini_image.py`

- [ ] **Step 1: Write failing tests for GeminiImageService**

Create `tests/test_gemini_image.py`:

```python
from __future__ import annotations

import base64
from unittest.mock import MagicMock, patch

import pytest


def test_generate_image_returns_dict():
    from civilplan_mcp.services.gemini_image import GeminiImageService

    svc = GeminiImageService(api_key="test-key")
    assert svc.api_key == "test-key"
    assert svc.model == "gemini-3-pro-image-preview"


def test_generate_image_calls_api(tmp_path):
    from civilplan_mcp.services.gemini_image import GeminiImageService

    # Create a fake 1x1 white PNG
    import io
    from PIL import Image as PILImage

    img = PILImage.new("RGB", (1, 1), "white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    fake_png_bytes = buf.getvalue()

    mock_image = MagicMock()
    mock_image.save = MagicMock()

    mock_part = MagicMock()
    mock_part.text = None
    mock_part.inline_data = MagicMock()
    mock_part.as_image.return_value = mock_image

    mock_response = MagicMock()
    mock_response.parts = [mock_part]

    with patch("civilplan_mcp.services.gemini_image.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_response

        svc = GeminiImageService(api_key="test-key")
        result = svc.generate_image(
            prompt="test prompt",
            output_path=str(tmp_path / "test.png"),
            aspect_ratio="16:9",
            image_size="2K",
        )

    assert result["status"] == "success"
    assert result["path"] == str(tmp_path / "test.png")
    mock_image.save.assert_called_once_with(str(tmp_path / "test.png"))


def test_generate_image_with_reference(tmp_path):
    from civilplan_mcp.services.gemini_image import GeminiImageService

    mock_image = MagicMock()
    mock_image.save = MagicMock()

    mock_part = MagicMock()
    mock_part.text = None
    mock_part.inline_data = MagicMock()
    mock_part.as_image.return_value = mock_image

    mock_response = MagicMock()
    mock_response.parts = [mock_part]

    with patch("civilplan_mcp.services.gemini_image.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_response

        svc = GeminiImageService(api_key="test-key")

        # Create a small reference image
        from PIL import Image as PILImage
        ref_path = tmp_path / "ref.png"
        PILImage.new("RGB", (10, 10), "gray").save(str(ref_path))

        result = svc.generate_image(
            prompt="test prompt with reference",
            output_path=str(tmp_path / "out.png"),
            reference_image_path=str(ref_path),
        )

    assert result["status"] == "success"
    # Verify contents list included the reference image
    call_args = mock_client.models.generate_content.call_args
    contents = call_args.kwargs.get("contents") or call_args[1].get("contents")
    assert len(contents) == 2  # prompt + image


def test_generate_image_api_failure(tmp_path):
    from civilplan_mcp.services.gemini_image import GeminiImageService

    with patch("civilplan_mcp.services.gemini_image.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API error")

        svc = GeminiImageService(api_key="test-key")
        result = svc.generate_image(
            prompt="test prompt",
            output_path=str(tmp_path / "fail.png"),
        )

    assert result["status"] == "error"
    assert "API error" in result["error"]


def test_generate_image_no_image_in_response(tmp_path):
    from civilplan_mcp.services.gemini_image import GeminiImageService

    mock_part = MagicMock()
    mock_part.text = "Sorry, I cannot generate that image."
    mock_part.inline_data = None

    mock_response = MagicMock()
    mock_response.parts = [mock_part]

    with patch("civilplan_mcp.services.gemini_image.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_response

        svc = GeminiImageService(api_key="test-key")
        result = svc.generate_image(
            prompt="test prompt",
            output_path=str(tmp_path / "noimg.png"),
        )

    assert result["status"] == "error"
    assert "no image" in result["error"].lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/test_gemini_image.py -v`
Expected: FAIL — module `civilplan_mcp.services.gemini_image` not found

- [ ] **Step 3: Create services package and gemini_image.py**

Create `civilplan_mcp/services/__init__.py`:

```python
```

Create `civilplan_mcp/services/gemini_image.py`:

```python
from __future__ import annotations

import logging
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

logger = logging.getLogger(__name__)


class GeminiImageService:
    def __init__(self, api_key: str, model: str = "gemini-3-pro-image-preview"):
        self.api_key = api_key
        self.model = model
        self._client = genai.Client(api_key=api_key)

    def generate_image(
        self,
        *,
        prompt: str,
        output_path: str,
        reference_image_path: str | None = None,
        aspect_ratio: str = "16:9",
        image_size: str = "2K",
    ) -> dict:
        try:
            contents: list = [prompt]
            if reference_image_path:
                ref_img = Image.open(reference_image_path)
                contents.append(ref_img)

            config = types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
            )

            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )

            for part in response.parts:
                if part.inline_data is not None:
                    image = part.as_image()
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    image.save(output_path)
                    return {"status": "success", "path": output_path}

            return {"status": "error", "error": "No image in API response"}

        except Exception as exc:
            logger.error("Gemini image generation failed: %s", exc)
            return {"status": "error", "error": str(exc)}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/test_gemini_image.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2
git add civilplan_mcp/services/__init__.py civilplan_mcp/services/gemini_image.py tests/test_gemini_image.py
git commit -m "feat: add Gemini image service for Nano Banana Pro API"
```

---

### Task 3: Create Prompt Templates

**Files:**
- Create: `civilplan_mcp/prompts/__init__.py`
- Create: `civilplan_mcp/prompts/birdseye_templates.py`
- Test: `tests/test_birdseye_templates.py`

- [ ] **Step 1: Write failing tests for prompt templates**

Create `tests/test_birdseye_templates.py`:

```python
from __future__ import annotations

import pytest


def test_build_birdseye_prompt_road():
    from civilplan_mcp.prompts.birdseye_templates import build_prompt

    prompt = build_prompt(
        view_type="birdseye",
        project_type="road",
        project_summary="경기도 지방도 890m, 폭 6m, 2차선 아스팔트 도로",
        details={"length_m": 890, "width_m": 6, "lanes": 2, "pavement": "아스콘"},
    )
    assert "bird's-eye view" in prompt.lower() or "aerial" in prompt.lower()
    assert "890" in prompt
    assert "road" in prompt.lower() or "도로" in prompt


def test_build_perspective_prompt_building():
    from civilplan_mcp.prompts.birdseye_templates import build_prompt

    prompt = build_prompt(
        view_type="perspective",
        project_type="building",
        project_summary="서울시 강남구 5층 오피스 빌딩",
        details={"floors": 5, "use": "오피스"},
    )
    assert "perspective" in prompt.lower()
    assert "building" in prompt.lower() or "빌딩" in prompt


def test_all_project_types_have_templates():
    from civilplan_mcp.prompts.birdseye_templates import DOMAIN_PROMPTS

    expected = {"road", "building", "water", "river", "landscape", "mixed"}
    assert set(DOMAIN_PROMPTS.keys()) == expected


def test_build_prompt_unknown_type_uses_mixed():
    from civilplan_mcp.prompts.birdseye_templates import build_prompt

    prompt = build_prompt(
        view_type="birdseye",
        project_type="unknown_type",
        project_summary="Test project",
        details={},
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 50
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/test_birdseye_templates.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Create prompts package and templates**

Create `civilplan_mcp/prompts/__init__.py`:

```python
```

Create `civilplan_mcp/prompts/birdseye_templates.py`:

```python
from __future__ import annotations

from typing import Any

DOMAIN_PROMPTS: dict[str, str] = {
    "road": (
        "Focus on the road alignment cutting through the terrain. "
        "Show road surface markings, lane dividers, shoulders, drainage ditches along both sides, "
        "utility corridors (water/sewer pipes if applicable), guard rails, and traffic signage. "
        "Include surrounding land use context: rice paddies, hills, or residential areas typical of Korean rural/suburban settings."
    ),
    "building": (
        "Focus on the building mass, facade materials, and rooftop details. "
        "Show the site context including parking areas, landscaping, pedestrian paths, and adjacent roads. "
        "Include typical Korean urban context: neighboring buildings, street trees, and utility poles."
    ),
    "water": (
        "Focus on the pipeline route and treatment facility layout. "
        "Show pipe trenches, manholes at regular intervals, pump stations, and connection points. "
        "Include cross-section hints showing pipe burial depth. "
        "Surrounding context: Korean suburban or rural terrain with roads running alongside."
    ),
    "river": (
        "Focus on the riverbank improvements, embankment structures, and flood control elements. "
        "Show gabion walls, riprap, walking paths along the levee, bridge crossings, and flood gates. "
        "Include the water surface with natural flow patterns and riparian vegetation."
    ),
    "landscape": (
        "Focus on the green space design, vegetation patterns, and hardscape elements. "
        "Show walking trails, rest areas with benches, playground equipment, water features, "
        "and ornamental planting beds. Include seasonal Korean trees (cherry blossom, pine, maple)."
    ),
    "mixed": (
        "Show a comprehensive development site with multiple infrastructure elements. "
        "Include roads, buildings, utility corridors, and landscaped areas working together. "
        "Emphasize how different systems connect and interact within the Korean development context."
    ),
}

VIEW_INSTRUCTIONS: dict[str, str] = {
    "birdseye": (
        "Create a photorealistic aerial bird's-eye view rendering, "
        "camera angle approximately 45-60 degrees from above, "
        "showing the full project extent with surrounding context."
    ),
    "perspective": (
        "Create a photorealistic eye-level perspective rendering, "
        "camera positioned at human eye height (1.6m), "
        "showing the project from the most representative viewpoint."
    ),
}


def build_prompt(
    *,
    view_type: str,
    project_type: str,
    project_summary: str,
    details: dict[str, Any],
) -> str:
    view_instruction = VIEW_INSTRUCTIONS.get(view_type, VIEW_INSTRUCTIONS["birdseye"])
    domain_context = DOMAIN_PROMPTS.get(project_type, DOMAIN_PROMPTS["mixed"])

    detail_lines = []
    for key, value in details.items():
        if value is not None:
            detail_lines.append(f"- {key}: {value}")
    detail_block = "\n".join(detail_lines) if detail_lines else "No additional details."

    return (
        f"{view_instruction}\n\n"
        f"Project description: {project_summary}\n\n"
        f"Technical details:\n{detail_block}\n\n"
        f"Domain-specific guidance:\n{domain_context}\n\n"
        f"Style: Professional architectural visualization for a Korean construction project plan. "
        f"Clear daytime weather, natural lighting, high detail. "
        f"Include a subtle north arrow and scale reference in the corner."
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/test_birdseye_templates.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2
git add civilplan_mcp/prompts/__init__.py civilplan_mcp/prompts/birdseye_templates.py tests/test_birdseye_templates.py
git commit -m "feat: add project-type-specific prompt templates for birdseye rendering"
```

---

### Task 4: Create Bird's-Eye View Generator Tool

**Files:**
- Create: `civilplan_mcp/tools/birdseye_generator.py`
- Test: `tests/test_birdseye_generator.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_birdseye_generator.py`:

```python
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


SAMPLE_PROJECT_SPEC = {
    "project_id": "PRJ-20260404-001",
    "domain": "토목_도로",
    "project_type": ["도로"],
    "road": {"class": "소로3류", "length_m": 890, "width_m": 6, "lanes": 2, "pavement": "아스콘"},
    "terrain": "구릉",
    "region": "경기도",
    "year_start": 2026,
    "year_end": 2028,
    "utilities": ["상수도", "하수도"],
}

DOMAIN_MAP = {
    "토목_도로": "road",
    "건축": "building",
    "토목_상하수도": "water",
    "토목_하천": "river",
    "조경": "landscape",
    "복합": "mixed",
}


def _mock_generate_image(**kwargs):
    return {"status": "success", "path": kwargs.get("output_path", "/tmp/test.png")}


@patch("civilplan_mcp.tools.birdseye_generator.get_settings")
@patch("civilplan_mcp.tools.birdseye_generator.GeminiImageService")
def test_generate_birdseye_returns_two_images(mock_svc_cls, mock_settings, tmp_path):
    from civilplan_mcp.tools.birdseye_generator import generate_birdseye_view

    mock_settings.return_value = MagicMock(
        gemini_api_key="test-key",
        output_dir=tmp_path,
    )
    mock_svc = MagicMock()
    mock_svc.generate_image.side_effect = lambda **kw: {
        "status": "success",
        "path": kw["output_path"],
    }
    mock_svc_cls.return_value = mock_svc

    result = generate_birdseye_view(
        project_summary="경기도 지방도 890m 도로",
        project_spec=SAMPLE_PROJECT_SPEC,
    )

    assert result["status"] == "success"
    assert "birdseye_view" in result
    assert "perspective_view" in result
    assert result["birdseye_view"]["status"] == "success"
    assert result["perspective_view"]["status"] == "success"
    assert mock_svc.generate_image.call_count == 2


@patch("civilplan_mcp.tools.birdseye_generator.get_settings")
@patch("civilplan_mcp.tools.birdseye_generator.GeminiImageService")
def test_generate_birdseye_with_svg_reference(mock_svc_cls, mock_settings, tmp_path):
    from civilplan_mcp.tools.birdseye_generator import generate_birdseye_view

    mock_settings.return_value = MagicMock(
        gemini_api_key="test-key",
        output_dir=tmp_path,
    )
    mock_svc = MagicMock()
    mock_svc.generate_image.side_effect = lambda **kw: {
        "status": "success",
        "path": kw["output_path"],
    }
    mock_svc_cls.return_value = mock_svc

    svg_content = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="gray"/></svg>'

    with patch("civilplan_mcp.tools.birdseye_generator.svg_to_png") as mock_svg:
        mock_svg.return_value = str(tmp_path / "ref.png")
        # Create fake ref.png so path exists
        (tmp_path / "ref.png").write_bytes(b"\x89PNG\r\n")

        result = generate_birdseye_view(
            project_summary="경기도 도로",
            project_spec=SAMPLE_PROJECT_SPEC,
            svg_drawing=svg_content,
        )

    assert result["status"] == "success"
    mock_svg.assert_called_once()
    # Both calls should include reference_image_path
    for call in mock_svc.generate_image.call_args_list:
        assert call.kwargs.get("reference_image_path") is not None


@patch("civilplan_mcp.tools.birdseye_generator.get_settings")
def test_generate_birdseye_no_api_key(mock_settings):
    from civilplan_mcp.tools.birdseye_generator import generate_birdseye_view

    mock_settings.return_value = MagicMock(gemini_api_key="")

    result = generate_birdseye_view(
        project_summary="Test",
        project_spec=SAMPLE_PROJECT_SPEC,
    )

    assert result["status"] == "error"
    assert "GEMINI_API_KEY" in result["error"]


@patch("civilplan_mcp.tools.birdseye_generator.get_settings")
@patch("civilplan_mcp.tools.birdseye_generator.GeminiImageService")
def test_generate_birdseye_partial_failure(mock_svc_cls, mock_settings, tmp_path):
    from civilplan_mcp.tools.birdseye_generator import generate_birdseye_view

    mock_settings.return_value = MagicMock(
        gemini_api_key="test-key",
        output_dir=tmp_path,
    )
    call_count = [0]

    def side_effect(**kw):
        call_count[0] += 1
        if call_count[0] == 1:
            return {"status": "success", "path": kw["output_path"]}
        return {"status": "error", "error": "Rate limit exceeded"}

    mock_svc = MagicMock()
    mock_svc.generate_image.side_effect = side_effect
    mock_svc_cls.return_value = mock_svc

    result = generate_birdseye_view(
        project_summary="Test",
        project_spec=SAMPLE_PROJECT_SPEC,
    )

    # Should still return partial results
    assert result["status"] == "partial"
    assert result["birdseye_view"]["status"] == "success"
    assert result["perspective_view"]["status"] == "error"


def test_domain_to_project_type_mapping():
    from civilplan_mcp.tools.birdseye_generator import _domain_to_project_type

    assert _domain_to_project_type("토목_도로") == "road"
    assert _domain_to_project_type("건축") == "building"
    assert _domain_to_project_type("토목_상하수도") == "water"
    assert _domain_to_project_type("토목_하천") == "river"
    assert _domain_to_project_type("조경") == "landscape"
    assert _domain_to_project_type("복합") == "mixed"
    assert _domain_to_project_type("unknown") == "mixed"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/test_birdseye_generator.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Create birdseye_generator.py**

Create `civilplan_mcp/tools/birdseye_generator.py`:

```python
from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any

from civilplan_mcp.config import get_settings
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.prompts.birdseye_templates import build_prompt
from civilplan_mcp.services.gemini_image import GeminiImageService
from civilplan_mcp.tools._base import wrap_response

logger = logging.getLogger(__name__)

DOMAIN_MAP: dict[str, str] = {
    "토목_도로": "road",
    "건축": "building",
    "토목_상하수도": "water",
    "토목_하천": "river",
    "조경": "landscape",
    "복합": "mixed",
}


def _domain_to_project_type(domain: str) -> str:
    return DOMAIN_MAP.get(domain, "mixed")


def svg_to_png(svg_content: str, output_path: str) -> str:
    import cairosvg

    cairosvg.svg2png(bytestring=svg_content.encode("utf-8"), write_to=output_path)
    return output_path


def generate_birdseye_view(
    *,
    project_summary: str,
    project_spec: dict[str, Any],
    svg_drawing: str | None = None,
    resolution: str = "2K",
    output_dir: str | None = None,
) -> dict[str, Any]:
    """Generate bird's-eye view and perspective renderings using Nano Banana Pro."""
    settings = get_settings()

    if not settings.gemini_api_key:
        return {
            "status": "error",
            "error": "GEMINI_API_KEY is not configured. Set it in .env or run setup_keys.py.",
        }

    out = Path(output_dir or settings.output_dir) / "renders"
    out.mkdir(parents=True, exist_ok=True)

    domain = project_spec.get("domain", "복합")
    project_type = _domain_to_project_type(domain)
    project_id = project_spec.get("project_id", "unknown")

    # Extract details for prompt
    details: dict[str, Any] = {}
    road = project_spec.get("road")
    if road:
        details.update({k: v for k, v in road.items() if v is not None})
    details["terrain"] = project_spec.get("terrain")
    details["region"] = project_spec.get("region")
    details["utilities"] = project_spec.get("utilities")

    # Convert SVG to PNG reference if provided
    ref_path: str | None = None
    if svg_drawing:
        try:
            ref_png = str(out / f"{project_id}_ref.png")
            ref_path = svg_to_png(svg_drawing, ref_png)
        except Exception as exc:
            logger.warning("SVG to PNG conversion failed, proceeding without reference: %s", exc)
            ref_path = None

    svc = GeminiImageService(api_key=settings.gemini_api_key)

    results: dict[str, Any] = {}
    for view_type in ("birdseye", "perspective"):
        prompt = build_prompt(
            view_type=view_type,
            project_type=project_type,
            project_summary=project_summary,
            details=details,
        )
        file_path = str(out / f"{project_id}_{view_type}.png")

        result = svc.generate_image(
            prompt=prompt,
            output_path=file_path,
            reference_image_path=ref_path,
            aspect_ratio="16:9",
            image_size=resolution,
        )
        results[f"{view_type}_view"] = result

    birdseye_ok = results["birdseye_view"].get("status") == "success"
    perspective_ok = results["perspective_view"].get("status") == "success"

    if birdseye_ok and perspective_ok:
        status = "success"
    elif birdseye_ok or perspective_ok:
        status = "partial"
    else:
        status = "error"

    domain_enum = ProjectDomain(domain) if domain in ProjectDomain.__members__.values() else ProjectDomain.복합

    return wrap_response(
        {
            "status": status,
            "project_id": project_id,
            "model": "nano-banana-pro (gemini-3-pro-image-preview)",
            "resolution": resolution,
            "birdseye_view": results["birdseye_view"],
            "perspective_view": results["perspective_view"],
        },
        domain_enum,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/test_birdseye_generator.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2
git add civilplan_mcp/tools/birdseye_generator.py tests/test_birdseye_generator.py
git commit -m "feat: add birdseye view generator MCP tool"
```

---

### Task 5: Register Tool in Server and Update Dependencies

**Files:**
- Modify: `civilplan_mcp/server.py`
- Modify: `civilplan_mcp/__init__.py`
- Modify: `requirements.txt`
- Modify: `pyproject.toml`
- Test: `tests/test_server_registration.py`

- [ ] **Step 1: Write failing test for new tool registration**

Add to `tests/test_server_registration.py`:

```python
def test_birdseye_tool_registered():
    from civilplan_mcp.server import build_mcp

    app = build_mcp()
    tool_names = [t.name for t in app._tool_manager.tools.values()]
    assert "civilplan_generate_birdseye_view" in tool_names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/test_server_registration.py::test_birdseye_tool_registered -v`
Expected: FAIL — tool not registered

- [ ] **Step 3: Register tool in server.py**

Add import at top of `civilplan_mcp/server.py`:

```python
from civilplan_mcp.tools.birdseye_generator import generate_birdseye_view
```

Add registration in `build_mcp()` after the last `_register_write_tool` call:

```python
    _register_write_tool(app, "civilplan_generate_birdseye_view", generate_birdseye_view)
```

- [ ] **Step 4: Update version to 2.0.0**

In `civilplan_mcp/__init__.py`:

```python
__all__ = ["__version__"]

__version__ = "2.0.0"
```

In `pyproject.toml`, change:

```toml
version = "2.0.0"
```

In `civilplan_mcp/config.py`, change:

```python
    version: str = "2.0.0"
```

- [ ] **Step 5: Update dependencies**

In `requirements.txt`, add before `pytest`:

```
google-genai>=1.0.0
cairosvg>=2.7.0
Pillow>=10.0.0
```

In `pyproject.toml`, add to dependencies list:

```toml
  "google-genai>=1.0.0",
  "cairosvg>=2.7.0",
  "Pillow>=10.0.0",
```

- [ ] **Step 6: Install new dependencies**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && pip install google-genai cairosvg Pillow`

- [ ] **Step 7: Run test to verify registration passes**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/test_server_registration.py -v`
Expected: PASS (including the new test)

- [ ] **Step 8: Run full test suite**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 9: Commit**

```bash
cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2
git add civilplan_mcp/server.py civilplan_mcp/__init__.py civilplan_mcp/config.py requirements.txt pyproject.toml tests/test_server_registration.py
git commit -m "feat: register birdseye tool, bump to v2.0.0, add new dependencies"
```

---

### Task 6: Write Comprehensive README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read current README for structure reference**

Run: `cat C:/Users/sinmb/workspace/CivilPlan-MCP-v2/README.md`

- [ ] **Step 2: Rewrite README.md**

Full rewrite of `README.md` with these sections:

```markdown
# CivilPlan MCP v2.0

> AI-powered construction project planning for Korean civil engineering and building projects.
> Connects to Claude, ChatGPT, and other AI agents via the Model Context Protocol (MCP).

건설/건축 공사 사업계획을 AI와 함께 만듭니다.
MCP(Model Context Protocol)를 통해 Claude, ChatGPT 등 AI 에이전트와 연결됩니다.

---

## What's New in v2.0

| Feature | Description |
|---------|-------------|
| **3D Bird's-Eye View** | Generate photorealistic aerial and perspective renderings using Nano Banana Pro (Gemini 3 Pro Image) |
| **Perspective Rendering** | Eye-level visualizations for project presentations |
| **SVG Reference Input** | Use existing drawings as reference for more accurate renderings |
| **20 MCP Tools** | Now includes rendering alongside planning, estimation, and documentation |

---

## Features

### Planning & Analysis (11 Tools)

| Tool | Description |
|------|-------------|
| `civilplan_parse_project` | Parse natural language project descriptions into structured data |
| `civilplan_get_legal_procedures` | Identify required permits, approvals, and legal procedures |
| `civilplan_get_phase_checklist` | Get phase-by-phase project checklists |
| `civilplan_evaluate_impact_assessments` | Evaluate 9 environmental/feasibility assessments |
| `civilplan_estimate_quantities` | Calculate material volumes from standard cross-sections |
| `civilplan_get_unit_prices` | Retrieve regional unit cost data (조달청 기준) |
| `civilplan_get_applicable_guidelines` | Find applicable design guidelines |
| `civilplan_fetch_guideline_summary` | Fetch guideline details |
| `civilplan_select_bid_type` | Recommend bidding methodology |
| `civilplan_estimate_waste_disposal` | Calculate construction waste estimates |
| `civilplan_query_land_info` | Query land/cadastral information (V-World API) |

### Financial Analysis (2 Tools)

| Tool | Description |
|------|-------------|
| `civilplan_analyze_feasibility` | IRR, NPV, payback period, DSCR analysis |
| `civilplan_validate_against_benchmark` | Validate costs against government benchmarks |

### Document Generation (7 Tools)

| Tool | Description |
|------|-------------|
| `civilplan_generate_boq_excel` | Excel BOQ with cost breakdown (6 sheets) |
| `civilplan_generate_investment_doc` | Word investment plan document |
| `civilplan_generate_budget_report` | Budget report document |
| `civilplan_generate_schedule` | Gantt-style project timeline (Excel) |
| `civilplan_generate_svg_drawing` | SVG conceptual drawings |
| `civilplan_generate_dxf_drawing` | DXF CAD drawings |
| `civilplan_generate_birdseye_view` | **NEW** 3D aerial + perspective renderings |

### Supported Domains

| Domain | Korean | Status |
|--------|--------|--------|
| Roads | 토목_도로 | Full support |
| Buildings | 건축 | Full support |
| Water/Sewerage | 토목_상하수도 | Full support |
| Rivers | 토목_하천 | Full support |
| Landscaping | 조경 | Partial (in progress) |
| Mixed | 복합 | Full support |

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/sinmb79/Construction-project-master.git
cd Construction-project-master
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```env
# Required for 3D rendering (Nano Banana Pro)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - for land information queries
DATA_GO_KR_API_KEY=your_data_go_kr_key
VWORLD_API_KEY=your_vworld_key
```

**How to get a Gemini API key:**
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API key" in the left sidebar
3. Create a new API key or use an existing project
4. Copy the key to your `.env` file

**Alternative: Encrypted local storage (Windows)**

```bash
python setup_keys.py
```

### 3. Start the Server

```bash
python server.py
```

Server runs at: `http://127.0.0.1:8765/mcp`

---

## Connecting to AI Agents

### Claude Desktop

Add to your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "civilplan": {
      "url": "http://127.0.0.1:8765/mcp"
    }
  }
}
```

Restart Claude Desktop after editing.

### Claude Code (CLI)

```bash
claude mcp add civilplan http://127.0.0.1:8765/mcp
```

### ChatGPT / OpenAI

ChatGPT supports MCP servers via compatible plugins or custom GPT configurations.
Connect using the server URL: `http://127.0.0.1:8765/mcp`

### Other MCP Clients

Any MCP-compatible client can connect using:
- **Transport:** Streamable HTTP
- **URL:** `http://127.0.0.1:8765/mcp`

---

## Example: Full Project Workflow

Input to AI agent:

> "경기도 화성시 지방도 890m, 폭 6m, 2차선 아스팔트 도로, 상하수도 포함, 2026~2028년 시행"

The AI agent can then use CivilPlan tools to:

1. **Parse** → Structured project data (domain, dimensions, region, utilities)
2. **Legal procedures** → 18 required permits, 18-month approval timeline
3. **Impact assessment** → 9 assessment categories evaluated
4. **Quantity estimation** → Material volumes (토공, 포장, 배수, 상하수도)
5. **Unit pricing** → Regional cost data applied (경기도 factor: 1.05)
6. **BOQ generation** → Excel with 6 sheets, total ~10.67 billion KRW
7. **Investment document** → Word document for approval process
8. **Schedule** → Gantt timeline with phase durations
9. **Drawings** → SVG/DXF conceptual drawings
10. **3D Rendering** → Bird's-eye view + perspective visualization

---

## 3D Rendering (Bird's-Eye View)

The `civilplan_generate_birdseye_view` tool generates two images per call:

| Output | Description |
|--------|-------------|
| Bird's-eye view | Aerial 45-60° angle showing full project extent |
| Perspective view | Eye-level view from the most representative viewpoint |

**Input options:**
- Text-only: Uses project description and technical details
- Text + SVG: Uses existing SVG drawing as spatial reference for more accurate results

**Resolution:** 2K (default) or 4K

**Powered by:** Google Nano Banana Pro (Gemini 3 Pro Image) via the `google-genai` SDK

---

## Architecture

```
MCP Client (Claude / ChatGPT / any MCP client)
        │
        │  MCP Protocol (Streamable HTTP)
        ▼
┌─────────────────────────────────────┐
│       CivilPlan MCP Server          │
│       (FastMCP 2.0+)               │
│                                     │
│  ┌──────────┐  ┌──────────────┐    │
│  │ 20 Tools │  │ Data Layer   │    │
│  │ (parse,  │  │ (JSON, SQL,  │    │
│  │  legal,  │  │  CSV)        │    │
│  │  render) │  │              │    │
│  └────┬─────┘  └──────────────┘    │
│       │                             │
│  ┌────▼─────────────────────┐      │
│  │ Services                  │      │
│  │ ├── Gemini Image API     │      │
│  │ ├── V-World API          │      │
│  │ └── Public Data Portal   │      │
│  └───────────────────────────┘      │
└─────────────────────────────────────┘
```

---

## Data Sources

| Data | Source | Update Frequency |
|------|--------|-----------------|
| Unit prices | 조달청 표준시장단가 | Bi-annual (Jan, Jul) |
| Wages | 건설업 임금실태조사 | Bi-annual (Jan, Sep) |
| Legal procedures | 법제처 법령정보 | Manual updates |
| Region factors | 통계청 | Annual |
| Land prices | User-supplied CSV | As needed |

The server includes an automatic update scheduler (APScheduler) that checks for new data releases.

---

## Limitations

| Item | Detail |
|------|--------|
| Accuracy | ±20-30% (planning stage estimates only) |
| Scope | Conceptual planning — not for detailed engineering design |
| Landscaping | Legal procedure data incomplete |
| Land data | Requires manual CSV download to `data/land_prices/` |
| Rendering | Requires internet + Gemini API key |
| Platform | Encrypted key storage (DPAPI) is Windows-only; use `.env` on other platforms |

---

## Disclaimer

> **참고용 개략 자료 — 공식 제출 불가**
>
> All outputs are approximate reference materials for planning purposes only.
> They cannot replace professional engineering design review and are not valid for official submission.
> Verify all results with domain experts before use in actual projects.

---

## License

MIT License. Free to use, modify, and distribute.

## Author

22B Labs — Hongik Ingan: reducing inequality in access to expert planning knowledge.
```

- [ ] **Step 3: Commit**

```bash
cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2
git add README.md
git commit -m "docs: rewrite README for v2.0.0 with rendering guide and connection instructions"
```

---

### Task 7: Final Validation and Release

**Files:**
- No new files

- [ ] **Step 1: Run full test suite**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Verify server starts without errors**

Run: `cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2 && timeout 5 python server.py 2>&1 || true`
Expected: Server starts, shows warnings for missing API keys, no import errors

- [ ] **Step 3: Tag release**

```bash
cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2
git tag -a v2.0.0 -m "v2.0.0: Add 3D bird's-eye view rendering with Nano Banana Pro"
```

- [ ] **Step 4: Push to remote with tags**

```bash
cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2
git push origin main --tags
```

- [ ] **Step 5: Create GitHub release**

```bash
cd C:/Users/sinmb/workspace/CivilPlan-MCP-v2
gh release create v2.0.0 --title "CivilPlan MCP v2.0.0 — 3D Bird's-Eye View Rendering" --notes "$(cat <<'NOTES'
## What's New

### 3D Bird's-Eye View Rendering
- New `civilplan_generate_birdseye_view` MCP tool
- Powered by Google Nano Banana Pro (Gemini 3 Pro Image)
- Generates aerial (bird's-eye) + eye-level (perspective) renderings
- Supports text-only or text + SVG reference image input
- 2K / 4K resolution options
- Domain-specific prompt templates for road, building, water, river, landscape, and mixed projects

### Infrastructure
- New Gemini API integration via `google-genai` SDK
- Added `GEMINI_API_KEY` to configuration system
- Now 20 MCP tools total

### Documentation
- Complete README rewrite with:
  - Tool reference tables
  - Claude Desktop / Claude Code / ChatGPT connection guides
  - API key setup instructions
  - Full workflow example
  - Architecture diagram

## Installation

```bash
git clone https://github.com/sinmb79/Construction-project-master.git
cd Construction-project-master
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
python server.py
```

## Breaking Changes
None. All existing 19 tools remain unchanged.
NOTES
)"
```

Expected: Release created on GitHub
