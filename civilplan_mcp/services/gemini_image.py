from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PIL import Image as PILImage

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:  # pragma: no cover - exercised in tests via runtime guard
    genai = None
    genai_types = None


logger = logging.getLogger(__name__)


class GeminiImageService:
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gemini-3-pro-image-preview",
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._client = client or self._build_client()

    def _build_client(self) -> Any:
        if genai is None:
            raise RuntimeError("google-genai is not installed. Install it to use GeminiImageService.")
        return genai.Client(api_key=self.api_key)

    def _build_config(self, *, aspect_ratio: str, image_size: str) -> Any:
        if genai_types is None:
            return {
                "response_modalities": ["TEXT", "IMAGE"],
                "image_config": {
                    "aspect_ratio": aspect_ratio,
                    "image_size": image_size,
                },
            }

        image_config_factory = getattr(genai_types, "ImageConfig", None)
        generate_config_factory = getattr(genai_types, "GenerateContentConfig", None)
        image_config = (
            image_config_factory(aspect_ratio=aspect_ratio, image_size=image_size)
            if callable(image_config_factory)
            else {
                "aspect_ratio": aspect_ratio,
                "image_size": image_size,
            }
        )

        if callable(generate_config_factory):
            return generate_config_factory(
                response_modalities=["TEXT", "IMAGE"],
                image_config=image_config,
            )

        return {
            "response_modalities": ["TEXT", "IMAGE"],
            "image_config": image_config,
        }

    @staticmethod
    def _extract_parts(response: Any) -> list[Any]:
        direct_parts = getattr(response, "parts", None)
        if direct_parts:
            return list(direct_parts)

        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            candidate_parts = getattr(getattr(candidate, "content", None), "parts", None)
            if candidate_parts:
                return list(candidate_parts)
        return []

    def generate_image(
        self,
        *,
        prompt: str,
        output_path: str,
        reference_image_path: str | None = None,
        aspect_ratio: str = "16:9",
        image_size: str = "2K",
    ) -> dict[str, str]:
        reference_image: PILImage.Image | None = None

        try:
            contents: list[Any] = [prompt]
            if reference_image_path:
                reference_image = PILImage.open(reference_image_path)
                contents.append(reference_image)

            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=self._build_config(aspect_ratio=aspect_ratio, image_size=image_size),
            )

            for part in self._extract_parts(response):
                if getattr(part, "inline_data", None) is not None and hasattr(part, "as_image"):
                    output = Path(output_path)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    part.as_image().save(str(output))
                    return {"status": "success", "path": str(output)}

            text_parts = [str(part.text).strip() for part in self._extract_parts(response) if getattr(part, "text", None)]
            message = "No image in API response."
            if text_parts:
                message = f"{message} {' '.join(text_parts)}"
            return {"status": "error", "error": message}
        except Exception as exc:
            logger.exception("Gemini image generation failed.")
            return {"status": "error", "error": str(exc)}
        finally:
            if reference_image is not None:
                reference_image.close()
