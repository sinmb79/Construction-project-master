from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from civilplan_mcp.config import get_settings
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.prompts.birdseye_templates import build_prompt
from civilplan_mcp.services.gemini_image import GeminiImageService
from civilplan_mcp.tools._base import wrap_response


logger = logging.getLogger(__name__)

DOMAIN_TO_PROJECT_TYPE = {
    "토목_도로": "road",
    "건축": "building",
    "토목_상하수도": "water",
    "토목_하천": "river",
    "조경": "landscape",
    "복합": "mixed",
}


def _domain_to_project_type(domain: str) -> str:
    return DOMAIN_TO_PROJECT_TYPE.get(domain, "mixed")


def _resolve_domain(domain: str | None) -> ProjectDomain:
    try:
        return ProjectDomain(domain or ProjectDomain.복합.value)
    except ValueError:
        return ProjectDomain.복합


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
) -> dict[str, Any]:
    settings = get_settings()
    domain = _resolve_domain(project_spec.get("domain"))
    project_id = project_spec.get("project_id", "birdseye-render")

    if not settings.gemini_api_key:
        return wrap_response(
            {
                "status": "error",
                "project_id": project_id,
                "error": "GEMINI_API_KEY is not configured. Add it to .env or store it with python setup_keys.py.",
            },
            domain,
        )

    output_dir = Path(project_spec.get("output_dir") or settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    details: dict[str, Any] = {}
    if isinstance(project_spec.get("road"), dict):
        details.update({key: value for key, value in project_spec["road"].items() if value is not None})
    for key in ("terrain", "region", "utilities", "year_start", "year_end"):
        value = project_spec.get(key)
        if value not in (None, "", [], {}):
            details[key] = value

    reference_image_path: str | None = None
    if svg_drawing:
        try:
            reference_image_path = svg_to_png(svg_drawing, str(output_dir / f"{project_id}_reference.png"))
        except Exception as exc:
            logger.warning("Failed to convert SVG reference for birdseye render: %s", exc)

    service = GeminiImageService(api_key=settings.gemini_api_key)
    project_type = _domain_to_project_type(domain.value)

    birdseye_result = service.generate_image(
        prompt=build_prompt(
            view_type="birdseye",
            project_type=project_type,
            project_summary=project_summary,
            details=details,
        ),
        output_path=str(output_dir / f"{project_id}_birdseye.png"),
        reference_image_path=reference_image_path,
        aspect_ratio="16:9",
        image_size=resolution,
    )
    perspective_result = service.generate_image(
        prompt=build_prompt(
            view_type="perspective",
            project_type=project_type,
            project_summary=project_summary,
            details=details,
        ),
        output_path=str(output_dir / f"{project_id}_perspective.png"),
        reference_image_path=reference_image_path,
        aspect_ratio="16:9",
        image_size=resolution,
    )

    if birdseye_result["status"] == "success" and perspective_result["status"] == "success":
        status = "success"
    elif birdseye_result["status"] == "success" or perspective_result["status"] == "success":
        status = "partial"
    else:
        status = "error"

    return wrap_response(
        {
            "status": status,
            "project_id": project_id,
            "model": service.model,
            "resolution": resolution,
            "reference_image_path": reference_image_path,
            "birdseye_view": birdseye_result,
            "perspective_view": perspective_result,
        },
        domain,
    )
