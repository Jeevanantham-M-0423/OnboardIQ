from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

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

        cleaned_prerequisites = [
            str(item).strip() for item in prerequisites if isinstance(item, str) and item.strip()
        ]
        graph[skill.strip()] = cleaned_prerequisites

    return graph


_SKILL_GRAPH: dict[str, list[str]] = _load_skill_graph()

_UNVISITED = 0
_VISITING = 1
_VISITED = 2


def generate_learning_path(
    missing_skills: Iterable[str],
    known_skills: Iterable[str],
) -> dict[str, list[str]]:
    known_set = {skill.strip() for skill in known_skills if skill and skill.strip()}
    missing_ordered = [skill.strip() for skill in missing_skills if skill and skill.strip()]

    added: set[str] = set()
    state: dict[str, int] = {}
    ordered_path: list[str] = []

    def dfs(skill: str) -> None:
        if skill in known_set or skill in added:
            return

        current_state = state.get(skill, _UNVISITED)

        if current_state == _VISITING:
            # Break potential cycles safely without crashing.
            return

        if current_state == _VISITED:
            return

        state[skill] = _VISITING

        for prerequisite in _SKILL_GRAPH.get(skill, []):
            dfs(prerequisite)

        state[skill] = _VISITED

        if skill not in known_set and skill not in added:
            added.add(skill)
            ordered_path.append(skill)

    for target_skill in missing_ordered:
        dfs(target_skill)

    return {"learning_path": ordered_path}
