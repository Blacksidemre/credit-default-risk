"""Model pipeline'larını oluşturan ortak bileşenler."""
from __future__ import annotations

from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import CATEGORICAL_FEATURES, ENGINEERED_FEATURES, RANDOM_STATE, RAW_FEATURES
from .data_prep import FeatureEngineer


def _feature_space() -> tuple[list[str], list[str]]:
    all_features = RAW_FEATURES + ENGINEERED_FEATURES
    categorical = CATEGORICAL_FEATURES
    numeric = [c for c in all_features if c not in categorical]
    return numeric, categorical


def build_preprocessor() -> ColumnTransformer:
    """Sayısal ve kategorik alanlar için üretim ortamına uygun preprocessing kurar."""
    numeric_features, categorical_features = _feature_space()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    # LightGBM eğitim ve tahmin aşamalarında aynı kolon isimlerini görsün.
    preprocessor.set_output(transform="pandas")
    return preprocessor


def build_logistic_pipeline() -> Pipeline:
    """Baseline Logistic Regression pipeline'ı."""
    return Pipeline(
        steps=[
            ("feature_engineering", FeatureEngineer()),
            ("preprocess", build_preprocessor()),
            (
                "model",
                LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    solver="liblinear",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def build_lightgbm_pipeline() -> Pipeline:
    """Final LightGBM pipeline'ı."""
    return Pipeline(
        steps=[
            ("feature_engineering", FeatureEngineer()),
            ("preprocess", build_preprocessor()),
            (
                "model",
                LGBMClassifier(
                    objective="binary",
                    n_estimators=450,
                    learning_rate=0.035,
                    num_leaves=31,
                    max_depth=-1,
                    min_child_samples=30,
                    subsample=0.90,
                    colsample_bytree=0.90,
                    reg_alpha=0.10,
                    reg_lambda=0.30,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                    verbosity=-1,
                ),
            ),
        ]
    )


def get_transformed_feature_names(fitted_pipeline: Pipeline) -> list[str]:
    """Eğitilmiş pipeline'ın model tarafında gördüğü feature isimlerini döndürür."""
    preprocessor = fitted_pipeline.named_steps["preprocess"]
    return preprocessor.get_feature_names_out().tolist()
