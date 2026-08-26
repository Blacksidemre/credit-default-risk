"""Proje genelinde kullanılan sabitler ve dosya yolları."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "default_of_credit_card_clients.csv"
DOCS_DIR = PROJECT_ROOT / "docs"
MODEL_DIR = PROJECT_ROOT / "models"
FINAL_MODEL_PATH = MODEL_DIR / "final_model.pkl"
METRICS_PATH = DOCS_DIR / "metrics.json"

TARGET_COL = "TARGET"
ID_COL = "ID"
RANDOM_STATE = 42
TEST_SIZE = 0.20
N_SPLITS = 5

RAW_FEATURES = [
    "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE",
    "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
    "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
    "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
]

ENGINEERED_FEATURES = ["PAY_SUM", "BILL_SUM", "LIMIT_PER_PAY", "AGE_BIN"]
CATEGORICAL_FEATURES = ["SEX", "EDUCATION", "MARRIAGE", "AGE_BIN"]
