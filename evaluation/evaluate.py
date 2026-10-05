"""Evaluation utilities for the resume ranking pipeline.

Expected JSONL input, one example per line:
{"resume": "...", "job_description": "...", "relevant": true}

"relevant" is the human-labeled ground truth. The evaluator reports
classification and ranking metrics without changing the production scorer.
"""

import argparse
import json
from pathlib import Path

from resume_parser.scorer import calculate_match_score
from resume_parser.semantic_matcher import semantic_similarity
from resume_parser.skill_extractor import extract_skills


def score_pair(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    skill_score, _, _ = calculate_match_score(resume_skills, jd_skills, jd_text=jd_text)
    semantic_score = semantic_similarity(resume_text, jd_text)
    return round(skill_score * 0.65 + semantic_score * 0.35)


def evaluate(records, threshold=70):
    scored = []
    for record in records:
        score = score_pair(record["resume"], record["job_description"])
        scored.append({"score": score, "relevant": bool(record["relevant"])})

    tp = sum(x["score"] >= threshold and x["relevant"] for x in scored)
    fp = sum(x["score"] >= threshold and not x["relevant"] for x in scored)
    fn = sum(x["score"] < threshold and x["relevant"] for x in scored)
    tn = sum(x["score"] < threshold and not x["relevant"] for x in scored)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(scored) if scored else 0.0

    # Ranking metric: average precision for the examples, sorted by model score.
    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    relevant_seen = 0
    precision_sum = 0.0
    total_relevant = sum(x["relevant"] for x in ranked)
    for index, item in enumerate(ranked, start=1):
        if item["relevant"]:
            relevant_seen += 1
            precision_sum += relevant_seen / index
    average_precision = precision_sum / total_relevant if total_relevant else 0.0

    return {
        "samples": len(scored),
        "threshold": threshold,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "average_precision": round(average_precision, 4),
        "confusion_matrix": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate resume shortlisting quality")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--threshold", type=int, default=70)
    args = parser.parse_args()

    records = [json.loads(line) for line in args.dataset.read_text().splitlines() if line.strip()]
    print(json.dumps(evaluate(records, args.threshold), indent=2))


if __name__ == "__main__":
    main()
