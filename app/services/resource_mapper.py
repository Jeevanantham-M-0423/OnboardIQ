from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from app.config import BASE_DIR

_RESOURCES_PATH: Path = BASE_DIR / "data" / "resources.json"


def _load_resources() -> dict[str, dict[str, str]]:
    try:
        with _RESOURCES_PATH.open("r", encoding="utf-8") as file:
            raw = json.load(file)
    except Exception:
        return {}

    if not isinstance(raw, dict):
        return {}

    normalized: dict[str, dict[str, str]] = {}

    for skill, resources in raw.items():
        if not isinstance(skill, str) or not isinstance(resources, dict):
            continue

        resource_map: dict[str, str] = {}
        for key, value in resources.items():
            if isinstance(key, str) and isinstance(value, str):
                resource_map[key.strip()] = value.strip()

        normalized[skill.strip()] = resource_map

    return normalized


_RESOURCES: dict[str, dict[str, str]] = _load_resources()


def map_resources(learning_path: Iterable[str]) -> list[dict[str, object]]:
    mapped: list[dict[str, object]] = []

    for skill in learning_path:
        normalized_skill = skill.strip() if isinstance(skill, str) else ""
        if not normalized_skill:
            continue

        mapped.append(
            {
                "skill": normalized_skill,
                "resources": dict(_RESOURCES.get(normalized_skill, {})),
            }
        )

    return mapped
