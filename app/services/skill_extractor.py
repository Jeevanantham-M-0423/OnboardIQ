from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from typing import List

from app.config import BASE_DIR

_SKILLS_DATA_PATH: Path = BASE_DIR / "data" / "skills.json"
_SYNONYMS_DATA_PATH: Path = BASE_DIR / "data" / "synonyms.json"

_KEYWORD_ALIASES: dict[str, list[str]] = {
    "rest api": ["rest apis", "restful api", "restful apis"],
    "ci/cd": ["cicd", "continuous integration", "continuous deployment"],
    "node.js": ["nodejs", "node js"],
    "next.js": ["nextjs", "next js"],
    "vue.js": ["vuejs", "vue js"],
    "nuxt.js": ["nuxtjs", "nuxt js"],
    "express.js": ["expressjs", "express js"],
    "asp.net": ["asp net"],
    "oauth 2.0": ["oauth2", "oauth2.0"],
    "a/b testing": ["ab testing"],
}


def _normalize_text(value: str) -> str:
    lowered = value.lower()
    collapsed = re.sub(r"[^a-z0-9#+./]+", " ", lowered)
    return re.sub(r"\s+", " ", collapsed).strip()


def _compile_phrase_pattern(phrase: str) -> re.Pattern[str]:
    escaped = re.escape(phrase.strip())
    escaped = escaped.replace(r"\ ", r"\s+")
    return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)


def _normalize_skill_name(name: str) -> str:
    aliases = {
        "aws": "AWS",
        "gcp": "GCP",
        "sql": "SQL",
        "ci/cd": "CI/CD",
        "rest api": "REST API",
        "node.js": "Node.js",
        "mongodb": "MongoDB",
        "tailwind css": "Tailwind CSS",
        "power bi": "Power BI",
    }

    key = name.strip().lower()
    if key in aliases:
        return aliases[key]

    return name.strip()


def _build_keywords(skill_name: str) -> list[str]:
    base = skill_name.strip()
    if not base:
        return []

    keywords = [base]
    keywords.extend(_KEYWORD_ALIASES.get(base.lower(), []))
    return keywords


def _load_synonyms() -> dict[str, list[str]]:
    try:
        with _SYNONYMS_DATA_PATH.open("r", encoding="utf-8") as file:
            entries: Any = json.load(file)
    except Exception:
        return {}

    if not isinstance(entries, dict):
        return {}

    normalized: dict[str, list[str]] = {}

    for canonical, variants in entries.items():
        if not isinstance(canonical, str) or not isinstance(variants, list):
            continue

        canonical_key = _normalize_text(canonical)
        if not canonical_key:
            continue

        normalized_variants = [
            _normalize_text(value)
            for value in variants
            if isinstance(value, str) and _normalize_text(value)
        ]

        if normalized_variants:
            normalized[canonical_key] = normalized_variants

    return normalized


def _build_synonym_rules() -> list[tuple[re.Pattern[str], str]]:
    rules: list[tuple[re.Pattern[str], str]] = []

    for canonical, variants in _SYNONYMS.items():
        unique_variants = sorted(set(variants), key=len, reverse=True)
        for variant in unique_variants:
            if variant == canonical:
                continue
            rules.append((_compile_phrase_pattern(variant), canonical))

    return rules


def _apply_synonym_mapping(normalized_text: str) -> str:
    mapped = normalized_text

    for pattern, replacement in _SYNONYM_RULES:
        mapped = pattern.sub(replacement, mapped)

    return re.sub(r"\s+", " ", mapped).strip()


def _load_skill_entries() -> list[dict[str, object]]:
    with _SKILLS_DATA_PATH.open("r", encoding="utf-8") as file:
        entries = json.load(file)

    if not isinstance(entries, list):
        return []

    normalized_entries: list[dict[str, object]] = []
    seen_names: set[str] = set()

    for entry in entries:
        if not isinstance(entry, str):
            continue

        canonical_name = _normalize_skill_name(entry)
        if not canonical_name:
            continue

        lowered_name = canonical_name.lower()
        if lowered_name in seen_names:
            continue
        seen_names.add(lowered_name)

        keywords = _build_keywords(canonical_name)
        if not keywords:
            continue

        normalized_keywords = [
            _normalize_text(keyword) for keyword in keywords if _normalize_text(keyword)
        ]

        if not normalized_keywords:
            continue

        normalized_entries.append(
            {
                "name": canonical_name,
                "normalized_name": _normalize_text(canonical_name),
                "normalized_keywords": normalized_keywords,
            }
        )

    return normalized_entries


_SKILL_ENTRIES: list[dict[str, object]] = _load_skill_entries()
_SYNONYMS: dict[str, list[str]] = _load_synonyms()
_SYNONYM_RULES: list[tuple[re.Pattern[str], str]] = _build_synonym_rules()


def _contains_normalized_keyword(normalized_text: str, keyword: str) -> bool:
    return f" {keyword} " in f" {normalized_text} "


def _matches_keyword(
    normalized_text: str,
    text_tokens: set[str],
    keyword: str,
) -> bool:
    if not keyword:
        return False

    keyword_tokens = keyword.split()
    if not keyword_tokens:
        return False

    # Full-word only match for single-token skills/keywords.
    if len(keyword_tokens) == 1:
        return keyword_tokens[0] in text_tokens

    # Prefer strict phrase match first.
    if _contains_normalized_keyword(normalized_text, keyword):
        return True

    # Controlled partial match: all normalized tokens must exist as full words.
    return all(token in text_tokens for token in keyword_tokens)


def extract_skills(text: str) -> List[str]:
    if not text:
        return []

    normalized_text = _apply_synonym_mapping(_normalize_text(text))
    text_tokens = set(normalized_text.split())

    found: list[str] = []
    seen: set[str] = set()

    for entry in _SKILL_ENTRIES:
        name = str(entry["name"])
        normalized_name = entry["normalized_name"]
        normalized_keywords = entry["normalized_keywords"]

        if not isinstance(normalized_name, str) or not isinstance(normalized_keywords, list):
            continue

        matched_by_name = _matches_keyword(normalized_text, text_tokens, normalized_name)
        matched_by_keywords = any(
            isinstance(keyword, str)
            and keyword
            and _matches_keyword(normalized_text, text_tokens, keyword)
            for keyword in normalized_keywords
        )

        matched = matched_by_name or matched_by_keywords

        if matched and name not in seen:
            found.append(name)
            seen.add(name)

    return found
