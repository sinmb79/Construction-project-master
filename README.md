# CivilPlan MCP

LICENSE: MIT

PHILOSOPHY: Hongik Ingan (홍익인간) - reduce inequality in access to expert planning knowledge.
This project is free to use, modify, and distribute.

CivilPlan is a FastMCP server for Korean civil, infrastructure, and building project planning workflows.

## Scope

- FastMCP Streamable HTTP server on `http://127.0.0.1:8765/mcp`
- 19 planning tools across v1.0 and v1.1
- Local JSON and SQLite bootstrap data
- Excel, DOCX, SVG, and DXF output generators
- Scheduled update scaffolding for wage, waste, and standard cost references

## Tool Catalog

### v1.0

1. `civilplan_parse_project`
2. `civilplan_get_legal_procedures`
3. `civilplan_get_phase_checklist`
4. `civilplan_evaluate_impact_assessments`
5. `civilplan_estimate_quantities`
6. `civilplan_get_unit_prices`
7. `civilplan_generate_boq_excel`
8. `civilplan_generate_investment_doc`
9. `civilplan_generate_schedule`
10. `civilplan_generate_svg_drawing`
11. `civilplan_get_applicable_guidelines`
12. `civilplan_fetch_guideline_summary`
13. `civilplan_select_bid_type`
14. `civilplan_estimate_waste_disposal`

### v1.1

15. `civilplan_query_land_info`
16. `civilplan_analyze_feasibility`
17. `civilplan_validate_against_benchmark`
18. `civilplan_generate_budget_report`
19. `civilplan_generate_dxf_drawing`

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python server.py
```

The server starts on `127.0.0.1:8765` and exposes the MCP endpoint at `/mcp`.

## API Key Setup

CivilPlan supports two local-only key flows:

### Option A: `.env`

1. Copy `.env.example` to `.env`
2. Fill in your own keys
3. Start the server

`.env` is ignored by git and loaded automatically at startup.

### Option B: encrypted local storage

```bash
python setup_keys.py
```

Or import an existing `.env` file into encrypted storage:

```bash
python setup_keys.py --from-env-file .env
```

On Windows, this stores the keys with DPAPI under your local user profile so the same machine and user account are required to decrypt them.

## Environment Variables

```env
DATA_GO_KR_API_KEY=
VWORLD_API_KEY=
```

- `DATA_GO_KR_API_KEY`: public data portal API key used for benchmark probing and future official integrations
- `VWORLD_API_KEY`: VWorld API key used for address-to-PNU lookup and cadastral queries

Live keys are intentionally not committed to the public repository.

## Client Connection

### Claude Desktop

```json
{
  "mcpServers": {
    "civilplan": {
      "command": "mcp-remote",
      "args": ["http://127.0.0.1:8765/mcp"]
    }
  }
}
```

### ChatGPT Developer Mode

ChatGPT cannot connect to `localhost` directly.
Expose the server with `ngrok http 8765` or Cloudflare Tunnel, then use the generated HTTPS URL in ChatGPT Settings -> Connectors -> Create.

## Project Domains

Every tool expects a `domain` parameter.

- `건축`
- `토목_도로`
- `토목_상하수도`
- `토목_하천`
- `조경`
- `복합`

Landscape-specific legal and procedure data is not fully implemented yet.
The server returns a readiness message instead of pretending the data is complete.

## Data Notes

- `civilplan_mcp/data/land_prices/` is intentionally empty in git.
- Put downloaded land-price CSV, TSV, or ZIP bundles there for local parcel-price lookup.
- The loader supports UTF-8, CP949, and EUC-KR encoded tabular files.

## Update Automation

The updater package includes scheduled jobs for:

- January 2, 09:00: wage H1 + waste + indirect rates H1
- July 10, 09:00: standard market price H2 + indirect rates H2
- September 2, 09:00: wage H2

If parsing fails, the server creates `.update_required_*` flag files and emits startup warnings.

## Known Limitations

- Official land-use planning data still depends on unstable external services. The server tries official and HTML fallback paths, but some parcels may still return partial zoning details.
- Land-price lookup requires manually downloaded source files under `civilplan_mcp/data/land_prices/`.
- Nara benchmark validation currently probes API availability and falls back to local heuristics when the public endpoint is unavailable.
- Updater fetchers are conservative and may request manual review when source pages change.
- Public repository builds do not include live API credentials. Users should set their own keys through `.env` or `setup_keys.py`.

## Verification

Current local verification command:

```bash
pytest tests -q
```
