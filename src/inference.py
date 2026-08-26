"""Kaydedilmiş model artifact'ı ile tekli ve batch inference fonksiyonları."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import joblib
import pandas as pd

from .config import FINAL_MODEL_PATH, RAW_FEATURES

_model_bundle: dict[str, Any] | None = None


def load_model(path: str | Path | None = None, force_reload: bool = False) -> dict[str, Any]:
    """Model bundle'ını tek kez belleğe yükler."""
    global _model_bundle
    model_path = Path(path) if path is not None else FINAL_MODEL_PATH
    if force_reload or _model_bundle is None:
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model bulunamadı: {model_path}. Önce `python -m src.train` çalıştırın."
            )
        loaded = joblib.load(model_path)
        # Eski sürümde yalnızca pipeline kaydedilmişse geriye dönük destek.
        if isinstance(loaded, dict) and "pipeline" in loaded:
            _model_bundle = loaded
        else:
            _model_bundle = {
                "pipeline": loaded,
                "threshold": 0.5,
                "raw_features": RAW_FEATURES,
                "model_name": "LightGBM",
            }
    return _model_bundle


def _to_frame(records: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(records)
    missing = [col for col in RAW_FEATURES if col not in frame.columns]
    if missing:
        raise ValueError(f"Eksik özellikler: {missing}")
    return frame[RAW_FEATURES].copy()


def predict_batch(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Birden çok ham müşteri kaydı için olasılık ve sınıf tahmini üretir."""
    if not records:
        return []
    bundle = load_model()
    pipeline = bundle["pipeline"]
    threshold = float(bundle.get("threshold", 0.5))
    frame = _to_frame(records)
    probabilities = pipeline.predict_proba(frame)[:, 1]
    return [
        {
            "default_probability": float(prob),
            "prediction": int(prob >= threshold),
            "threshold": threshold,
            "risk_label": "high" if prob >= threshold else "low",
        }
        for prob in probabilities
    ]


def predict_single(features: Mapping[str, Any]) -> dict[str, Any]:
    """Tek müşteri için tahmin üretir."""
    return predict_batch([features])[0]


def predict_proba_df(df: pd.DataFrame):
    """DataFrame kullanan geriye dönük uyumlu olasılık tahmin fonksiyonu."""
    bundle = load_model()
    return bundle["pipeline"].predict_proba(df[RAW_FEATURES])[:, 1]
