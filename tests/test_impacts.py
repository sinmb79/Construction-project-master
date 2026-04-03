from civilplan_mcp.tools.impact_evaluator import evaluate_impact_assessments


def test_evaluate_impact_assessments_flags_borderline_disaster_review() -> None:
    result = evaluate_impact_assessments(
        domain="토목_도로",
        project_type="도로",
        road_length_m=890,
        development_area_m2=5340,
        total_cost_billion=10.67,
        building_floor_area_m2=None,
        housing_units=None,
        is_urban_area=True,
        near_cultural_heritage=False,
        near_river=False,
        near_protected_area=False,
    )

    target = next(item for item in result["evaluations"] if item["name"] == "재해영향평가")
    assert target["result"] == "BORDERLINE"
