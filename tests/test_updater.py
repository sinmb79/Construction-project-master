from pathlib import Path

from civilplan_mcp.updater.scheduler import build_scheduler
from civilplan_mcp.updater.wage_updater import check_update_flags, flag_manual_update_required


def test_build_scheduler_registers_expected_jobs() -> None:
    scheduler = build_scheduler(start=False)

    assert {job.id for job in scheduler.get_jobs()} == {
        "wage_h1",
        "waste_annual",
        "standard_h1",
        "standard_h2",
        "wage_h2",
    }


def test_flag_manual_update_required_creates_flag(tmp_path: Path) -> None:
    flag_manual_update_required("wage", "manual review needed", data_dir=tmp_path)

    warnings = check_update_flags(data_dir=tmp_path)
    assert warnings
