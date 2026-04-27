import logging
from typing import TypedDict

from sentence_transformers import SentenceTransformer, util

from .preprocessing import clean
from .scoring import keyword_score, length_score, combine_scores, calibrate_similarity

logger = logging.getLogger(__name__)

_MODEL_NAME = "all-MiniLM-L6-v2"
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading SentenceTransformer model '%s'...", _MODEL_NAME)
        _model = SentenceTransformer(_MODEL_NAME)
        logger.info("Model loaded.")
    return _model


class EvaluationResult(TypedDict):
    similarity: float
    keyword_score: float
    length_score: float
    final_score: float


def evaluate_answer(student_answer: str, model_answer: str) -> EvaluationResult:
    if not student_answer or not student_answer.strip():
        raise ValueError("student_answer must not be empty.")
    if not model_answer or not model_answer.strip():
        raise ValueError("model_answer must not be empty.")

    student_clean = clean(student_answer)
    model_clean = clean(model_answer)

    model = _get_model()
    embeddings = model.encode([student_clean, model_clean], convert_to_tensor=True)
    raw_sim = max(0.0, float(util.cos_sim(embeddings[0], embeddings[1])))
    similarity = calibrate_similarity(raw_sim)

    kw = keyword_score(student_clean, model_clean)
    ln = length_score(student_clean, model_clean)

    return EvaluationResult(
        similarity=round(similarity, 4),
        keyword_score=round(kw, 4),
        length_score=round(ln, 4),
        final_score=combine_scores(raw_sim, kw, ln),
    )


def batch_evaluate(pairs: list[tuple[str, str]]) -> list[EvaluationResult]:
    if not pairs:
        return []

    model = _get_model()
    cleaned = [(clean(s), clean(m)) for s, m in pairs]
    all_texts = [t for pair in cleaned for t in pair]
    embeddings = model.encode(all_texts, convert_to_tensor=True)

    results: list[EvaluationResult] = []
    for i, (student_clean, model_clean) in enumerate(cleaned):
        s_emb = embeddings[i * 2]
        m_emb = embeddings[i * 2 + 1]
        raw_sim = max(0.0, float(util.cos_sim(s_emb, m_emb)))
        similarity = calibrate_similarity(raw_sim)
        kw = keyword_score(student_clean, model_clean)
        ln = length_score(student_clean, model_clean)
        results.append(EvaluationResult(
            similarity=round(similarity, 4),
            keyword_score=round(kw, 4),
            length_score=round(ln, 4),
            final_score=combine_scores(raw_sim, kw, ln),
        ))

    return results
