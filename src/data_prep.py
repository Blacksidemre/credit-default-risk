import pandas as pd
from .config import RAW_DATA_PATH, TARGET_COL

def load_raw_data(path: str | None = None) -> pd.DataFrame:
    if path is None:
        path = RAW_DATA_PATH
    df = pd.read_csv(path)
    if "default payment next month" in df.columns:
        df = df.rename(columns={"default payment next month": TARGET_COL})
    if "default.payment.next.month" in df.columns:
        df = df.rename(columns={"default.payment.next.month": TARGET_COL})
    if "ID" in df.columns:
        df = df.drop(columns=["ID"])
    return df

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pay_cols = [c for c in df.columns if c.startswith("PAY_AMT")]
    bill_cols = [c for c in df.columns if c.startswith("BILL_AMT")]
    if pay_cols:
        df["PAY_SUM"] = df[pay_cols].sum(axis=1)
        df["LIMIT_PER_PAY"] = df["LIMIT_BAL"] / (df["PAY_SUM"] + 1)
    if bill_cols:
        df["BILL_SUM"] = df[bill_cols].sum(axis=1)
    if "AGE" in df.columns:
        df["AGE_BIN"] = pd.cut(df["AGE"],
                               bins=[0, 30, 40, 50, 60, 120],
                               labels=False,
                               include_lowest=True)
    return df

def get_feature_target(df: pd.DataFrame):
    y = df[TARGET_COL]
    X = df.drop(columns=[TARGET_COL])
    return X, y
