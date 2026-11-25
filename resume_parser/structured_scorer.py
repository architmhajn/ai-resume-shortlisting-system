def calculate_structured_score(resume_profile, jd_profile):
    """Score experience, education, projects and certifications as evidence."""
    required_experience = jd_profile.get("min_experience_years", jd_profile.get("experience_years", 0)) or 0
    candidate_experience = float(resume_profile.get("experience_years", 0) or 0)
    experience_score = min(candidate_experience / required_experience, 1.0) * 100 if required_experience else 100.0

    education_required = bool(jd_profile.get("education") or jd_profile.get("education_required"))
    education_score = 100.0 if (not education_required or resume_profile.get("has_education")) else 0.0
    project_score = 100.0 if resume_profile.get("has_projects") else 0.0
    certification_score = 100.0 if resume_profile.get("has_certifications") else 0.0

    return round(experience_score * 0.55 + education_score * 0.25 + project_score * 0.10 + certification_score * 0.10)


def build_explanation(resume_profile, jd_profile, skill_score, semantic_score):
    reasons, gaps = [], []
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

    required_experience = jd_profile.get("min_experience_years", jd_profile.get("experience_years", 0)) or 0
    actual_experience = resume_profile.get("experience_years", 0)
    if required_experience:
        if actual_experience >= required_experience:
            reasons.append(f"Meets the {required_experience}-year experience requirement")
        else:
            gaps.append(f"Experience evidence is below the {required_experience}-year requirement")

    if jd_profile.get("education") or jd_profile.get("education_required"):
        if resume_profile.get("has_education"):
            reasons.append("Education evidence detected")
        else:
            gaps.append("Required education evidence was not detected")

    if resume_profile.get("has_projects"):
        reasons.append("Relevant project evidence detected")
    if resume_profile.get("has_certifications"):
        reasons.append("Certification evidence detected")

    return reasons, gaps
