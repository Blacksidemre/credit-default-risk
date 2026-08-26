# Sonuçlar ve Değerlendirme

## Hold-out Performansı

| Model | ROC-AUC | Average Precision | Recall | F2 | False Negative Rate |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.7378 | 0.4960 | 0.6544 | 0.5808 | 0.3456 |
| LightGBM | 0.7884 | 0.5638 | 0.8486 | 0.6443 | 0.1514 |

LightGBM final model olarak seçilmiştir.

## Eşik

Final threshold: `0.29844278293849474`.

Eşik test seti üzerinde seçilmemiştir. Yalnızca eğitim verisindeki 5-fold out-of-fold tahminler kullanılarak F2 maksimizasyonu yapılmıştır. Böylece iş probleminde kritik olan false negative hatalarının azaltılması hedeflenir.

## Grafikler

- `target_distribution.png`
- `roc_auc_curve.png`
- `precision_recall_curve.png`
- `feature_importance.png`
- `confusion_matrix.png`
- `model_metric_comparison.png`
- `calibration_curve.png`

Tüm sayısal sonuçların kaynak dosyası: `metrics.json`.
