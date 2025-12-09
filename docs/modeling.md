# Modelleme ve Özellik Mühendisliği

## Ön İşleme

- `ID` kolonu model dışında bırakılmıştır.
- Hedef kolon, veri setindeki ham isimden `TARGET` olarak yeniden adlandırılmıştır.
- Tüm sayısal özellikler için:
  - Median imputasyon
  - StandardScaler ile ölçekleme

Bu adımlar sklearn `ColumnTransformer` ve `Pipeline` yapısı içine gömülmüştür.

## Eklenen Özellikler

- `PAY_SUM`: PAY_AMT1–6 toplamı
- `BILL_SUM`: BILL_AMT1–6 toplamı
- `LIMIT_PER_PAY`: LIMIT_BAL / (PAY_SUM + 1)
- `AGE_BIN`: yaşın kategoriye çevrilmiş hali

## Modeller

1. **Logistic Regression (baseline)**  
   Basit, yorumlanabilir, hızlı eğitilen bir referans modeldir.

2. **LightGBM (final model)**  
   Ağaç tabanlı gradient boosting yaklaşımıdır. Kullanılan temel hiperparametreler:
   - `n_estimators = 300`
   - `learning_rate = 0.05`
   - `num_leaves = 50`
   - `subsample = 0.9`

`docs/feature_importance.png` dosyasında LightGBM modelinin en önemli 15 özelliği gösterilmektedir.
