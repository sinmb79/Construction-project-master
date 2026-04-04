# CivilPlan MCP v2 - Bird's-Eye View Generation Design Spec

## Overview

Add a new MCP tool `generate_birdseye_view` to CivilPlan MCP that generates 3D architectural/civil engineering bird's-eye view and perspective renderings using Google's Nano Banana Pro (Gemini 3 Pro Image) API. Additionally, remove all local LLM dependencies and create a polished release with comprehensive documentation.

## Scope

### In Scope
1. **New MCP tool**: `generate_birdseye_view` — generates 2 images (bird's-eye + perspective)
2. **Nano Banana Pro integration** via `google-genai` Python SDK
3. **Project-type-specific prompt templates** (road, building, water/sewerage, river, landscaping)
4. **Local LLM removal** — delete all local LLM code and dependencies
5. **Release v2.0.0** — GitHub release with detailed README and connection guides

### Out of Scope
- Night/day or seasonal variations
- Video/animation generation
- 3D model file export (OBJ, FBX, etc.)

## Architecture

### Data Flow

```
MCP Client (Claude / ChatGPT)
        |
        | MCP Protocol (HTTP)
        v
CivilPlan MCP Server (FastMCP)
        |
        | generate_birdseye_view tool called
        v
BirdseyeViewGenerator
        |
        |-- [If SVG drawing exists] Convert SVG to PNG reference image
        |-- [Always] Build optimized prompt from project data
        |
        v
Google Gemini API (Nano Banana Pro model)
        |
        v
2x PNG images returned (bird's-eye + perspective)
        |
        |-- Save to output directory
        |-- Return base64 + file paths via MCP response
```

### New Files

| File | Purpose |
|------|---------|
| `civilplan_mcp/tools/birdseye_generator.py` | MCP tool implementation |
| `civilplan_mcp/prompts/birdseye_templates.py` | Project-type prompt templates |
| `civilplan_mcp/services/gemini_image.py` | Nano Banana Pro API client wrapper |
| `tests/test_birdseye_generator.py` | Unit tests |

### Tool Interface

```python
@mcp.tool()
async def generate_birdseye_view(
    project_summary: str,       # Parsed project description (from project_parser)
    project_type: str,          # "road" | "building" | "water" | "river" | "landscape" | "mixed"
    svg_drawing: str | None,    # Optional SVG drawing content from drawing_generator
    resolution: str = "2k",     # "2k" | "4k"
    output_dir: str = "./output/renders"
) -> dict:
    """
    Returns:
    {
        "birdseye_view": {"path": str, "base64": str},
        "perspective_view": {"path": str, "base64": str},
        "prompt_used": str,
        "model": "nano-banana-pro"
    }
    """
```

### Prompt Template Strategy

Each project type gets a specialized prompt template:

- **Road**: Emphasize road alignment, terrain, surrounding land use, utility corridors
- **Building**: Emphasize building mass, facade, site context, parking/landscaping
- **Water/Sewerage**: Emphasize pipeline routes, treatment facilities, connection points
- **River**: Emphasize riverbank, embankments, bridges, flood plains
- **Landscape**: Emphasize vegetation, pathways, public spaces, terrain grading
- **Mixed**: Combine relevant elements from applicable types

Template format:
```
"Create a photorealistic {view_type} of a {project_type} project:
{project_details}
Style: Professional architectural visualization, Korean construction context,
clear weather, daytime, {resolution} resolution"
```

### API Configuration

- API key stored via existing `.env` / `secure_store.py` pattern
- New env var: `GEMINI_API_KEY`
- SDK: `google-genai` (official Google Gen AI Python SDK)
- Model: `gemini-3-pro-image` (Nano Banana Pro)
- Error handling: On API failure, return error message without crashing the MCP tool

### SVG-to-PNG Conversion

When an SVG drawing is provided as reference:
1. Convert SVG to PNG using `cairosvg` or `Pillow`
2. Send as reference image alongside the text prompt
3. Nano Banana Pro uses it for spatial understanding

### Local LLM Removal

Identify and remove:
- Any local model loading code (transformers, llama-cpp, ollama, etc.)
- Related dependencies in `requirements.txt` / `pyproject.toml`
- Config entries referencing local models
- Replace with Gemini API calls where needed

## Release Plan

### Version: v2.0.0

### README Overhaul
- Project overview with feature highlights
- Quick start guide (clone, install, configure, run)
- Tool reference table (all 20 tools including new birdseye)
- Claude Desktop connection guide (step-by-step with screenshots description)
- ChatGPT / OpenAI connection guide
- API key setup guide (Gemini, public data portal)
- Example outputs (birdseye rendering description)
- Troubleshooting FAQ

### GitHub Release
- Tag: `v2.0.0`
- Release notes summarizing changes
- Installation instructions

## Testing Strategy

- Unit test for prompt template generation
- Unit test for SVG-to-PNG conversion
- Integration test with mocked Gemini API response
- Manual end-to-end test with real API key

## Dependencies Added

| Package | Purpose |
|---------|---------|
| `google-genai` | Gemini API SDK (Nano Banana Pro) |
| `cairosvg` | SVG to PNG conversion |
| `Pillow` | Image processing |

## Dependencies Removed

All local LLM packages (to be identified during implementation by scanning current requirements).
