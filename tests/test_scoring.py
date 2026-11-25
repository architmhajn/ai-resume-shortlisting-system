from resume_parser.scorer import calculate_match_score
from resume_parser.skill_extractor import extract_skills


def test_skill_aliases_are_normalized():
    skills = extract_skills("Python, Python3, Spring Boot, REST API, JavaScript and SQL")
    assert "python" in skills
    assert "spring boot" in skills
    assert "spring" not in skills
    assert "javascript" in skills
    assert "rest api" in skills


def test_missing_required_skill_caps_score():
    score, missing, status = calculate_match_score(["python"], ["python", "java"], jd_text="Required: Python and Java")
    assert score == 69
    assert "java" in missing
    assert status == "Rejected"


def test_preferred_skill_has_lower_weight():
    score, missing, status = calculate_match_score(["python"], ["python", "java"], jd_text="Required: Python. Preferred: Java.")
    assert score == 80
    assert missing == ["java"]
    assert status == "Shortlisted"
