from __future__ import annotations

from pathlib import Path
from typing import Any

import svgwrite

from civilplan_mcp.config import get_settings
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def generate_svg_drawing(
    *,
    drawing_type: str,
    project_spec: dict[str, Any],
    quantities: dict[str, Any],
    scale: str = "1:200",
    output_filename: str | None = None,
) -> dict[str, Any]:
    output_dir = Path(project_spec.get("output_dir", get_settings().output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / (output_filename or f"{drawing_type}.svg")

    length = float(project_spec["road"]["length_m"] or 100.0)
    width = float(project_spec["road"]["width_m"] or 6.0)
    drawing = svgwrite.Drawing(str(path), size=("800px", "240px"))
    drawing.add(drawing.rect(insert=(20, 80), size=(min(720, length / 2), width * 10), fill="#d9d9d9", stroke="#1f1f1f"))
    drawing.add(drawing.text(drawing_type, insert=(20, 30), font_size="20px"))
    drawing.add(drawing.text(f"Scale {scale}", insert=(20, 55), font_size="12px"))
    drawing.add(drawing.text("CivilPlan conceptual drawing", insert=(20, 220), font_size="12px"))
    drawing.save()

    return wrap_response(
        {
            "status": "success",
            "file_path": str(path),
            "drawing_type": drawing_type,
            "quantity_sections": list(quantities["quantities"].keys()),
        },
        ProjectDomain.토목_도로,
    )
