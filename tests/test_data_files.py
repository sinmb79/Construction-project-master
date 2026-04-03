from pathlib import Path

from civilplan_mcp.config import get_settings
from civilplan_mcp.db.bootstrap import bootstrap_database, load_json_data


def test_required_seed_files_exist() -> None:
    data_dir = get_settings().data_dir
    required = [
        "unit_prices_2026.json",
        "legal_procedures.json",
        "region_factors.json",
        "road_standards.json",
        "guidelines_catalog.json",
        "association_prices_catalog.json",
        "waste_disposal_prices_2025.json",
        "indirect_cost_rates.json",
        "supervision_rates.json",
        "rental_benchmark.json",
        "price_update_calendar.json",
        "data_validity_warnings.json",
    ]

    for name in required:
        assert (data_dir / name).exists(), name


def test_load_json_data_reads_seed_file() -> None:
    data = load_json_data("region_factors.json")

    assert "경기도" in data


def test_bootstrap_database_creates_sqlite_file(tmp_path: Path) -> None:
    db_path = tmp_path / "civilplan.db"

    bootstrap_database(db_path)

    assert db_path.exists()
