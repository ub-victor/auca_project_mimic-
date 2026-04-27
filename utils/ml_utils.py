import pickle
from pathlib import Path

ML_MODELS_DIR = Path(__file__).resolve().parent.parent / 'ml_models'


def load_model(filename):
    model_path = ML_MODELS_DIR / filename
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    with open(model_path, 'rb') as f:
        return pickle.load(f)


def get_evaluator():
    return load_model('answer_evaluator.pkl')


def get_vectorizer():
    return load_model('vectorizer.pkl')
