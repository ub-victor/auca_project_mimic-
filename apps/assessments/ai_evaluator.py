"""
AI answer evaluator for assessments.
This module loads the sentence-transformers model once and exposes a simple
evaluation interface for submission scoring and feedback.
"""
import logging
from typing import List, Tuple

from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

_MODEL = None
_MODEL_NAME = 'all-MiniLM-L6-v2'


class AnswerEvaluator:
    def __init__(self, model_name: str = _MODEL_NAME):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        logger.info('Loaded SentenceTransformer model: %s', model_name)

    def encode(self, text: str):
        return self.model.encode(text, convert_to_tensor=True, normalize_embeddings=True)

    def _score_similarity(self, student_text: str, reference_text: str) -> float:
        student_embedding = self.encode(student_text)
        reference_embedding = self.encode(reference_text)
        similarity = float(util.pytorch_cos_sim(student_embedding, reference_embedding).item())
        return max(0.0, min(1.0, similarity))

    def _compose_feedback(self, similarity: float) -> str:
        if similarity >= 0.85:
            return 'Excellent alignment to the reference answer. The response is clear and on-topic.'
        if similarity >= 0.70:
            return 'Good alignment. The answer is relevant but can be refined with more detail.'
        if similarity >= 0.50:
            return 'Partial alignment. Add more supporting details and close the gaps to the reference.'
        return 'Low alignment. Review the question guidance and include more of the expected concepts.'

    def evaluate_answer(self, student_answer: str, reference_answer: str) -> dict:
        student_text = (student_answer or '').strip()
        ref_text = (reference_answer or '').strip()

        if not student_text or not ref_text:
            return {
                'similarity_score': 0.0,
                'ai_score': 0.0,
                'ai_feedback': 'Missing student answer or reference text for evaluation.',
            }

        similarity = self._score_similarity(student_text, ref_text)
        ai_score = round(similarity * 100, 2)
        return {
            'similarity_score': round(similarity, 4),
            'ai_score': ai_score,
            'ai_feedback': self._compose_feedback(similarity),
        }

    def batch_evaluate(self, pairs: List[Tuple[str, str]]) -> List[dict]:
        results = []
        for student_answer, reference_answer in pairs:
            results.append(self.evaluate_answer(student_answer, reference_answer))
        return results


def get_evaluator() -> AnswerEvaluator:
    global _MODEL
    if _MODEL is None:
        _MODEL = AnswerEvaluator()
    return _MODEL


def evaluate_answer(student_answer: str, reference_answer: str) -> dict:
    return get_evaluator().evaluate_answer(student_answer, reference_answer)


def batch_evaluate(pairs: List[Tuple[str, str]]) -> List[dict]:
    return get_evaluator().batch_evaluate(pairs)
