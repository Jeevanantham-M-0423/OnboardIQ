from typing import Iterable


def find_skill_gap(
    resume_skills: Iterable[str],
    jd_skills: Iterable[str],
) -> dict[str, list[str]]:
    resume_set = {skill.strip() for skill in resume_skills if skill and skill.strip()}
    jd_set = {skill.strip() for skill in jd_skills if skill and skill.strip()}

    missing_skills = sorted(jd_set - resume_set)
    matched_skills = sorted(jd_set & resume_set)

    return {
        "missing_skills": missing_skills,
        "matched_skills": matched_skills,
    }
