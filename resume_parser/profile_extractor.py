from .llm_extractor import extract_jd_with_llm, extract_resume_with_llm
from .structure_extractor import extract_jd_profile, extract_structure


def extract_resume_profile(text):
    """Prefer LLM structure when configured, otherwise use deterministic extraction."""
    profile = extract_resume_with_llm(text)
    if profile:
        fallback = extract_structure(text)
        profile.setdefault("skills", [])
        profile.setdefault("experience", [])
        profile.setdefault("education", [])
        profile.setdefault("projects", [])
        profile.setdefault("certifications", [])
        profile["experience_years"] = max(
            [float(item.get("years", 0) or 0) for item in profile["experience"]] + [fallback["experience_years"]]
        )
        profile["has_projects"] = bool(profile["projects"])
        profile["has_certifications"] = bool(profile["certifications"])
        profile["has_education"] = bool(profile["education"])
        return profile
    return extract_structure(text)


def extract_job_profile(text):
    """Prefer LLM JD structure when configured, with deterministic fallback."""
    profile = extract_jd_with_llm(text)
    if profile:
        fallback = extract_jd_profile(text)
        profile.setdefault("required_skills", [])
        profile.setdefault("preferred_skills", [])
        profile.setdefault("responsibilities", [])
        profile.setdefault("min_experience_years", fallback["experience_years"])
        profile.setdefault("education", "")
        return profile
    return extract_jd_profile(text)
