import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
from resume_parser.skill_extractor import extract_skills

from resume_parser.extract_text import extract_text_from_pdf

from flask import Flask, render_template
import mysql.connector
from flask import request, redirect, url_for
import os
from werkzeug.utils import secure_filename



app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Archit@dbms",
        database="resume_ai"
    )

@app.route('/')
def upload():
    return render_template('upload.html')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_resume():

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if 'resume' not in request.files:
        return "No file uploaded"

    file = request.files['resume']

    if file.filename == '':
        return "No selected file"

    if not allowed_file(file.filename):
        return "Only PDF files are allowed"

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)


    text = extract_text_from_pdf(file_path)
    skills = extract_skills(text)
    print("Extracted Skills:", skills)

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO resumes (filename, extracted_text)
    VALUES (%s, %s)
    """
    cursor.execute(sql, (filename, text))
    conn.commit()

    cursor.close()
    conn.close()

    return "Resume uploaded, text extracted & saved to database"




if __name__ == "__main__":
    app.run(debug=True)
