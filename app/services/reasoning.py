from __future__ import annotations

import json
from pathlib import Path

from app.config import BASE_DIR

_SKILL_GRAPH_PATH: Path = BASE_DIR / "data" / "skill_graph.json"


def _load_skill_graph() -> dict[str, list[str]]:
    try:
        with _SKILL_GRAPH_PATH.open("r", encoding="utf-8") as file:
            raw_graph = json.load(file)
    except Exception:
        return {}

    if not isinstance(raw_graph, dict):
        return {}

    graph: dict[str, list[str]] = {}
    for skill, prerequisites in raw_graph.items():
        if not isinstance(skill, str) or not isinstance(prerequisites, list):
            continue

        graph[skill.strip()] = [
            item.strip()
            for item in prerequisites
            if isinstance(item, str) and item.strip()
        ]

    return graph


_SKILL_GRAPH: dict[str, list[str]] = _load_skill_graph()


def _is_prerequisite(prerequisite: str, target_skill: str, visiting: set[str] | None = None) -> bool:
    if visiting is None:
        visiting = set()

    if target_skill in visiting:
        return False

    visiting.add(target_skill)

    direct_requirements = _SKILL_GRAPH.get(target_skill, [])
    if prerequisite in direct_requirements:
        return True

    for dependency in direct_requirements:
        if _is_prerequisite(prerequisite, dependency, visiting):
            return True

    return False


def generate_reason(skill: str, jd_skills: list[str], resume_skills: list[str]) -> str:
    normalized_skill = skill.strip()
    jd_set = {item.strip() for item in jd_skills if item and item.strip()}
    resume_set = {item.strip() for item in resume_skills if item and item.strip()}

    if normalized_skill in jd_set and normalized_skill not in resume_set:
        return "Required in job description but missing in resume"

    missing_skills = sorted(jd_set - resume_set)
    for missing_skill in missing_skills:
        if missing_skill == normalized_skill:
            continue

        if _is_prerequisite(normalized_skill, missing_skill):
            return f"Needed as a prerequisite for learning {missing_skill}"

    return "Included in learning path"
