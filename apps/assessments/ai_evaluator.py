"""
Thin wrapper so the rest of the assessments app imports from here,
keeping the ML package decoupled from Django internals.
"""
from ml_model import evaluate_answer, batch_evaluate  # noqa: F401
