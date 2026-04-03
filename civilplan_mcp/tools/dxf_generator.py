from __future__ import annotations

from pathlib import Path

import ezdxf

from civilplan_mcp.config import get_settings
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


DXF_LAYERS = [
    "ROAD-OUTLINE",
    "ROAD-PAVEMENT",
    "ROAD-DRAINAGE",
    "PIPE-WATER",
    "PIPE-SEWER",
    "PIPE-STORM",
    "DIM",
    "TEXT",
    "TITLE-BLOCK",
]


def generate_dxf_drawing(
    *,
    drawing_type: str,
    project_spec: dict,
    quantities: dict,
    scale: str = "1:200",
    output_filename: str | None = None,
) -> dict:
    output_dir = Path(project_spec.get("output_dir", get_settings().output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / (output_filename or f"{drawing_type}.dxf")

    doc = ezdxf.new("R2018")
    msp = doc.modelspace()
    for layer in DXF_LAYERS:
        if layer not in doc.layers:
            doc.layers.add(layer)

    width = float(project_spec["road"]["width_m"] or 6.0)
    length = min(float(project_spec["road"]["length_m"] or 100.0), 200.0)
    msp.add_lwpolyline([(0, 0), (length, 0), (length, width), (0, width), (0, 0)], dxfattribs={"layer": "ROAD-OUTLINE"})
    msp.add_text(f"{drawing_type} {scale}", dxfattribs={"layer": "TEXT", "height": 2.5}).set_placement((0, width + 5))
    msp.add_text("CivilPlan conceptual DXF", dxfattribs={"layer": "TITLE-BLOCK", "height": 2.5}).set_placement((0, -5))
    doc.saveas(path)

    return wrap_response(
        {
            "status": "success",
            "file_path": str(path),
            "drawing_type": drawing_type,
            "layers": DXF_LAYERS,
            "quantity_sections": list(quantities["quantities"].keys()),
        },
        ProjectDomain.토목_도로,
    )
