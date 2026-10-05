import re


def extract_requirements(jd_text, skills):
    """Extract required/preferred skills and simple experience requirements from a JD.

    This is a deterministic first-pass extractor. It is intentionally separate from
    scoring so an LLM/embedding extractor can replace or enrich it later.
    """
    text = jd_text.lower()
    required = set()
    preferred = set()

    # Common requirement language. Keep this conservative to avoid inventing requirements.
    required_markers = re.compile(
        r"(?:required|must have|mandatory|essential|should have|strong knowledge of|proficient in|experience with)"
        r"[^.\n:;]{0,180}", re.I,
    )
    preferred_markers = re.compile(
        r"(?:preferred|nice to have|good to have|plus|bonus|desirable)":[^\n.]{0,180}", re.I,
    )

    required_chunks = required_markers.findall(jd_text)
    preferred_chunks = preferred_markers.findall(jd_text)

    for skill in skills:
        pattern = r"(?<!\\w)" + re.escape(skill) + r"(?!\\w)"
        if re.search(pattern, text):
            if any(re.search(pattern, chunk, re.I) for chunk in required_chunks):
                required.add(skill)
            elif any(re.search(pattern, chunk, re.I) for chunk in preferred_chunks):
                preferred.add(skill)

    # If the JD does not explicitly label requirements, treat detected skills as
    # required rather than silently making every skill optional.
    if not required and not preferred:
        required = set(skills)

    preferred -= required

    experience_years = None
    exp_patterns = [
        r"(\d+)\s*\+?\s*years?\s+(?:of\s+)?(?:relevant\s+)?experience",
        r"experience\s*(?:of|:)?\s*(\d+)\s*\+?\s*years?",
    ]
    for pattern in exp_patterns:
        match = re.search(pattern, text)
        if match:
            experience_years = int(match.group(1))
            break

    return {
        "required_skills": sorted(required),
        "preferred_skills": sorted(preferred),
        "experience_years": experience_years,
    }
