from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
import logging
import re
from pathlib import Path
from typing import Any, Iterable

from app.config import BASE_DIR

logger = logging.getLogger("onboardiq.enricher")

_DATA_DIR = BASE_DIR / "data"
_EXTERNAL_DIR = _DATA_DIR / "external"
_SKILLS_PATH = _DATA_DIR / "skills.json"
_SYNONYMS_PATH = _DATA_DIR / "synonyms.json"
_GRAPH_PATH = _DATA_DIR / "skill_graph.json"
_CATEGORIES_PATH = _DATA_DIR / "skill_categories.json"

_CANONICAL_OVERRIDES = {
    "aws": "AWS",
    "gcp": "GCP",
    "sql": "SQL",
    "nlp": "NLP",
    "mlops": "MLOps",
    "devops": "DevOps",
    "devsecops": "DevSecOps",
    "ci/cd": "CI/CD",
    "api": "API",
    "rest api": "REST API",
    "rest apis": "REST API",
    "node.js": "Node.js",
    "next.js": "Next.js",
    "vue.js": "Vue.js",
    "nuxt.js": "Nuxt.js",
    "express.js": "Express.js",
    "mongodb": "MongoDB",
    "power bi": "Power BI",
    "tailwind css": "Tailwind CSS",
}

_CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Programming", ["python", "java", "c++", "c#", "rust", "go", "kotlin", "swift", "javascript", "typescript", "programming"]),
    ("Web", ["react", "node", "api", "frontend", "backend", "html", "css", "graphql", "django", "flask", "fastapi", "spring", "angular", "vue"]),
    ("DevOps", ["docker", "kubernetes", "terraform", "ansible", "helm", "ci/cd", "jenkins", "prometheus", "grafana", "devops", "sre", "nginx"]),
    ("Databases", ["sql", "database", "postgres", "mysql", "mongodb", "redis", "nosql", "oracle", "sqlite", "dynamodb"]),
    ("Cloud", ["aws", "azure", "gcp", "cloud", "lambda", "ec2", "s3", "vpc", "serverless"]),
    ("Data Science", ["pandas", "numpy", "machine learning", "deep learning", "nlp", "statistics", "tensorflow", "pytorch", "scikit", "data"]),
    ("Soft Skills", ["communication", "leadership", "teamwork", "stakeholder", "mentoring", "negotiation", "collaboration", "critical thinking"]),
]

_SKILL_KEYS = {
    "skill",
    "skills",
    "required_skills",
    "key_skills",
    "competencies",
    "tags",
    "technologies",
    "tools",
    "primary_skills",
    "secondary_skills",
}

_TEXT_KEYS = {
    "text",
    "resume_text",
    "description",
    "job_description",
    "summary",
    "content",
}


def _normalize_text(value: str) -> str:
    lowered = value.lower()
    normalized = re.sub(r"[^a-z0-9#+./]+", " ", lowered)
    return re.sub(r"\s+", " ", normalized).strip()


def _normalize_skill(value: str) -> str:
    normalized = _normalize_text(value)
    if not normalized:
        return ""

    if normalized in _CANONICAL_OVERRIDES:
        return _CANONICAL_OVERRIDES[normalized]

    parts = [part.capitalize() for part in normalized.split()]
    return " ".join(parts)


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=True)
        file.write("\n")


def _load_existing_skills() -> list[str]:
    try:
        data = _read_json(_SKILLS_PATH)
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    skills: list[str] = []
    for item in data:
        if isinstance(item, str):
            skills.append(item)
        elif isinstance(item, dict) and isinstance(item.get("name"), str):
            skills.append(item["name"])

    return skills


def _iter_json_records(data: Any) -> Iterable[dict[str, Any]]:
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                yield item
    elif isinstance(data, dict):
        yielded = False
        for key in ("data", "records", "items", "rows"):
            value = data.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        yielded = True
                        yield item
        if not yielded:
            yield data


def _iter_external_records() -> Iterable[tuple[Path, dict[str, Any]]]:
    if not _EXTERNAL_DIR.exists():
        return

    patterns = ["*.json", "*.jsonl", "*.csv"]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(_EXTERNAL_DIR.rglob(pattern)))

    for file_path in files:
        try:
            if file_path.suffix.lower() == ".csv":
                with file_path.open("r", encoding="utf-8", errors="ignore", newline="") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        yield file_path, dict(row)
            elif file_path.suffix.lower() == ".jsonl":
                with file_path.open("r", encoding="utf-8", errors="ignore") as file:
                    for line in file:
                        line = line.strip()
                        if not line:
                            continue
                        item = json.loads(line)
                        if isinstance(item, dict):
                            yield file_path, item
            else:
                data = _read_json(file_path)
                for item in _iter_json_records(data):
                    yield file_path, item
        except Exception as exc:
            logger.warning("Skipping dataset file due to parse error: %s (%s)", file_path, exc)


def _split_skill_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in re.split(r"[,;|/]", value) if part.strip()]

    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            if isinstance(item, str):
                items.extend([part.strip() for part in re.split(r"[,;|/]", item) if part.strip()])
        return items

    return []


def _extract_skills_from_record(record: dict[str, Any], known_skills: set[str]) -> set[str]:
    skills: set[str] = set()

    for key, value in record.items():
        normalized_key = _normalize_text(key)
        if normalized_key in _SKILL_KEYS:
            for raw_skill in _split_skill_values(value):
                normalized_skill = _normalize_skill(raw_skill)
                if normalized_skill:
                    skills.add(normalized_skill)

    known_by_normalized = {_normalize_text(skill): skill for skill in known_skills}

    for key, value in record.items():
        normalized_key = _normalize_text(key)
        if normalized_key not in _TEXT_KEYS or not isinstance(value, str):
            continue

        text = f" {_normalize_text(value)} "
        for normalized_skill, skill in known_by_normalized.items():
            if normalized_skill and f" {normalized_skill} " in text:
                skills.add(skill)

    return skills


def _extract_ordered_skills_from_record(
    record: dict[str, Any],
) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()

    # Keep source field ordering where possible to infer prerequisite direction.
    for key, value in record.items():
        normalized_key = _normalize_text(key)
        if normalized_key not in _SKILL_KEYS:
            continue

        for raw_skill in _split_skill_values(value):
            normalized_skill = _normalize_skill(raw_skill)
            if not normalized_skill:
                continue

            if normalized_skill not in seen:
                ordered.append(normalized_skill)
                seen.add(normalized_skill)

    return ordered


def _load_existing_synonyms() -> dict[str, set[str]]:
    try:
        data = _read_json(_SYNONYMS_PATH)
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    synonyms: dict[str, set[str]] = {}
    for canonical, variants in data.items():
        if not isinstance(canonical, str):
            continue

        key = _normalize_text(canonical)
        if not key:
            continue

        synonyms[key] = set()
        if isinstance(variants, list):
            for variant in variants:
                if isinstance(variant, str):
                    normalized_variant = _normalize_text(variant)
                    if normalized_variant and normalized_variant != key:
                        synonyms[key].add(normalized_variant)

    return synonyms


def _build_synonyms(skills: list[str], dataset_records: Iterable[dict[str, Any]]) -> dict[str, list[str]]:
    synonyms = _load_existing_synonyms()

    for skill in skills:
        canonical = _normalize_text(skill)
        if not canonical:
            continue

        variants = synonyms.setdefault(canonical, set())

        compact = canonical.replace(" ", "")
        if compact != canonical:
            variants.add(compact)

        dotted = canonical.replace(" ", ".")
        if dotted != canonical:
            variants.add(dotted)

        if canonical.endswith(" api"):
            variants.add(canonical.replace(" api", "ful api"))
            variants.add(canonical.replace(" api", " services"))

    for record in dataset_records:
        aliases = record.get("aliases") or record.get("synonyms")
        skill = record.get("skill") or record.get("name")

        if not isinstance(skill, str):
            continue

        canonical = _normalize_text(skill)
        if not canonical:
            continue

        variants = synonyms.setdefault(canonical, set())

        if isinstance(aliases, list):
            for alias in aliases:
                if isinstance(alias, str):
                    normalized_alias = _normalize_text(alias)
                    if normalized_alias and normalized_alias != canonical:
                        variants.add(normalized_alias)

    return {
        canonical: sorted(variant for variant in variants if variant != canonical)
        for canonical, variants in sorted(synonyms.items())
        if variants
    }


def _categorize_skill(skill: str) -> str:
    normalized = _normalize_text(skill)

    for category, keywords in _CATEGORY_RULES:
        if any(keyword in normalized for keyword in keywords):
            return category

    return "General"


def _build_categories(skills: list[str]) -> dict[str, str]:
    return {skill: _categorize_skill(skill) for skill in skills}


def _load_existing_graph() -> dict[str, list[str]]:
    try:
        data = _read_json(_GRAPH_PATH)
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    graph: dict[str, list[str]] = {}
    for skill, prerequisites in data.items():
        if not isinstance(skill, str) or not isinstance(prerequisites, list):
            continue

        key = _normalize_skill(skill)
        values = [_normalize_skill(item) for item in prerequisites if isinstance(item, str)]
        graph[key] = [value for value in values if value and value != key]

    return graph


def _build_graph(dataset_items: Iterable[tuple[Path, dict[str, Any]]], existing_graph: dict[str, list[str]]) -> dict[str, list[str]]:
    graph = {skill: list(prereqs) for skill, prereqs in existing_graph.items()}

    for file_path, record in dataset_items:
        if "onet" not in file_path.name.lower() and "onet" not in str(file_path.parent).lower():
            continue

        skill_value = record.get("skill") or record.get("name") or record.get("target_skill")
        if not isinstance(skill_value, str):
            continue

        skill = _normalize_skill(skill_value)
        if not skill:
            continue

        prerequisites_raw = (
            record.get("prerequisites")
            or record.get("depends_on")
            or record.get("required_skills")
            or []
        )

        prerequisites = [_normalize_skill(item) for item in _split_skill_values(prerequisites_raw)]
        cleaned = [item for item in prerequisites if item and item != skill]

        if not cleaned:
            continue

        existing = graph.setdefault(skill, [])
        for prereq in cleaned:
            if prereq not in existing:
                existing.append(prereq)

    # Infer relationships from dataset co-occurrence and ordering.
    co_occurrence_count: Counter[tuple[str, str]] = Counter()
    precedence_count: Counter[tuple[str, str]] = Counter()

    for _, record in dataset_items:
        ordered_skills = _extract_ordered_skills_from_record(record)
        if len(ordered_skills) < 2:
            continue

        unique_skills = list(dict.fromkeys(ordered_skills))

        for i, skill_a in enumerate(unique_skills):
            for j in range(i + 1, len(unique_skills)):
                skill_b = unique_skills[j]
                pair = tuple(sorted((skill_a, skill_b)))
                co_occurrence_count[pair] += 1
                precedence_count[(skill_a, skill_b)] += 1

    def depends_on(start_skill: str, target_skill: str) -> bool:
        stack = [start_skill]
        visited: set[str] = set()

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)

            for prereq in graph.get(current, []):
                if prereq == target_skill:
                    return True
                stack.append(prereq)

        return False

    inferred_edges: dict[str, set[str]] = defaultdict(set)
    for pair, pair_count in co_occurrence_count.items():
        if pair_count < 2:
            continue

        first, second = pair
        first_before_second = precedence_count.get((first, second), 0)
        second_before_first = precedence_count.get((second, first), 0)

        dominant_count = max(first_before_second, second_before_first)
        if dominant_count == 0:
            continue

        dominance_ratio = dominant_count / pair_count
        if dominance_ratio < 0.65:
            continue

        if first_before_second > second_before_first:
            prereq, dependent = first, second
        else:
            prereq, dependent = second, first

        inferred_edges[dependent].add(prereq)

    for dependent, prereqs in inferred_edges.items():
        existing = graph.setdefault(dependent, [])

        for prereq in sorted(prereqs):
            if prereq == dependent:
                continue

            # Prevent circular edges in the directed prerequisite graph.
            if depends_on(prereq, dependent):
                continue

            if prereq not in existing:
                existing.append(prereq)

    for skill, prereqs in list(graph.items()):
        seen: set[str] = set()
        unique = []
        for prereq in prereqs:
            if prereq not in seen and prereq != skill:
                unique.append(prereq)
                seen.add(prereq)
        graph[skill] = unique

    return dict(sorted(graph.items(), key=lambda item: item[0]))


def enrich_datasets() -> dict[str, int]:
    existing_skills = _load_existing_skills()
    normalized_existing = [_normalize_skill(skill) for skill in existing_skills]
    normalized_existing = [skill for skill in normalized_existing if skill]

    record_pairs = list(_iter_external_records() or [])
    records_only = [record for _, record in record_pairs]

    known_skill_set = set(normalized_existing)
    discovered_skills: set[str] = set()
    for _, record in record_pairs:
        discovered_skills.update(_extract_skills_from_record(record, known_skill_set))

    merged_skills = sorted(set(normalized_existing).union(discovered_skills))

    if len(merged_skills) < 200:
        merged_skills = sorted(set(merged_skills).union(set(normalized_existing)))

    _write_json(_SKILLS_PATH, merged_skills)

    synonyms = _build_synonyms(merged_skills, records_only)
    _write_json(_SYNONYMS_PATH, synonyms)

    categories = _build_categories(merged_skills)
    _write_json(_CATEGORIES_PATH, categories)

    existing_graph = _load_existing_graph()
    graph = _build_graph(record_pairs, existing_graph)
    _write_json(_GRAPH_PATH, graph)

    logger.info(
        "Dataset enrichment complete: skills=%s synonyms=%s categories=%s graph_nodes=%s",
        len(merged_skills),
        len(synonyms),
        len(categories),
        len(graph),
    )

    return {
        "skills": len(merged_skills),
        "synonyms": len(synonyms),
        "categories": len(categories),
        "graph_nodes": len(graph),
    }
