import re

SKILLS_DB = [
    "python", "java", "c", "c++", "sql", "mysql", "postgresql",
    "flask", "django", "spring", "html", "css", "javascript",
    "machine learning", "deep learning", "nlp",
    "data analysis", "pandas", "numpy",
    "git", "github", "docker", "aws", "linux"
]

def extract_skills(text):
    text = text.lower()
    found_skills = set()

    for skill in SKILLS_DB:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            found_skills.add(skill)

    return list(found_skills)
