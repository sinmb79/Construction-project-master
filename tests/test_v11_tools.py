from pathlib import Path

import ezdxf

from civilplan_mcp.config import Settings
from civilplan_mcp.tools.benchmark_validator import validate_against_benchmark
from civilplan_mcp.tools.budget_report_generator import generate_budget_report
from civilplan_mcp.tools.dxf_generator import generate_dxf_drawing
from civilplan_mcp.tools.feasibility_analyzer import analyze_feasibility
from civilplan_mcp.tools.land_info_query import (
    build_land_use_bbox_params,
    extract_address_result,
    extract_feature_properties,
    query_land_info,
)
from civilplan_mcp.tools.project_parser import parse_project
from civilplan_mcp.tools.quantity_estimator import estimate_quantities


def test_query_land_info_returns_graceful_message_without_api_keys() -> None:
    result = query_land_info(address="경기도 양주시 덕계동 123", pnu=None)

    assert result["status"] == "disabled"


def test_settings_keep_public_data_key_for_nara_usage() -> None:
    settings = Settings(data_go_kr_api_key="abc")

    assert settings.data_go_kr_api_key == "abc"


def test_extract_address_result_reads_vworld_shape() -> None:
    payload = {
        "response": {
            "status": "OK",
            "result": {
                "point": {"x": "127.061", "y": "37.821"},
                "items": [
                    {
                        "id": "4163010100101230000",
                        "address": {"parcel": "경기도 양주시 덕계동 123"}
                    }
                ],
            },
        }
    }

    parsed = extract_address_result(payload)
    assert parsed["pnu"] == "4163010100101230000"
    assert parsed["x"] == 127.061


def test_extract_feature_properties_returns_first_feature() -> None:
    payload = {
        "response": {
            "status": "OK",
            "result": {
                "featureCollection": {
                    "features": [
                        {"properties": {"pnu": "4163010100101230000", "jimok": "대"}}
                    ]
                }
            },
        }
    }

    parsed = extract_feature_properties(payload)
    assert parsed["jimok"] == "대"


def test_build_land_use_bbox_params_uses_wfs_bbox_pattern() -> None:
    params = build_land_use_bbox_params(127.0, 37.0, "test-key")

    assert params["SERVICE"] == "WFS"
    assert params["REQUEST"] == "GetFeature"
    assert params["TYPENAME"] == "lt_c_lhblpn"
    assert params["SRSNAME"] == "EPSG:4326"
    assert params["KEY"] == "test-key"
    assert params["OUTPUTFORMAT"] == "application/json"
    assert params["BBOX"] == "126.9995,36.9995,127.0005,37.0005,EPSG:4326"


def test_analyze_feasibility_returns_positive_cost_structure() -> None:
    result = analyze_feasibility(
        land_area_m2=600,
        land_price_per_m2=850000,
        land_price_multiplier=1.0,
        construction_cost_total=890000000,
        other_costs_million=50,
        revenue_type="임대",
        building_floor_area_m2=720,
        sale_price_per_m2=None,
        monthly_rent_per_m2=16000,
        vacancy_rate_pct=10.0,
        operating_expense_pct=20.0,
        equity_ratio_pct=30.0,
        loan_rate_pct=5.5,
        loan_term_years=10,
        construction_months=24,
        sale_months=12,
    )

    assert result["cost_structure"]["total_investment"] > 0
    assert "irr_pct" in result["returns"]


def test_validate_against_benchmark_includes_bid_warning() -> None:
    result = validate_against_benchmark(
        project_type="소로_도로",
        road_length_m=890,
        floor_area_m2=None,
        region="경기도",
        our_estimate_won=1067000000,
    )

    assert "낙찰가 ≠ 사업비" in result["bid_rate_reference"]["경고"]


def test_generate_budget_report_creates_docx(tmp_path: Path) -> None:
    project_data = parse_project(description="복지관 신축 2026~2028 경기도")
    project_data["output_dir"] = str(tmp_path)
    result = generate_budget_report(
        report_type="예산편성요구서",
        project_data=project_data,
        boq_summary={"total_cost": 1067000000, "direct_cost": 900422000, "indirect_cost": 166578000},
        department="도로과",
        requester="22B Labs",
        output_filename="budget.docx",
    )

    assert Path(result["file_path"]).exists()


def test_generate_dxf_drawing_creates_dxf(tmp_path: Path) -> None:
    project_spec = parse_project(description="소로 신설 L=890m B=6m 경기도")
    project_spec["output_dir"] = str(tmp_path)
    quantities = estimate_quantities(
        road_class="소로",
        length_m=890,
        width_m=6.0,
        terrain="평지",
        pavement_type="아스콘",
        include_water_supply=False,
        include_sewage=False,
        include_retaining_wall=False,
        include_bridge=False,
        bridge_length_m=0.0,
    )

    result = generate_dxf_drawing(
        drawing_type="횡단면도",
        project_spec=project_spec,
        quantities=quantities,
        scale="1:200",
        output_filename="road.dxf",
    )

    doc = ezdxf.readfile(result["file_path"])
    assert doc is not None
