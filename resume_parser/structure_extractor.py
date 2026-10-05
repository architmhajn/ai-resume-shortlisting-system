import re


def _section(text, headings):
    pattern = r"(?:^|\\n)\\s*(?:" + "|".join(re.escape(h) for h in headings) + r")\\s*[:\\-]?\\s*(.*?)(?=\\n\\s*[A-Za-z][A-Za-z &/]{2,30}\\s*[:\\-]?\\s*\\n|$)"
    match = re.search(pattern, text, re.I | re.S)
    return match.group(1).strip() if match else ""


def extract_structure(text):
    """Extract conservative, evidence-based resume structure from raw text."""
    experience_section = _section(text, ["experience", "work experience", "professional experience", "employment"])
    education_section = _section(text, ["education", "academic background"])
    projects_section = _section(text, ["projects", "academic projects", "personal projects"])
    certifications_section = _section(text, ["certifications", "certificates"])

    years = [int(x) for x in re.findall(r"(?<!\\d)(\\d{1,2})\\s*\\+?\\s*years?", text.lower())]
    experience_years = max(years) if years else 0

    degree_terms = re.findall(
        r"\\b(?:b\\.?tech|b\\.?e\\.?|m\\.?tech|m\\.?e\\.?|bachelor(?:'s)?|master(?:'s)?|ph\\.?d)\\b",
        text,
        re.I,
    )

    return {
        "experience_text": experience_section,
        "education_text": education_section,
        "projects_text": projects_section,
        "certifications_text": certifications_section,
        "experience_years": experience_years,
        "degree_mentions": sorted(set(x.lower() for x in degree_terms)),
        "has_projects": bool(projects_section),
        "has_certifications": bool(certifications_section),
        "has_education": bool(education_section or degree_terms),
    }


def extract_jd_profile(jd_text):
    """Extract explicit JD expectations without inventing candidate facts."""
    text = jd_text.lower()
    years = re.findall(r"(?<!\\d)(\\d{1,2})\\s*\\+?\\s*years?", text)
    experience_years = max((int(x) for x in years), default=0)

    education_required = bool(re.search(
        r"\\b(b\\.?tech|b\\.?e\\.?|m\\.?tech|m\\.?e\\.?|bachelor|master|degree)\\b",
        text,
        re.I,
    ))

    return {
        "experience_years": experience_years,
        "education_required": education_required,
    }
