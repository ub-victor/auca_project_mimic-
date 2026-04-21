_STOPWORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "of", "and",
    "or", "but", "for", "with", "as", "by", "from", "that", "this",
    "are", "was", "were", "be", "been", "has", "have", "had", "do",
    "does", "did", "will", "would", "can", "could", "may", "might",
    "its", "their", "they", "we", "you", "he", "she", "i", "not",
}

# Suffixes to strip for lightweight stemming (order matters — longest first)
_SUFFIXES = ("tion", "tions", "ing", "ings", "tion", "ed", "er", "ers",
             "ment", "ments", "ity", "ies", "ness", "al", "ly", "es", "s")


def _stem(word: str) -> str:
    """Strip common suffixes so storage/stores/stored all reduce to stor."""
    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _keywords(text: str) -> set[str]:
    """Return stemmed, stopword-filtered keywords from cleaned text."""
    return {
        _stem(w)
        for w in text.split()
        if w not in _STOPWORDS and len(w) > 2
    }


def keyword_score(student_clean: str, model_clean: str) -> float:
    """
    Fraction of stemmed model keywords found in the student answer (0–1).
    Uses suffix stemming so paraphrased answers aren't unfairly penalised.
    """
    model_kw = _keywords(model_clean)
    if not model_kw:
        return 1.0
    student_kw = _keywords(student_clean)
    return len(model_kw & student_kw) / len(model_kw)


def length_score(student_clean: str, model_clean: str) -> float:
    """
    Soft length score (0–1).
    - Acceptable window: 30 %–200 % of model length (concise answers are fine)
    - Below 30 %: linear penalty down to 0
    - Above 200 %: very gentle penalty, floored at 0.5 (verbosity ≠ wrong)
    """
    model_len = len(model_clean.split())
    if model_len == 0:
        return 1.0
    student_len = len(student_clean.split())
    if student_len == 0:
        return 0.0
    ratio = student_len / model_len
    if ratio < 0.3:
        # Too short — scale linearly from 0 to 1 across 0–0.3
        return ratio / 0.3
    elif ratio <= 2.0:
        # Acceptable range — full marks
        return 1.0
    else:
        # Too verbose — gentle penalty, never below 0.5
        return max(0.5, 1.0 - (ratio - 2.0) * 0.1)


def calibrate_similarity(raw: float) -> float:
    """
    Stretch cosine similarity to use the full 0–1 range.
    all-MiniLM-L6-v2 rarely goes below ~0.2 even for unrelated sentences,
    so we subtract a baseline of 0.20 and rescale to [0, 1].
    Completely wrong answers now score near 0 instead of ~0.5.
    """
    baseline = 0.20
    calibrated = (raw - baseline) / (1.0 - baseline)
    return max(0.0, min(1.0, calibrated))


def combine_scores(semantic: float, kw: float, length: float) -> float:
    """
    Weighted combination scaled to 0–10.

    Weights (must sum to 1.0):
      - semantic  0.60  — meaning matters most
      - keyword   0.30  — technical terminology coverage
      - length    0.10  — completeness signal, not a proxy for quality

    Semantic is calibrated first to remove the artificial floor.
    """
    cal_semantic = calibrate_similarity(semantic)
    raw = (0.60 * cal_semantic) + (0.30 * kw) + (0.10 * length)
    return round(raw * 10, 2)
