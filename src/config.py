from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "default_of_credit_card_clients.csv"
MODEL_DIR = PROJECT_ROOT / "models"
FINAL_MODEL_PATH = MODEL_DIR / "final_model.pkl"

TARGET_COL = "TARGET"
TEST_SIZE = 0.2
RANDOM_STATE = 42
