"""
AI Answer Evaluator — Team 5
Uses sentence-transformers to compute semantic similarity between
a student answer and the model answer, then maps it to a score.
Model is loaded once (singleton) to avoid slow per-request loading.
"""
from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Singleton model instance ──────────────────────────────────────────
_model = None
MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(MODEL_NAME)
            logger.info("SentenceTransformer loaded: %s", MODEL_NAME)
        except ImportError:
            logger.warning("sentence-transformers not installed. Using fallback evaluator.")
            _model = "fallback"
    return _model


# ── Similarity helpers ────────────────────────────────────────────────

def _cosine_similarity(vec_a, vec_b) -> float:
    import numpy as np
    a, b = np.array(vec_a), np.array(vec_b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0


def _fallback_similarity(student: str, model_ans: str) -> float:
    """Simple word-overlap fallback when sentence-transformers is unavailable."""
    s_words = set(student.lower().split())
    m_words = set(model_ans.lower().split())
    if not m_words:
        return 0.0
    return len(s_words & m_words) / len(m_words)


# ── Score mapping ─────────────────────────────────────────────────────

def _similarity_to_score(similarity: float, max_score: float = 10.0) -> float:
    """Map cosine similarity [0,1] to a score out of max_score."""
    if similarity >= 0.90:
        ratio = 1.0
    elif similarity >= 0.75:
        ratio = 0.85
    elif similarity >= 0.60:
        ratio = 0.70
    elif similarity >= 0.45:
        ratio = 0.50
    elif similarity >= 0.30:
        ratio = 0.30
    else:
        ratio = 0.10
    return round(ratio * max_score, 2)


def _generate_feedback(similarity: float) -> str:
    if similarity >= 0.90:
        return "Excellent answer! Closely matches the model answer."
    elif similarity >= 0.75:
        return "Good answer. Covers most key points."
    elif similarity >= 0.60:
        return "Satisfactory. Some key concepts are present but incomplete."
    elif similarity >= 0.45:
        return "Partial answer. Several important points are missing."
    elif similarity >= 0.30:
        return "Weak answer. Mostly off-topic or very incomplete."
    else:
        return "Answer does not match the expected response."


# ── Public API ────────────────────────────────────────────────────────

def evaluate_answer(student_answer: str, model_answer: str, max_score: float = 10.0) -> dict:
    """
    Evaluate a single student answer against the model answer.
    Returns a dict with: similarity_score, ai_score, final_score, ai_feedback.
    """
    model = _get_model()

    if model == "fallback":
        similarity = _fallback_similarity(student_answer, model_answer)
    else:
        embeddings = model.encode([student_answer, model_answer])
        similarity = _cosine_similarity(embeddings[0], embeddings[1])

    score    = _similarity_to_score(similarity, max_score)
    feedback = _generate_feedback(similarity)

    return {
        "similarity_score": round(similarity, 4),
        "ai_score":         score,
        "final_score":      score,
        "ai_feedback":      feedback,
        "max_score":        max_score,
    }


def batch_evaluate(pairs: list[tuple[str, str]], max_score: float = 10.0) -> list[dict]:
    """Evaluate multiple (student_answer, model_answer) pairs at once."""
    return [evaluate_answer(s, m, max_score) for s, m in pairs]
