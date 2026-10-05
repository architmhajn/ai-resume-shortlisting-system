import os
import sys
import uuid

import mysql.connector
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from resume_parser.extract_text import extract_text_from_pdf
from resume_parser.scorer import calculate_match_score
from resume_parser.skill_extractor import extract_skills

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {"pdf"}


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "resume_ai"),
    )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


insert_result_sql = """
INSERT INTO results (resume_id, score, status, missing_skills)
VALUES (%s, %s, %s, %s)
"""


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

    # UUID avoids overwriting another candidate's upload when filenames match.
    safe_name = secure_filename(file.filename)
    filename = f"{uuid.uuid4().hex}_{safe_name}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    text = extract_text_from_pdf(file_path)
    skills = extract_skills(text)
    jd_text = request.form.get("job_description", "").strip()

    if jd_text:
        jd_skills = extract_skills(jd_text)
        score, missing_skills, status = calculate_match_score(
            skills, jd_skills, jd_text=jd_text
        )
    else:
        jd_skills = []
        score = None
        missing_skills = []
        status = "JD Not Provided"

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO resumes (filename, extracted_text) VALUES (%s, %s)",
            (filename, text),
        )
        resume_id = cursor.lastrowid

        cursor.execute(
            insert_result_sql,
            (
                resume_id,
                score if score is not None else 0,
                status,
                ", ".join(missing_skills),
            ),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "result.html",
        resume_skills=skills,
        jd_skills=jd_skills if jd_text else "Not Provided",
        score=score,
        missing_skills=missing_skills,
        status=status,
    )


@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                r.id,
                r.filename,
                res.score,
                res.status,
                res.missing_skills,
                res.created_at
            FROM resumes r
            JOIN results res ON r.id = res.resume_id
            ORDER BY res.score DESC
            """
        )
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("dashboard.html", results=results)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
