# Model Card — Credit Default Risk LightGBM

## Amaç

Bir kredi kartı müşterisinin bir sonraki ay temerrüde düşme olasılığını tahmin etmek.

## Veri

- Kaynak: UCI Default of Credit Card Clients
- Satır: 30.000
- Ham model girdisi: 23 özellik
- Hedef pozitif oranı: %22,12

## Model

Final estimator: LightGBM Classifier.

Pipeline sırası:

1. Veri temizleme
2. Feature engineering
3. Sayısal median imputasyon + StandardScaler
4. Kategorik most-frequent imputasyon + OneHotEncoder
5. LightGBM

## Türetilen Özellikler

- PAY_SUM
- BILL_SUM
- LIMIT_PER_PAY
- AGE_BIN

## Validasyon

- StratifiedKFold: 5 split
- Hold-out: ilk fold, 24.000 train / 6.000 test
- Threshold seçimi: yalnızca train verisindeki 5-fold out-of-fold olasılıklar üzerinde F2 maksimizasyonu

## Hold-out Sonuçları

| Metrik | Logistic Regression | LightGBM |
|---|---:|---:|
| ROC-AUC | 0.7378 | 0.7884 |
| Average Precision | 0.4960 | 0.5638 |
| Recall | 0.6544 | 0.8486 |
| F2 | 0.5808 | 0.6443 |
| False Negative Rate | 0.3456 | 0.1514 |

Final LightGBM threshold: `0.2984427829`.

## Kullanım Notu

Bu model eğitim/demonstrasyon amaçlıdır. Gerçek kredi kararı gibi yüksek etkili finansal kararlarda tek başına otomatik karar mekanizması olarak kullanılmamalı; güncel veri, regülasyon, adalet/fairness, açıklanabilirlik ve insan gözetimi kontrolleri eklenmelidir.
