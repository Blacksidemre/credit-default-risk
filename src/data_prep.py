"""Veri okuma, temizleme, özellik mühendisliği ve stratified bölme yardımcıları."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import StratifiedKFold

from .config import (
    ID_COL,
    N_SPLITS,
    RANDOM_STATE,
    RAW_DATA_PATH,
    RAW_FEATURES,
    TARGET_COL,
)

TARGET_ALIASES = (
    "default payment next month",
    "default.payment.next.month",
    "default_payment_next_month",
    "target",
)


def _resolve_data_path(path: str | Path | None = None) -> Path:
    """Veri dosyasını hem standart data/raw yolunda hem verilen yolda güvenli biçimde çözer."""
    candidate = Path(path) if path is not None else RAW_DATA_PATH
    if candidate.exists():
        return candidate

    # Repo köküne doğrudan konmuş veri dosyası için geriye dönük uyumluluk.
    root_candidate = RAW_DATA_PATH.parents[2] / "default_of_credit_card_clients.csv"
    if root_candidate.exists():
        return root_candidate

    raise FileNotFoundError(
        f"Veri dosyası bulunamadı: {candidate}. "
        "Beklenen konum: data/raw/default_of_credit_card_clients.csv"
    )


def load_raw_data(path: str | Path | None = None) -> pd.DataFrame:
    """UCI kredi kartı veri setini okur ve hedef kolonunu standartlaştırır."""
    data_path = _resolve_data_path(path)
    df = pd.read_csv(data_path)

    rename_map: dict[str, str] = {}
    for col in df.columns:
        if col.strip().lower() in {alias.lower() for alias in TARGET_ALIASES}:
            rename_map[col] = TARGET_COL
    df = df.rename(columns=rename_map)

    if TARGET_COL not in df.columns:
        raise ValueError(
            f"Hedef kolon bulunamadı. Desteklenen adlar: {TARGET_ALIASES}"
        )
    return df


def clean_data(df: pd.DataFrame, require_target: bool = True) -> pd.DataFrame:
    """Kolonları doğrular, ID'yi kaldırır ve UCI kategori kodlarını normalize eder."""
    cleaned = df.copy()

    # Hedef adı farklı geldiyse standardize et.
    for col in list(cleaned.columns):
        if col.strip().lower() in {alias.lower() for alias in TARGET_ALIASES}:
            cleaned = cleaned.rename(columns={col: TARGET_COL})

    if ID_COL in cleaned.columns:
        cleaned = cleaned.drop(columns=[ID_COL])

    missing = [c for c in RAW_FEATURES if c not in cleaned.columns]
    if missing:
        raise ValueError(f"Eksik girdi kolonları: {missing}")
    if require_target and TARGET_COL not in cleaned.columns:
        raise ValueError(f"'{TARGET_COL}' hedef kolonu bulunamadı.")

    numeric_cols = RAW_FEATURES + ([TARGET_COL] if TARGET_COL in cleaned.columns else [])
    for col in numeric_cols:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    # UCI veri setindeki EDUCATION 0/5/6 kodları 'other' (4) altında birleştirilir.
    cleaned["EDUCATION"] = cleaned["EDUCATION"].replace({0: 4, 5: 4, 6: 4})
    # MARRIAGE=0 tanımsız değeri 'other' (3) olarak normalize edilir.
    cleaned["MARRIAGE"] = cleaned["MARRIAGE"].replace({0: 3})

    if TARGET_COL in cleaned.columns:
        valid_target = cleaned[TARGET_COL].dropna().isin([0, 1]).all()
        if not valid_target:
            raise ValueError("TARGET yalnızca 0 ve 1 değerlerini içermelidir.")
        cleaned[TARGET_COL] = cleaned[TARGET_COL].astype(int)

    return cleaned


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Domain bilgisine dayalı dört yeni özellik üretir."""
    featured = df.copy()
    pay_cols = [f"PAY_AMT{i}" for i in range(1, 7)]
    bill_cols = [f"BILL_AMT{i}" for i in range(1, 7)]

    featured["PAY_SUM"] = featured[pay_cols].sum(axis=1, min_count=1)
    featured["BILL_SUM"] = featured[bill_cols].sum(axis=1, min_count=1)

    # Sıfıra bölmeyi önlemek için ödeme toplamı 0 ise paydayı 1 kabul ediyoruz.
    safe_pay_sum = featured["PAY_SUM"].replace(0, 1.0)
    featured["LIMIT_PER_PAY"] = featured["LIMIT_BAL"] / safe_pay_sum
    featured["LIMIT_PER_PAY"] = featured["LIMIT_PER_PAY"].replace([np.inf, -np.inf], np.nan)

    # Yaş aralıkları: <=30, 31-40, 41-50, 51-60, 60+
    featured["AGE_BIN"] = pd.cut(
        featured["AGE"],
        bins=[-np.inf, 30, 40, 50, 60, np.inf],
        labels=["<=30", "31-40", "41-50", "51-60", "60+"],
        include_lowest=True,
    )
    return featured


def get_feature_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Ham özellik matrisi ile hedefi ayırır."""
    if TARGET_COL not in df.columns:
        raise ValueError(f"'{TARGET_COL}' kolonu bulunamadı.")
    X = df[RAW_FEATURES].copy()
    y = df[TARGET_COL].astype(int).copy()
    return X, y


def stratified_train_test_split(
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = N_SPLITS,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    StratifiedKFold'un ilk fold'unu hold-out test kümesi olarak kullanır.

    N_SPLITS=5 olduğunda yaklaşık %80 eğitim / %20 test ayrımı elde edilir ve
    hedef sınıf oranları iki kümede de korunur.
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    train_idx, test_idx = next(skf.split(X, y))
    return (
        X.iloc[train_idx].reset_index(drop=True),
        X.iloc[test_idx].reset_index(drop=True),
        y.iloc[train_idx].reset_index(drop=True),
        y.iloc[test_idx].reset_index(drop=True),
    )


def iter_stratified_folds(
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = N_SPLITS,
    random_state: int = RANDOM_STATE,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """Tekrarlanabilir StratifiedKFold indekslerini üretir."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    yield from skf.split(X, y)


class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Feature engineering'i sklearn Pipeline içine taşıyan transformer."""

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None) -> "FeatureEngineer":
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=RAW_FEATURES)
        cleaned = clean_data(X, require_target=False)
        return add_features(cleaned)
