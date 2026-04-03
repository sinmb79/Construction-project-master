"""
CivilPlan MCP Server
LICENSE: MIT
PHILOSOPHY: Hongik Ingan - reduce inequality in access to expert planning knowledge.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator

from fastmcp import FastMCP

from civilplan_mcp import __version__
from civilplan_mcp.config import check_api_keys, get_settings
from civilplan_mcp.tools.benchmark_validator import validate_against_benchmark
from civilplan_mcp.tools.bid_type_selector import select_bid_type
from civilplan_mcp.tools.boq_generator import generate_boq_excel
from civilplan_mcp.tools.budget_report_generator import generate_budget_report
from civilplan_mcp.tools.doc_generator import generate_investment_doc
from civilplan_mcp.tools.drawing_generator import generate_svg_drawing
from civilplan_mcp.tools.dxf_generator import generate_dxf_drawing
from civilplan_mcp.tools.feasibility_analyzer import analyze_feasibility
from civilplan_mcp.tools.guideline_fetcher import fetch_guideline_summary
from civilplan_mcp.tools.guideline_resolver import get_applicable_guidelines
from civilplan_mcp.tools.impact_evaluator import evaluate_impact_assessments
from civilplan_mcp.tools.land_info_query import query_land_info
from civilplan_mcp.tools.legal_procedures import get_legal_procedures
from civilplan_mcp.tools.phase_checklist import get_phase_checklist
from civilplan_mcp.tools.project_parser import parse_project
from civilplan_mcp.tools.quantity_estimator import estimate_quantities
from civilplan_mcp.tools.schedule_generator import generate_schedule
from civilplan_mcp.tools.unit_price_query import get_unit_prices
from civilplan_mcp.tools.waste_estimator import estimate_waste_disposal
from civilplan_mcp.updater.scheduler import build_scheduler
from civilplan_mcp.updater.wage_updater import check_update_flags


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def build_server_config() -> dict[str, object]:
    settings = get_settings()
    return {
        "name": settings.app_name,
        "version": settings.version,
        "host": settings.host,
        "port": settings.port,
        "path": settings.http_path,
    }


@asynccontextmanager
async def civilplan_lifespan(_: FastMCP) -> AsyncIterator[dict[str, object]]:
    warnings = check_update_flags()
    if warnings:
        logger.warning("=== 자동 갱신 실패 항목 감지 ===")
        for warning in warnings:
            logger.warning(warning)
    logger.warning("⚠️  일부 기준 자료가 수년 전 기준입니다. 실제 적용 전 law.go.kr 최신 고시 확인 필수.")

    missing_keys = check_api_keys()
    for key in missing_keys:
        logger.warning("API key missing: %s", key)
    if missing_keys:
        logger.warning("Provide keys in .env or run `python setup_keys.py` for encrypted local storage.")

    scheduler = build_scheduler(start=True)
    try:
        yield {"missing_api_keys": missing_keys}
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)


def _register_read_tool(app: FastMCP, name: str, fn) -> None:
    app.tool(name=name, annotations={"readOnlyHint": True, "idempotentHint": True})(fn)


def _register_write_tool(app: FastMCP, name: str, fn) -> None:
    app.tool(name=name, annotations={})(fn)


def build_mcp() -> FastMCP:
    app = FastMCP(
        name="civilplan_mcp",
        version=__version__,
        instructions=(
            "CivilPlan supports conceptual planning for Korean civil and building projects. "
            "All numeric outputs are approximate and not valid for formal submission."
        ),
        lifespan=civilplan_lifespan,
    )

    _register_read_tool(app, "civilplan_parse_project", parse_project)
    _register_read_tool(app, "civilplan_get_legal_procedures", get_legal_procedures)
    _register_read_tool(app, "civilplan_get_phase_checklist", get_phase_checklist)
    _register_read_tool(app, "civilplan_evaluate_impact_assessments", evaluate_impact_assessments)
    _register_read_tool(app, "civilplan_estimate_quantities", estimate_quantities)
    _register_read_tool(app, "civilplan_get_unit_prices", get_unit_prices)
    _register_write_tool(app, "civilplan_generate_boq_excel", generate_boq_excel)
    _register_write_tool(app, "civilplan_generate_investment_doc", generate_investment_doc)
    _register_write_tool(app, "civilplan_generate_schedule", generate_schedule)
    _register_write_tool(app, "civilplan_generate_svg_drawing", generate_svg_drawing)
    _register_read_tool(app, "civilplan_get_applicable_guidelines", get_applicable_guidelines)
    _register_read_tool(app, "civilplan_fetch_guideline_summary", fetch_guideline_summary)
    _register_read_tool(app, "civilplan_select_bid_type", select_bid_type)
    _register_read_tool(app, "civilplan_estimate_waste_disposal", estimate_waste_disposal)
    _register_read_tool(app, "civilplan_query_land_info", query_land_info)
    _register_read_tool(app, "civilplan_analyze_feasibility", analyze_feasibility)
    _register_read_tool(app, "civilplan_validate_against_benchmark", validate_against_benchmark)
    _register_write_tool(app, "civilplan_generate_budget_report", generate_budget_report)
    _register_write_tool(app, "civilplan_generate_dxf_drawing", generate_dxf_drawing)
    return app


def main() -> None:
    app = build_mcp()
    settings = get_settings()
    app.run(
        transport="streamable-http",
        host=settings.host,
        port=settings.port,
        path=settings.http_path,
        show_banner=False,
    )


if __name__ == "__main__":
    main()
