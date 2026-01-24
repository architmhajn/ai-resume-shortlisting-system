CREATE DATABASE resume_ai;
USE resume_ai;
CREATE TABLE resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    extracted_text LONGTEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE job_descriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jd_text LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT,
    match_score INT,
    missing_skills TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);
