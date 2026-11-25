import re


def extract_jd_requirements(jd_text, jd_skills):
    """Classify detected JD skills as required or preferred when language supports it."""
    text = jd_text.lower()
    required = set()
    preferred = set()

    required_chunks = re.findall(
        r"(?:required|must have|mandatory|essential|should have|strong knowledge of|proficient in|experience with)[^.\\n:;]{0,180}",
        text,
        re.I,
    )
    preferred_chunks = re.findall(
        r"(?:preferred|nice to have|good to have|plus|bonus|desirable)[^.\\n]{0,180}",
        text,
        re.I,
    )

    for skill in jd_skills:
        pattern = r"(?<!\\w)" + re.escape(skill.lower()) + r"(?!\\w)"
        if any(re.search(pattern, chunk, re.I) for chunk in required_chunks):
            required.add(skill)
        elif any(re.search(pattern, chunk, re.I) for chunk in preferred_chunks):
            preferred.add(skill)

    # Backward-compatible fallback: if the JD does not explicitly label skills,
    # treat all detected skills as required instead of silently making them optional.
    if not required and not preferred:
        required = set(jd_skills)

    preferred -= required
    return sorted(required), sorted(preferred)


def calculate_match_score(resume_skills, jd_skills, jd_text=None):
    """Return an explainable skill score while preserving the original API shape."""
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    if not jd_set:
        return 0, [], "Rejected"

    if jd_text:
        required_skills, preferred_skills = extract_jd_requirements(jd_text, jd_skills)
    else:
        required_skills, preferred_skills = list(jd_set), []

    required_set = set(required_skills)
    preferred_set = set(preferred_skills)

    matched_required = sorted(resume_set & required_set)
    missing_required = sorted(required_set - resume_set)
    matched_preferred = sorted(resume_set & preferred_set)
    missing_preferred = sorted(preferred_set - resume_set)

    required_score = (
        len(matched_required) / len(required_set) * 100
        if required_set else 100
    )
    preferred_score = (
        len(matched_preferred) / len(preferred_set) * 100
        if preferred_set else 100
    )

    # Mandatory skills dominate the score. A missing mandatory skill also
    # prevents preferred skills from producing a false positive shortlist.
    score = round(required_score * 0.80 + preferred_score * 0.20)
    if missing_required:
        score = min(score, 69)

    status = "Shortlisted" if score >= 70 else "Rejected"
    missing = missing_required + missing_preferred
    return score, missing, status
