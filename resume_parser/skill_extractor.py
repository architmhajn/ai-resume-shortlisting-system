import re

# Canonical skill -> common variants found in resumes and job descriptions.
SKILL_ALIASES = {
    "python": ["python", "python3"],
    "java": ["java", "java se", "java ee"],
    "c": ["c", "c language"],
    "c++": ["c++", "cpp"],
    "sql": ["sql", "structured query language"],
    "mysql": ["mysql", "my sql"],
    "postgresql": ["postgresql", "postgres", "postgre sql"],
    "flask": ["flask", "flask framework"],
    "django": ["django", "django framework"],
    "spring": ["spring", "spring framework", "spring boot"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "javascript": ["javascript", "js", "ecmascript"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "nlp": ["nlp", "natural language processing"],
    "data analysis": ["data analysis", "data analytics"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf"],
    "git": ["git", "git scm"],
    "github": ["github", "github actions"],
    "docker": ["docker", "containerization", "containers"],
    "aws": ["aws", "amazon web services"],
    "linux": ["linux", "unix"],
    "rest api": ["rest api", "restful api", "rest apis", "restful services"],
    "spring boot": ["spring boot", "springboot"],
    "fastapi": ["fastapi", "fast api"],
}

SKILLS_DB = list(SKILL_ALIASES.keys())


def extract_skills(text):
    """Return canonical skill names using phrase-aware alias matching."""
    normalized = re.sub(r"\\s+", " ", text.lower())
    found_skills = set()

    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            # Boundary checks prevent short skills such as 'c' from matching
            # inside unrelated words.
            pattern = r"(?<!\\w)" + re.escape(alias) + r"(?!\\w)"
            if re.search(pattern, normalized):
                found_skills.add(canonical)
                break

    return sorted(found_skills)
