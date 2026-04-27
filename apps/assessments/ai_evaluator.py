"""
AI Answer Evaluator — Team 5 (Valentin NGANUCYE-SINGIZWA)
Core ML module for the AUCA Automated Student Answer Evaluation System.

Features:
- Semantic similarity scoring using sentence-transformers
- Cheating detection: compares student answers against each other
- Batch evaluation
- Fallback word-overlap when sentence-transformers unavailable
"""
from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

_model = None
MODEL_NAME = "all-MiniLM-L6-v2"
CHEATING_THRESHOLD = 0.92  # Similarity above this = probable cheating


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(MODEL_NAME)
            logger.info("SentenceTransformer loaded: %s", MODEL_NAME)
        except ImportError:
            logger.warning("sentence-transformers not installed. Using fallback.")
            _model = "fallback"
    return _model


def _cosine_similarity(vec_a, vec_b) -> float:
    import numpy as np
    a, b = np.array(vec_a), np.array(vec_b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0


def _fallback_similarity(s1: str, s2: str) -> float:
    w1 = set(s1.lower().split())
    w2 = set(s2.lower().split())
    if not w2:
        return 0.0
    return len(w1 & w2) / len(w2)


def _similarity_to_score(similarity: float, max_score: float = 10.0) -> float:
    if similarity >= 0.90:   ratio = 1.0
    elif similarity >= 0.75: ratio = 0.85
    elif similarity >= 0.60: ratio = 0.70
    elif similarity >= 0.45: ratio = 0.50
    elif similarity >= 0.30: ratio = 0.30
    else:                    ratio = 0.10
    return round(ratio * max_score, 2)


def _generate_feedback(similarity: float) -> str:
    if similarity >= 0.90:   return "Excellent answer! Closely matches the model answer."
    elif similarity >= 0.75: return "Good answer. Covers most key points."
    elif similarity >= 0.60: return "Satisfactory. Some key concepts present but incomplete."
    elif similarity >= 0.45: return "Partial answer. Several important points missing."
    elif similarity >= 0.30: return "Weak answer. Mostly off-topic or very incomplete."
    else:                    return "Answer does not match the expected response."


def _encode(texts: list[str]):
    """Encode texts using the model."""
    model = _get_model()
    if model == "fallback":
        return None
    return model.encode(texts)


# ── Public API ────────────────────────────────────────────────────────

def evaluate_answer(student_answer: str, model_answer: str, max_score: float = 10.0) -> dict:
    """Evaluate a single student answer against the model answer."""
    model = _get_model()
    if model == "fallback":
        similarity = _fallback_similarity(student_answer, model_answer)
    else:
        embeddings = model.encode([student_answer, model_answer])
        similarity = _cosine_similarity(embeddings[0], embeddings[1])

    return {
        "similarity_score": round(similarity, 4),
        "ai_score":         _similarity_to_score(similarity, max_score),
        "final_score":      _similarity_to_score(similarity, max_score),
        "ai_feedback":      _generate_feedback(similarity),
        "max_score":        max_score,
    }


def batch_evaluate(pairs: list[tuple[str, str]], max_score: float = 10.0) -> list[dict]:
    """Evaluate multiple (student_answer, model_answer) pairs."""
    return [evaluate_answer(s, m, max_score) for s, m in pairs]


def detect_cheating(question_id: int) -> list[dict]:
    """
    Compare all student answers for a question against each other.
    Returns list of suspected cheating pairs with similarity scores.
    This is the core ML cheating detection feature.
    """
    from apps.assessments.models import Answer

    answers = list(Answer.objects.filter(
        question_id=question_id,
        answer_text__isnull=False
    ).exclude(answer_text='').select_related('student'))

    if len(answers) < 2:
        return []

    model = _get_model()
    suspects = []

    if model != "fallback":
        # Encode all answers at once (efficient batch encoding)
        texts = [a.answer_text for a in answers]
        try:
            embeddings = model.encode(texts)
        except Exception as e:
            logger.error("Encoding failed: %s", e)
            return []

        for i in range(len(answers)):
            for j in range(i + 1, len(answers)):
                sim = _cosine_similarity(embeddings[i], embeddings[j])
                if sim >= CHEATING_THRESHOLD:
                    suspects.append({
                        'student_a':    answers[i].student,
                        'student_b':    answers[j].student,
                        'similarity':   round(sim, 4),
                        'question_id':  question_id,
                        'answer_a_id':  answers[i].pk,
                        'answer_b_id':  answers[j].pk,
                        'risk_level':   'HIGH' if sim >= 0.97 else 'MEDIUM',
                    })
    else:
        # Fallback word-overlap cheating detection
        for i in range(len(answers)):
            for j in range(i + 1, len(answers)):
                sim = _fallback_similarity(answers[i].answer_text, answers[j].answer_text)
                if sim >= 0.85:
                    suspects.append({
                        'student_a':   answers[i].student,
                        'student_b':   answers[j].student,
                        'similarity':  round(sim, 4),
                        'question_id': question_id,
                        'answer_a_id': answers[i].pk,
                        'answer_b_id': answers[j].pk,
                        'risk_level':  'HIGH' if sim >= 0.95 else 'MEDIUM',
                    })

    return sorted(suspects, key=lambda x: x['similarity'], reverse=True)


def detect_cheating_for_assessment(assessment_id: int) -> list[dict]:
    """Run cheating detection across all questions in an assessment."""
    from apps.assessments.models import Question

    questions = Question.objects.filter(assessment_id=assessment_id)
    all_suspects = []
    for q in questions:
        suspects = detect_cheating(q.pk)
        for s in suspects:
            s['question_text'] = q.question_text[:80]
        all_suspects.extend(suspects)
    return all_suspects
