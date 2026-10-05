"""Local semantic similarity for resume/JD matching."""

from functools import lru_cache


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def semantic_similarity(resume_text, jd_text):
    """Return cosine similarity as a 0-100 percentage.

    The model is loaded lazily so the Flask app can still start when the
    embedding dependency/model is unavailable.
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    model = _load_model()
    embeddings = model.encode(
        [resume_text, jd_text],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    similarity = float(embeddings[0] @ embeddings[1])
    return round(max(0.0, min(1.0, similarity)) * 100, 2)
