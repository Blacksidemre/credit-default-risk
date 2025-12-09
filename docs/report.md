# Kredi Kartı Default Risk Tahmin Projesi

Bu proje, UCI *Default of Credit Card Clients* veri seti üzerinde kredi kartı müşterilerinin bir sonraki ay temerrüde düşme olasılığını tahmin etmek için geliştirilmiştir.

## Problem Tanımı

Amaç, kredi kartı müşterilerinin bir sonraki ay ödemede temerrüde düşüp düşmeyeceğini (`TARGET` = 1) tahmin etmektir. Bu sayede banka, riski yüksek müşteriler için limit azaltma, ek teminat isteme veya kampanya kısıtlama gibi aksiyonlar alabilir.

## Özet

- Sektör: Bankacılık / Kredi riski
- Veri seti: ~30.000 müşteri
- Hedef değişken: `TARGET` (1 = default, 0 = normal ödeme)
- Eğitim / test ayrımı: %80 / %20 (stratified)
- Modeller:
  - Logistic Regression (baseline)
  - LightGBM (final model)
- Ana metrik: ROC-AUC

Elde edilen sonuçlar:

- Logistic Regression ROC-AUC: **0.718**
- LightGBM ROC-AUC: **0.772** (final model)
