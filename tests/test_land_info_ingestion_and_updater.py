from __future__ import annotations

from io import BytesIO
from pathlib import Path
import zipfile

from civilplan_mcp.config import Settings
from civilplan_mcp.tools.land_info_query import (
    _read_land_price_from_files,
    extract_land_use_html_properties,
)
from civilplan_mcp.updater import wage_updater


def test_extract_land_use_html_properties_reads_regulation_table() -> None:
    html = """
    <div class="tbl04 mb">
      <table>
        <tbody>
          <tr>
            <td>제2종일반주거지역</td>
            <td>60%</td>
            <td>200%</td>
          </tr>
          <tr class="center"><td colspan="3" class="center bg">건폐율</td></tr>
          <tr><td colspan="3" class="left" id="PopupG_pop"><p>최대 건폐율 60%</p></td></tr>
          <tr class="center"><td colspan="3" class="center bg">용적률</td></tr>
          <tr><td colspan="3" class="left" id="PopupY_pop"><p>최대 용적률 200%</p></td></tr>
        </tbody>
      </table>
    </div>
    """

    parsed = extract_land_use_html_properties(html)

    assert parsed["usedistrictnm"] == "제2종일반주거지역"
    assert parsed["bcr"] == "60"
    assert parsed["far"] == "200"


def test_read_land_price_from_zip_file(tmp_path: Path, monkeypatch) -> None:
    land_price_dir = tmp_path / "land_prices"
    land_price_dir.mkdir()
    archive_path = land_price_dir / "seoul_land_prices.zip"

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "prices.csv",
            "PNU,LANDPRICE\n1111010100100010000,1250000\n",
        )
    archive_path.write_bytes(buffer.getvalue())

    settings = Settings(data_dir=tmp_path)
    monkeypatch.setattr("civilplan_mcp.tools.land_info_query.get_settings", lambda: settings)

    price = _read_land_price_from_files("1111010100100010000")

    assert price == {"individual_m2_won": 1250000, "source": "seoul_land_prices.zip:prices.csv"}


def test_update_wage_rates_creates_flag_and_log_on_parse_failure(tmp_path: Path, monkeypatch) -> None:
    settings = Settings(data_dir=tmp_path)

    monkeypatch.setattr(wage_updater, "get_settings", lambda: settings)
    monkeypatch.setattr(
        wage_updater,
        "fetch_source_text",
        lambda url: "<html><body>No structured wage table here</body></html>",
    )

    result = wage_updater.update_wage_rates(period="상반기")

    assert result["status"] == "pending_manual_review"
    assert (tmp_path / ".update_required_wage").exists()
    assert (tmp_path / "update_log.json").exists()
