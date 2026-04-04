import asyncio

from civilplan_mcp.server import build_mcp, build_server_config


def test_build_server_config_defaults() -> None:
    config = build_server_config()

    assert config["host"] == "127.0.0.1"
    assert config["port"] == 8765
    assert config["path"] == "/mcp"


def test_server_registers_all_20_tools() -> None:
    app = build_mcp()
    tools = asyncio.run(app.list_tools())
    names = {tool.name for tool in tools}

    assert len(names) == 20
    assert "civilplan_parse_project" in names
    assert "civilplan_generate_dxf_drawing" in names
    assert "civilplan_generate_birdseye_view" in names


def test_read_tools_have_read_only_hint() -> None:
    app = build_mcp()
    tools = {tool.name: tool for tool in asyncio.run(app.list_tools())}

    assert tools["civilplan_parse_project"].annotations.readOnlyHint is True
    assert tools["civilplan_generate_boq_excel"].annotations.readOnlyHint is None
