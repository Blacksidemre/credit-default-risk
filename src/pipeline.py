from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from lightgbm import LGBMClassifier
import joblib

from .config import TEST_SIZE, RANDOM_STATE, FINAL_MODEL_PATH
from .data_prep import load_raw_data, add_features, get_feature_target

def build_preprocessor(feature_names):
    num_cols = feature_names
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    pre = ColumnTransformer(
        transformers=[("num", numeric, num_cols)],
        remainder="drop",
    )
    return pre

def train_baseline():
    df = load_raw_data()
    df = add_features(df)
    X, y = get_feature_target(df)
    pre = build_preprocessor(X.columns.tolist())
    model = LogisticRegression(max_iter=2000)
    pipe = Pipeline([("prep", pre), ("model", model)])
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    pipe.fit(X_train, y_train)
    preds = pipe.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)
    return pipe, auc

def train_lgbm_with_features(save: bool = True):
    df = load_raw_data()
    df = add_features(df)
    X, y = get_feature_target(df)
    pre = build_preprocessor(X.columns.tolist())
    lgbm = LGBMClassifier(
        random_state=RANDOM_STATE,
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=50,
        subsample=0.9,
    )
    pipe = Pipeline([("prep", pre), ("model", lgbm)])
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    pipe.fit(X_train, y_train)
    preds = pipe.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)
    if save:
        FINAL_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipe, FINAL_MODEL_PATH)
    return pipe, auc
