CREATE TABLE IF NOT EXISTS unit_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    item TEXT NOT NULL,
    spec TEXT,
    unit TEXT NOT NULL,
    base_price INTEGER NOT NULL,
    source TEXT,
    year INTEGER DEFAULT 2026
);

CREATE TABLE IF NOT EXISTS region_factors (
    region TEXT PRIMARY KEY,
    factor REAL NOT NULL,
    note TEXT
);

CREATE TABLE IF NOT EXISTS legal_procedures (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    law TEXT,
    threshold TEXT,
    authority TEXT,
    duration_min_months INTEGER,
    duration_max_months INTEGER,
    mandatory INTEGER DEFAULT 0,
    note TEXT,
    reference_url TEXT,
    domain TEXT DEFAULT '복합'
);

CREATE TABLE IF NOT EXISTS project_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    description TEXT,
    parsed_spec TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
