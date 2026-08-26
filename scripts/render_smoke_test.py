"""Render build aşamasında model artifact ve inference zincirini doğrular."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.inference import load_model, predict_single

SAMPLE = {
    "LIMIT_BAL": 200000,
    "SEX": 2,
    "EDUCATION": 2,
    "MARRIAGE": 1,
    "AGE": 35,
    "PAY_0": 0,
    "PAY_2": 0,
    "PAY_3": 0,
    "PAY_4": 0,
    "PAY_5": 0,
    "PAY_6": 0,
    "BILL_AMT1": 50000,
    "BILL_AMT2": 48000,
    "BILL_AMT3": 47000,
    "BILL_AMT4": 45000,
    "BILL_AMT5": 43000,
    "BILL_AMT6": 42000,
    "PAY_AMT1": 5000,
    "PAY_AMT2": 5000,
    "PAY_AMT3": 5000,
    "PAY_AMT4": 5000,
    "PAY_AMT5": 5000,
    "PAY_AMT6": 5000,
}


def main() -> None:
    bundle = load_model(force_reload=True)
    result = predict_single(SAMPLE)
    probability = float(result["default_probability"])
    if not 0.0 <= probability <= 1.0:
        raise RuntimeError(f"Geçersiz olasılık üretildi: {probability}")
    print(
        "Render smoke test OK | "
        f"model={bundle.get('model_name', 'unknown')} | "
        f"threshold={float(bundle.get('threshold', 0.5)):.6f} | "
        f"probability={probability:.6f}"
    )


if __name__ == "__main__":
    main()
