"""Proje görsellerini üreten ve otomatik docs/ klasörüne kaydeden fonksiyonlar."""
from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    auc,
    precision_recall_curve,
    roc_curve,
)

from .config import DOCS_DIR

sns.set_theme(style="whitegrid", context="notebook")


def _output_path(filename: str, output_dir: str | Path = DOCS_DIR) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / filename


def save_target_distribution(y: Sequence[int], output_dir: str | Path = DOCS_DIR) -> Path:
    """Hedef sınıf dağılımını seaborn countplot ile kaydeder."""
    path = _output_path("target_distribution.png", output_dir)
    plot_df = pd.DataFrame({"TARGET": np.asarray(y, dtype=int)})
    plt.figure(figsize=(7, 5))
    ax = sns.countplot(data=plot_df, x="TARGET", hue="TARGET", legend=False, palette="Set2")
    ax.set_title("Hedef Değişken Sınıf Dağılımı")
    ax.set_xlabel("Temerrüt (0=Hayır, 1=Evet)")
    ax.set_ylabel("Müşteri Sayısı")
    total = len(plot_df)
    for patch in ax.patches:
        height = patch.get_height()
        ax.annotate(
            f"{int(height):,}\n({height / total:.1%})",
            (patch.get_x() + patch.get_width() / 2, height),
            ha="center",
            va="bottom",
            fontsize=10,
        )
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return path


def save_roc_curves(
    y_true: Sequence[int],
    probabilities: Mapping[str, Sequence[float]],
    output_dir: str | Path = DOCS_DIR,
) -> Path:
    """Bir veya birden fazla modelin ROC-AUC eğrilerini kaydeder."""
    path = _output_path("roc_auc_curve.png", output_dir)
    plt.figure(figsize=(8, 6))
    for model_name, y_prob in probabilities.items():
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, linewidth=2, label=f"{model_name} (AUC={roc_auc:.3f})")
    plt.plot([0, 1], [0, 1], linestyle="--", linewidth=1.5, label="Rastgele")
    plt.title("ROC-AUC Eğrileri")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return path


def save_precision_recall_curves(
    y_true: Sequence[int],
    probabilities: Mapping[str, Sequence[float]],
    output_dir: str | Path = DOCS_DIR,
) -> Path:
    """Precision-Recall eğrilerini kaydeder."""
    path = _output_path("precision_recall_curve.png", output_dir)
    plt.figure(figsize=(8, 6))
    prevalence = float(np.mean(y_true))
    for model_name, y_prob in probabilities.items():
        precision, recall, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = auc(recall, precision)
        plt.plot(recall, precision, linewidth=2, label=f"{model_name} (AUC={pr_auc:.3f})")
    plt.axhline(prevalence, linestyle="--", linewidth=1.5, label=f"Pozitif oranı={prevalence:.3f}")
    plt.title("Precision-Recall Eğrileri")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return path


def save_feature_importance(
    feature_names: Sequence[str],
    importances: Sequence[float],
    output_dir: str | Path = DOCS_DIR,
    top_n: int = 25,
) -> Path:
    """LightGBM feature importance değerlerini yatay çubuk grafik olarak kaydeder."""
    path = _output_path("feature_importance.png", output_dir)
    importance_df = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .head(top_n)
        .sort_values("importance", ascending=True)
    )
    plt.figure(figsize=(10, 8))
    sns.barplot(data=importance_df, x="importance", y="feature", orient="h", hue="feature", legend=False, palette="viridis")
    plt.title(f"LightGBM Feature Importance - İlk {min(top_n, len(importance_df))}")
    plt.xlabel("Önem Skoru")
    plt.ylabel("Özellik")
    plt.tight_layout()
    plt.savefig(path, dpi=170, bbox_inches="tight")
    plt.close()
    return path


def save_confusion_matrix(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    output_dir: str | Path = DOCS_DIR,
) -> Path:
    """Final model confusion matrix grafiğini kaydeder."""
    path = _output_path("confusion_matrix.png", output_dir)
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_true,
        y_pred,
        display_labels=["Non-default", "Default"],
        cmap="Blues",
        values_format="d",
        ax=ax,
    )
    ax.set_title("LightGBM Confusion Matrix")
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


def save_metric_comparison(
    model_metrics: Mapping[str, Mapping[str, float]],
    output_dir: str | Path = DOCS_DIR,
) -> Path:
    """Ana sınıflandırma metriklerini modeller arasında karşılaştırır."""
    path = _output_path("model_metric_comparison.png", output_dir)
    selected = ["roc_auc", "average_precision", "precision", "recall", "f1", "f2"]
    rows = []
    for model_name, metrics in model_metrics.items():
        for metric in selected:
            rows.append({"model": model_name, "metric": metric, "score": metrics[metric]})
    metric_df = pd.DataFrame(rows)
    plt.figure(figsize=(11, 6))
    sns.barplot(data=metric_df, x="metric", y="score", hue="model")
    plt.ylim(0, 1)
    plt.title("Model Metrik Karşılaştırması")
    plt.xlabel("Metrik")
    plt.ylabel("Skor")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return path


def save_calibration_curve(
    y_true: Sequence[int],
    probabilities: Mapping[str, Sequence[float]],
    output_dir: str | Path = DOCS_DIR,
) -> Path:
    """Tahmin olasılıklarının kalibrasyonunu görselleştirir."""
    path = _output_path("calibration_curve.png", output_dir)
    plt.figure(figsize=(7, 6))
    for model_name, y_prob in probabilities.items():
        frac_pos, mean_pred = calibration_curve(y_true, y_prob, n_bins=10, strategy="quantile")
        plt.plot(mean_pred, frac_pos, marker="o", label=model_name)
    plt.plot([0, 1], [0, 1], linestyle="--", label="Mükemmel kalibrasyon")
    plt.title("Olasılık Kalibrasyon Eğrisi")
    plt.xlabel("Ortalama Tahmin Olasılığı")
    plt.ylabel("Gerçek Pozitif Oranı")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return path
