def calculate_match_score(resume_skills, jd_skills):
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    if not jd_set:
        return 0, [], "Rejected"

    matched = resume_set.intersection(jd_set)
    missing = jd_set - resume_set

    score = int((len(matched) / len(jd_set)) * 100)

    status = "Shortlisted" if score >= 70 else "Rejected"

    return score, list(missing), status
