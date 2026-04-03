from __future__ import annotations

from pathlib import Path
from typing import Any

from openpyxl import Workbook

from civilplan_mcp.config import get_settings
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


def generate_schedule(
    *,
    project_name: str,
    project_spec: dict[str, Any],
    legal_procedures: dict[str, Any],
    output_filename: str | None = None,
) -> dict[str, Any]:
    output_dir = Path(project_spec.get("output_dir", get_settings().output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / (output_filename or f"{project_name}_schedule.xlsx")

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "일정표"
    sheet.append(["단계", "소요일", "비고"])
    for phase, procedures in legal_procedures.get("phases", {}).items():
        sheet.append([phase, len(procedures), "자동 생성"])
    workbook.save(path)

    return wrap_response({"status": "success", "file_path": str(path)}, ProjectDomain.복합)
