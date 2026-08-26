# Final Model Raporu

Proje uçtan uca yeniden çalıştırılmış ve final LightGBM modeli gerçek veri üzerinde üretilmiştir.

## Sonuç Özeti

- Veri: 30.000 müşteri
- Default oranı: %22,12
- Train: 24.000
- Test: 6.000
- LightGBM ROC-AUC: 0.7884
- LightGBM Average Precision: 0.5638
- LightGBM Recall: 0.8486
- LightGBM F2: 0.6443
- LightGBM False Negative Rate: 0.1514
- Final threshold: 0.2984427829

## Üretim Artifact'ları

- `models/final_model.pkl`
- `docs/metrics.json`
- `docs/target_distribution.png`
- `docs/roc_auc_curve.png`
- `docs/precision_recall_curve.png`
- `docs/feature_importance.png`
- `docs/confusion_matrix.png`
- `docs/model_metric_comparison.png`
- `docs/calibration_curve.png`

API, ham 23 alanı alır ve feature engineering dahil tüm preprocessing'i model pipeline'ı içinde uygular.
