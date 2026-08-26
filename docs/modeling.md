# Modelleme ve Özellik Mühendisliği

## Temizleme

- `ID` kaldırılır.
- Hedef kolon `TARGET` adına çevrilir.
- `EDUCATION` 0/5/6 kodları 4 (`other`) altında birleştirilir.
- `MARRIAGE=0`, 3 (`other`) olarak normalize edilir.

## Özellikler

- `PAY_SUM`: `PAY_AMT1`–`PAY_AMT6` toplamı
- `BILL_SUM`: `BILL_AMT1`–`BILL_AMT6` toplamı
- `LIMIT_PER_PAY`: `LIMIT_BAL / PAY_SUM` (sıfır ödeme güvenli ele alınır)
- `AGE_BIN`: `<=30`, `31-40`, `41-50`, `51-60`, `60+`

## Preprocessing

- Sayısal: median imputasyon + StandardScaler
- Kategorik: most-frequent imputasyon + OneHotEncoder

## Modeller

### Logistic Regression

Baseline model, `class_weight="balanced"`, `max_iter=3000`.

### LightGBM

Final model parametreleri:

- `n_estimators=450`
- `learning_rate=0.035`
- `num_leaves=31`
- `min_child_samples=30`
- `subsample=0.90`
- `colsample_bytree=0.90`
- `reg_alpha=0.10`
- `reg_lambda=0.30`
- `class_weight="balanced"`

Karar eşiği, train split üzerinde 5-fold OOF F2 maksimizasyonu ile seçilir.
