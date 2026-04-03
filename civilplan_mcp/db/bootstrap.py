from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from civilplan_mcp.config import BASE_DIR, get_settings


SCHEMA_PATH = BASE_DIR / "civilplan_mcp" / "db" / "schema.sql"


def load_json_data(filename: str) -> Any:
    path = get_settings().data_dir / filename
    return json.loads(path.read_text(encoding="utf-8"))


def bootstrap_database(db_path: Path | None = None) -> Path:
    target = db_path or get_settings().db_path
    target.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(target) as connection:
        connection.executescript(schema)

        region_factors = load_json_data("region_factors.json")
        connection.executemany(
            "INSERT OR REPLACE INTO region_factors(region, factor, note) VALUES(?, ?, ?)",
            [(region, values["factor"], values["note"]) for region, values in region_factors.items()],
        )

        unit_prices = load_json_data("unit_prices_2026.json")["items"]
        connection.executemany(
            """
            INSERT INTO unit_prices(category, item, spec, unit, base_price, source, year)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item["category"],
                    item["item"],
                    item.get("spec"),
                    item["unit"],
                    item["base_price"],
                    item["source"],
                    item.get("year", 2026),
                )
                for item in unit_prices
            ],
        )

        legal_procedures = load_json_data("legal_procedures.json")["procedures"]
        connection.executemany(
            """
            INSERT OR REPLACE INTO legal_procedures(
                id, category, name, law, threshold, authority, duration_min_months,
                duration_max_months, mandatory, note, reference_url, domain
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item["id"],
                    item["category"],
                    item["name"],
                    item["law"],
                    item["threshold"],
                    item["authority"],
                    item["duration_min_months"],
                    item["duration_max_months"],
                    1 if item["mandatory"] else 0,
                    item["note"],
                    item["reference_url"],
                    item.get("domain", "복합"),
                )
                for item in legal_procedures
            ],
        )

    return target
