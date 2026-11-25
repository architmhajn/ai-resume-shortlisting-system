import os
import sys
import uuid

import mysql.connector
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from resume_parser.extract_text import extract_text_from_pdf
from resume_parser.profile_extractor import extract_job_profile, extract_resume_profile
from resume_parser.scorer import calculate_match_score
from resume_parser.semantic_matcher import semantic_similarity
from resume_parser.skill_extractor import extract_skills
from resume_parser.structured_scorer import build_explanation, calculate_structured_score

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf"}


def get_db_connection():
    return mysql.connector.connect(host=os.getenv("DB_HOST", "localhost"), user=os.getenv("DB_USER", "root"), password=os.getenv("DB_PASSWORD", ""), database=os.getenv("DB_NAME", "resume_ai"))


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def calculate_final_score(skill_score, semantic_score, structured_score):
    return round(skill_score * 0.50 + semantic_score * 0.30 + structured_score * 0.20)


def analyze_candidate(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    skill_score, missing_skills, _ = calculate_match_score(resume_skills, jd_skills, jd_text=jd_text)
    try:
        semantic_score = semantic_similarity(resume_text, jd_text)
    except Exception as exc:
        print(f"Semantic matcher unavailable: {exc}")
        semantic_score = 0.0
    resume_profile, resume_llm_used = extract_resume_profile(resume_text, return_source=True)
    jd_profile, jd_llm_used = extract_job_profile(jd_text, return_source=True)
    structured_score = calculate_structured_score(resume_profile, jd_profile)
    score = calculate_final_score(skill_score, semantic_score, structured_score)
    reasons, evidence_gaps = build_explanation(resume_profile, jd_profile, skill_score, semantic_score)
    return {
        "score": score, "skill_score": skill_score, "semantic_score": semantic_score,
        "structured_score": structured_score,
        "missing_skills": list(dict.fromkeys(missing_skills + evidence_gaps)),
        "reasons": reasons, "status": "Shortlisted" if score >= 70 else "Rejected",
        "experience_years": resume_profile.get("experience_years", 0),
        "has_projects": resume_profile.get("has_projects", False),
        "has_certifications": resume_profile.get("has_certifications", False),
        "llm_enriched": resume_llm_used or jd_llm_used,
    }


insert_result_sql = "INSERT INTO results (resume_id, score, status, missing_skills) VALUES (%s, %s, %s, %s)"


@app.route("/")
def upload():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload_resume():
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    if "resume" not in request.files:
        return "No file uploaded", 400
    file = request.files["resume"]
    if file.filename == "":
        return "No selected file", 400
    if not allowed_file(file.filename):
        return "Only PDF files are allowed", 400
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    text = extract_text_from_pdf(file_path)
    jd_text = request.form.get("job_description", "").strip()
    analysis = analyze_candidate(text, jd_text) if jd_text else {"score": None, "skill_score": None, "semantic_score": None, "structured_score": None, "missing_skills": [], "reasons": [], "status": "JD Not Provided", "experience_years": 0, "has_projects": False, "has_certifications": False}
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO resumes (filename, extracted_text) VALUES (%s, %s)", (filename, text))
        resume_id = cursor.lastrowid
        cursor.execute(insert_result_sql, (resume_id, analysis["score"] or 0, analysis["status"], ", ".join(analysis["missing_skills"])))
        conn.commit()
    except Exception:
        conn.rollback(); raise
    finally:
        cursor.close(); conn.close()
    return render_template("result.html", resume_skills=extract_skills(text), jd_skills=extract_skills(jd_text) if jd_text else "Not Provided", **analysis)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", results=[], ranked=False, job_description="")


@app.route("/rank", methods=["POST"])
def rank_resumes():
    jd_text = request.form.get("job_description", "").strip()
    if not jd_text:
        return "Job description is required", 400
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, filename, extracted_text FROM resumes ORDER BY id DESC")
        candidates = cursor.fetchall()
    finally:
        cursor.close(); conn.close()
    ranked = [{"id": c["id"], "filename": c["filename"], **analyze_candidate(c["extracted_text"], jd_text)} for c in candidates]
    ranked.sort(key=lambda row: row["score"], reverse=True)
    for position, row in enumerate(ranked, start=1):
        row["rank"] = position
    return render_template("dashboard.html", results=ranked, ranked=True, job_description=jd_text)


@app.route("/candidate/<int:resume_id>")
def candidate_detail(resume_id):
    jd_text = request.args.get("job_description", "").strip()
    if not jd_text:
        return "Job description is required", 400
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, filename, extracted_text FROM resumes WHERE id = %s", (resume_id,))
        candidate = cursor.fetchone()
    finally:
        cursor.close(); conn.close()
    if not candidate:
        return "Candidate not found", 404
    analysis = analyze_candidate(candidate["extracted_text"], jd_text)
    return render_template("candidate.html", candidate=candidate, analysis=analysis)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
