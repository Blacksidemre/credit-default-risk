"""Logistic Regression + LightGBM eğitim, değerlendirme, görselleştirme ve model kaydetme akışı."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import joblib
import numpy as np
from sklearn.base import clone
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from .config import (
    DOCS_DIR,
    FINAL_MODEL_PATH,
    METRICS_PATH,
    N_SPLITS,
    RANDOM_STATE,
    RAW_FEATURES,
)
from .data_prep import clean_data, get_feature_target, load_raw_data, stratified_train_test_split
from .pipeline import build_lightgbm_pipeline, build_logistic_pipeline, get_transformed_feature_names
from .visualization import (
    save_calibration_curve,
    save_confusion_matrix,
    save_feature_importance,
    save_metric_comparison,
    save_precision_recall_curves,
    save_roc_curves,
    save_target_distribution,
)


def find_f2_threshold(y_true, y_prob) -> float:
    """Yanlış negatif maliyetini öne çıkarmak için F2 skorunu maksimize eden eşik değerini bulur."""
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    if thresholds.size == 0:
        return 0.5
    beta_sq = 4.0
    f2 = (1 + beta_sq) * precision[:-1] * recall[:-1] / (
        beta_sq * precision[:-1] + recall[:-1] + 1e-12
    )
    return float(thresholds[int(np.nanargmax(f2))])


def evaluate_model(y_true, y_prob, threshold: float) -> dict[str, float | int]:
    """İş problemi için önemli binary classification metriklerini hesaplar."""
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "threshold": float(threshold),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "average_precision": float(average_precision_score(y_true, y_prob)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "f2": float(fbeta_score(y_true, y_pred, beta=2, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if (tn + fp) else 0.0,
        "false_negative_rate": float(fn / (fn + tp)) if (fn + tp) else 0.0,
        "brier_score": float(brier_score_loss(y_true, y_prob)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def main() -> dict:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_df = load_raw_data()
    df = clean_data(raw_df, require_target=True)
    X, y = get_feature_target(df)
    X_train, X_test, y_train, y_test = stratified_train_test_split(X, y)

    save_target_distribution(y)

    logistic = build_logistic_pipeline()
    lightgbm = build_lightgbm_pipeline()

    print("[1/5] Logistic Regression eğitiliyor...")
    logistic.fit(X_train, y_train)
    log_prob = logistic.predict_proba(X_test)[:, 1]
    log_metrics = evaluate_model(y_test, log_prob, threshold=0.5)

    print("[2/5] LightGBM için out-of-fold threshold optimizasyonu yapılıyor...")
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    oof_prob = cross_val_predict(
        clone(lightgbm),
        X_train,
        y_train,
        cv=cv,
        method="predict_proba",
        n_jobs=1,
    )[:, 1]
    threshold = find_f2_threshold(y_train, oof_prob)

    print(f"[3/5] LightGBM eğitiliyor (seçilen threshold={threshold:.4f})...")
    lightgbm.fit(X_train, y_train)
    lgb_prob = lightgbm.predict_proba(X_test)[:, 1]
    lgb_metrics = evaluate_model(y_test, lgb_prob, threshold=threshold)
    lgb_pred = (lgb_prob >= threshold).astype(int)

    probability_map = {
        "Logistic Regression": log_prob,
        "LightGBM": lgb_prob,
    }
    metric_map = {
        "Logistic Regression": log_metrics,
        "LightGBM": lgb_metrics,
    }

    print("[4/5] Grafikler oluşturuluyor...")
    save_roc_curves(y_test, probability_map)
    save_precision_recall_curves(y_test, probability_map)
    save_confusion_matrix(y_test, lgb_pred)
    save_metric_comparison(metric_map)
    save_calibration_curve(y_test, probability_map)

    feature_names = get_transformed_feature_names(lightgbm)
    importances = lightgbm.named_steps["model"].feature_importances_
    save_feature_importance(feature_names, importances)

    # Deployment modeli tüm veri üzerinde yeniden eğitilir; test metrikleri yukarıdaki hold-out'tan gelir.
    print("[5/5] Final model tüm veri ile yeniden eğitilip kaydediliyor...")
    final_pipeline = clone(lightgbm)
    final_pipeline.fit(X, y)

    bundle = {
        "pipeline": final_pipeline,
        "threshold": threshold,
        "raw_features": RAW_FEATURES,
        "model_name": "LightGBM",
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "sklearn_artifact_version": 1,
    }
    joblib.dump(bundle, FINAL_MODEL_PATH)

    report = {
        "dataset": {
            "rows": int(len(df)),
            "features": int(len(RAW_FEATURES)),
            "default_rate": float(y.mean()),
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
            "validation": f"StratifiedKFold first hold-out fold, n_splits={N_SPLITS}",
        },
        "models": metric_map,
        "final_model": {
            "name": "LightGBM",
            "threshold_strategy": "5-fold out-of-fold F2 maximization on training split",
            "threshold": threshold,
            "artifact": str(FINAL_MODEL_PATH.relative_to(FINAL_MODEL_PATH.parents[1])),
        },
    }
    METRICS_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    main()
