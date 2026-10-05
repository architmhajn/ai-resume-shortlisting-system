# AI Resume Shortlisting System

An explainable AI-based resume screening application built with Flask, Python and MySQL. It combines explicit skill matching, semantic similarity and structured resume evidence to rank candidates against a job description.

## Features

- PDF resume upload and text extraction
- Skill normalization with aliases such as Python/Python3 and JavaScript/JS
- Required vs preferred skill matching
- Semantic similarity using Sentence Transformers
- Structured evidence for experience, education, projects and certifications
- Explainable score breakdown and detected gaps
- Multi-candidate recruiter ranking dashboard
- Candidate detail view
- Optional LLM-powered structured extraction with deterministic fallback
- Evaluation script for precision, recall, F1 and average precision
- Automated unit tests for core scoring logic

## Scoring

The production score is:

- **50% Skill Match** — explicit required/preferred skill alignment
- **30% Semantic Relevance** — contextual similarity between resume and JD
- **20% Structured Evidence** — experience, education, projects and certifications

A missing required skill caps the skill component at 69, preventing preferred skills from masking an important requirement.

## Architecture

```
PDF Resume ──> Text Extraction ──> Skill Extraction ──────┐
                                                         │
Job Description ───────────────> JD Requirement Analysis ├─> Final Score
                                                         │
Resume + JD ──> Sentence Transformer ─> Semantic Score ──┤
                                                         │
Resume/JD ──> Structured/LLM Extraction ─> Evidence ─────┘
                                                               │
                                                               v
                                                    Recruiter Ranking Dashboard
```

## Setup

1. Create a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create the MySQL database and tables required by the existing application schema.
4. Configure environment variables:

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=resume_ai
FLASK_DEBUG=0

# Optional LLM extraction
LLM_API_KEY=your_api_key
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-4o-mini
```

The LLM layer is optional. Without an API key, the application uses deterministic extraction.

5. Run:

```bash
python app.py
```

Open the local Flask URL shown in the terminal.

## Testing

Run the core tests with:

```bash
pytest -q
```

## Evaluation

The evaluator accepts JSONL records in this format:

```json
{"resume":"...", "job_description":"...", "relevant":true}
```

Run:

```bash
python evaluation/evaluate.py evaluation/dataset.jsonl --threshold 70
```

Use human-labeled data for meaningful metrics. Do not treat fabricated or tiny example datasets as benchmark results.

## Security note

Database credentials are read from environment variables and should never be committed to the repository. The original repository history contained a database password; that credential should be rotated even though the current branch no longer contains it.

## Project goal

The project demonstrates how a student-built recruitment system can move beyond keyword matching by combining deterministic NLP, transformer-based semantic similarity, structured evidence extraction and explainable ranking.
