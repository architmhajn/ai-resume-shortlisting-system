from .llm_extractor import extract_jd_with_llm, extract_resume_with_llm
from .structure_extractor import extract_jd_profile, extract_structure


def extract_resume_profile(text, return_source=False):
    """Extract a resume profile and optionally report whether LLM extraction was used."""
    profile = extract_resume_with_llm(text)
    if profile:
        fallback = extract_structure(text)
        profile.setdefault("skills", [])
        profile.setdefault("experience", [])
        profile.setdefault("education", [])
        profile.setdefault("projects", [])
        profile.setdefault("certifications", [])
        years = []
        for item in profile["experience"]:
            if isinstance(item, dict):
                try:
                    years.append(float(item.get("years", 0) or 0))
                except (TypeError, ValueError):
                    pass
        profile["experience_years"] = max(years + [float(fallback.get("experience_years", 0) or 0)])
        profile["has_projects"] = bool(profile["projects"])
        profile["has_certifications"] = bool(profile["certifications"])
        profile["has_education"] = bool(profile["education"])
        return (profile, True) if return_source else profile
    fallback = extract_structure(text)
    return (fallback, False) if return_source else fallback


def extract_job_profile(text, return_source=False):
    """Extract a JD profile and optionally report whether LLM extraction was used."""
    profile = extract_jd_with_llm(text)
    if profile:
        fallback = extract_jd_profile(text)
        if not isinstance(profile.get("required_skills"), list):
            profile["required_skills"] = []
        if not isinstance(profile.get("preferred_skills"), list):
            profile["preferred_skills"] = []
        if not isinstance(profile.get("responsibilities"), list):
            profile["responsibilities"] = []
        if not profile.get("min_experience_years"):
            profile["min_experience_years"] = fallback.get("experience_years", 0)
        if not profile.get("education"):
            profile["education"] = fallback.get("education", "")
        return (profile, True) if return_source else profile
    fallback = extract_jd_profile(text)
    return (fallback, False) if return_source else fallback
