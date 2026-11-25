import glob, time, traceback
from resume_parser.extract_text import extract_text_from_pdf
from resume_parser.skill_extractor import extract_skills
from resume_parser.scorer import calculate_match_score
from resume_parser.semantic_matcher import semantic_similarity
from resume_parser.profile_extractor import extract_resume_profile, extract_job_profile
from resume_parser.structured_scorer import calculate_structured_score, build_explanation

text = extract_text_from_pdf("uploads/Archit-Mahajan-Resume-info.pdf")
jd = "Python developer with SQL, Flask and machine learning experience"

def step(name, fn):
    t = time.time()
    print(f"-> {name} ...", flush=True)
    try:
        r = fn()
        print(f"   OK in {time.time()-t:.1f}s", flush=True)
        return r
    except Exception:
        print(f"   FAILED in {name}", flush=True)
        traceback.print_exc()
        raise SystemExit

rs = step("extract_skills", lambda: extract_skills(text))
js = step("extract_skills jd", lambda: extract_skills(jd))
step("calculate_match_score", lambda: calculate_match_score(rs, js, jd_text=jd))
step("semantic_similarity", lambda: semantic_similarity(text, jd))
rp = step("extract_resume_profile", lambda: extract_resume_profile(text, return_source=True))
jp = step("extract_job_profile", lambda: extract_job_profile(jd, return_source=True))
print("ALL STEPS OK")