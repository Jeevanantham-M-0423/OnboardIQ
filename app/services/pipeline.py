from __future__ import annotations

import hashlib
from pathlib import Path
from threading import Lock
from typing import Any

from app.services.gap_analyzer import find_skill_gap
from app.services.parser import extract_text_from_docx, extract_text_from_pdf
from app.services.path_generator import generate_learning_path
from app.services.reasoning import generate_reason
from app.services.resource_mapper import map_resources
from app.services.skill_extractor import extract_skills

_CACHE_LOCK = Lock()
_PIPELINE_CACHE: dict[str, dict[str, Any]] = {}


def _compute_file_hash(file_path: Path) -> str:
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)

    return digest.hexdigest()


def _make_cache_key(resume_path: Path, job_description_path: Path) -> str:
    resume_hash = _compute_file_hash(resume_path)
    jd_hash = _compute_file_hash(job_description_path)
    return f"{resume_hash}:{jd_hash}"


def _extract_text_by_extension(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)

    if suffix == ".docx":
        return extract_text_from_docx(file_path)

    return ""


def build_onboarding_pipeline(resume_path: Path, job_description_path: Path) -> dict[str, Any]:
    if not resume_path.exists():
        raise ValueError("Resume file is missing.")

    if not job_description_path.exists():
        raise ValueError("Job description file is missing.")

    cache_key = _make_cache_key(resume_path, job_description_path)

    with _CACHE_LOCK:
        cached_result = _PIPELINE_CACHE.get(cache_key)

    if cached_result is not None:
        return cached_result

    resume_text = _extract_text_by_extension(resume_path).strip()
    jd_text = _extract_text_by_extension(job_description_path).strip()

    if not resume_text:
        raise ValueError("Resume content is empty or could not be extracted.")

    if not jd_text:
        raise ValueError("Job description content is empty or could not be extracted.")

    resume_skills = list(extract_skills(resume_text) or [])
    jd_skills = list(extract_skills(jd_text) or [])

    gap_result = find_skill_gap(resume_skills, jd_skills)

    learning_path_result = generate_learning_path(
        list(gap_result.get("missing_skills", []) or []),
        resume_skills,
    )

    roadmap_items = map_resources(list(learning_path_result.get("learning_path", []) or []))

    roadmap: list[dict[str, object]] = []
    for item in roadmap_items:
        skill_name = str(item.get("skill", "")).strip()
        resources = item.get("resources", {})

        if not skill_name:
            continue

        roadmap.append(
            {
                "skill": skill_name,
                "reason": generate_reason(skill_name, jd_skills, resume_skills),
                "resources": resources if isinstance(resources, dict) else {},
            }
        )

    result = {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": list(gap_result.get("matched_skills", []) or []),
        "missing_skills": list(gap_result.get("missing_skills", []) or []),
        "roadmap": roadmap,
    }

    with _CACHE_LOCK:
        # Keep caching simple and bounded.
        if len(_PIPELINE_CACHE) >= 128:
            _PIPELINE_CACHE.clear()
        _PIPELINE_CACHE[cache_key] = result

    return result
