from __future__ import annotations

from typing import Any


DOMAIN_PROMPTS: dict[str, str] = {
    "road": (
        "Focus on the road alignment, lane markings, shoulders, drainage channels, utility corridors, "
        "guard rails, and the surrounding Korean rural or suburban context."
    ),
    "building": (
        "Focus on the building massing, facade materials, rooftop equipment, parking, pedestrian circulation, "
        "and the surrounding Korean urban block."
    ),
    "water": (
        "Focus on pipeline routing, manholes, pump stations, treatment structures, trench alignment, "
        "and road-side utility coordination."
    ),
    "river": (
        "Focus on embankments, flood-control structures, riprap, levee walks, bridge crossings, "
        "and natural riparian vegetation."
    ),
    "landscape": (
        "Focus on planting composition, trails, plazas, seating, play areas, water features, "
        "and seasonal Korean vegetation."
    ),
    "mixed": (
        "Show a comprehensive development site where roads, buildings, utility systems, and landscape work together "
        "as one coordinated Korean construction project."
    ),
}

VIEW_INSTRUCTIONS: dict[str, str] = {
    "birdseye": (
        "Create a photorealistic bird's-eye view rendering with an aerial camera angle around 45 to 60 degrees, "
        "covering the full project extent and nearby context."
    ),
    "perspective": (
        "Create a photorealistic perspective rendering from a representative human-scale viewpoint, "
        "showing how the project feels on the ground."
    ),
}


def build_prompt(
    *,
    view_type: str,
    project_type: str,
    project_summary: str,
    details: dict[str, Any],
) -> str:
    view_instruction = VIEW_INSTRUCTIONS.get(view_type, VIEW_INSTRUCTIONS["birdseye"])
    domain_instruction = DOMAIN_PROMPTS.get(project_type, DOMAIN_PROMPTS["mixed"])
    detail_lines = [f"- {key}: {value}" for key, value in details.items() if value not in (None, "", [], {})]
    detail_block = "\n".join(detail_lines) if detail_lines else "- No additional technical details provided."

    return (
        f"{view_instruction}\n\n"
        f"Project summary:\n{project_summary}\n\n"
        f"Technical details:\n{detail_block}\n\n"
        f"Domain guidance:\n{domain_instruction}\n\n"
        "Style requirements:\n"
        "- Professional architectural visualization for a Korean civil or building project.\n"
        "- Clear daytime weather, realistic materials, and readable spatial hierarchy.\n"
        "- Include surrounding terrain, access roads, and scale cues where appropriate.\n"
        "- Avoid people-heavy staging, exaggerated concept-art effects, or fantasy aesthetics."
    )
