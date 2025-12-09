import joblib
import pandas as pd
from .config import FINAL_MODEL_PATH

_model = None

def load_model(path=None):
    global _model
    if _model is None:
        if path is None:
            path = FINAL_MODEL_PATH
        _model = joblib.load(path)
    return _model

def predict_proba_df(df: pd.DataFrame):
    model = load_model()
    return model.predict_proba(df)[:, 1]

def predict_single(features: dict):
    df = pd.DataFrame([features])
    return float(predict_proba_df(df)[0])
