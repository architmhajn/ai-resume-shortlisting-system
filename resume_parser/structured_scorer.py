def calculate_structured_score(resume_profile, jd_profile):
    """Score explicit experience and education evidence.

    Missing sections are not treated as automatic failures; only explicit JD
    requirements influence these components.
    """
    experience_required = jd_profile.get("experience_years", 0)
    candidate_experience = resume_profile.get("experience_years", 0)

    if experience_required:
        experience_score = min(candidate_experience / experience_required, 1.0) * 100
    else:
        experience_score = 100.0

    if jd_profile.get("education_required"):
        education_score = 100.0 if resume_profile.get("has_education") else 0.0
    else:
        education_score = 100.0

    # Experience is more informative than section presence, but both remain
    # subordinate to explicit skills and semantic relevance.
    return round(experience_score * 0.70 + education_score * 0.30)


def build_explanation(resume_profile, jd_profile, skill_score, semantic_score):
    reasons = []
    gaps = []

    if skill_score >= 80:
        reasons.append("Strong explicit skill alignment")
    elif skill_score >= 60:
        reasons.append("Moderate explicit skill alignment")
    else:
        gaps.append("Several required skills are missing")

    if semantic_score >= 75:
        reasons.append("High contextual similarity to the job description")
    elif semantic_score < 55:
        gaps.append("Low contextual similarity to the job description")

    required_experience = jd_profile.get("experience_years", 0)
    actual_experience = resume_profile.get("experience_years", 0)
    if required_experience:
        if actual_experience >= required_experience:
            reasons.append(f"Meets the {required_experience}-year experience requirement")
        else:
            gaps.append(f"Experience evidence is below the {required_experience}-year requirement")

    if jd_profile.get("education_required") and not resume_profile.get("has_education"):
        gaps.append("Required education evidence was not detected")

    return reasons, gaps
