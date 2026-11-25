import json
import os
import urllib.error
import urllib.request


RESUME_SCHEMA = {
    "skills": [],
    "experience": [{"title": "", "company": "", "years": 0, "description": ""}],
    "education": [{"degree": "", "institution": "", "year": ""}],
    "projects": [{"name": "", "description": "", "technologies": []}],
    "certifications": [],
}

JD_SCHEMA = {
    "required_skills": [],
    "preferred_skills": [],
    "min_experience_years": 0,
    "education": "",
    "responsibilities": [],
}


def _call_llm(prompt):
    """Call an OpenAI-compatible chat endpoint when configured."""
    api_key = os.getenv("LLM_API_KEY")
    endpoint = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    if not api_key:
        return None

    payload = json.dumps({
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "Return only valid JSON. Never invent facts not present in the document."},
            {"role": "user", "content": prompt},
        ],
    }).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
            return json.loads(body["choices"][0]["message"]["content"])
    except (urllib.error.URLError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"LLM extraction unavailable: {exc}")
        return None


def extract_resume_with_llm(text):
    prompt = f"""Extract the resume into this exact JSON shape:\n{json.dumps(RESUME_SCHEMA)}\n\nResume:\n{text}"""
    return _call_llm(prompt)


def extract_jd_with_llm(text):
    prompt = f"""Extract the job description into this exact JSON shape:\n{json.dumps(JD_SCHEMA)}\n\nJob description:\n{text}"""
    return _call_llm(prompt)
