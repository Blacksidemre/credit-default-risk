````markdown
# credit-default-risk-final

Bu proje, UCI **Default of Credit Card Clients** veri seti kullanılarak kredi kartı müşterilerinin bir sonraki ay temerrüde düşme riskini tahmin etmek için hazırlanmıştır.  
Amaç, gerçek hayatta bankaların kredi riskini yönetmek için kullanabileceği, uçtan uca bir makine öğrenmesi pipeline’ı kurmaktır.

---

## 1. Problem Tanımı

- Hedef değişken: `TARGET`
  - `1` → Müşteri bir sonraki ay ödemede **temerrüde düşüyor**
  - `0` → Müşteri normal ödemeye devam ediyor
- İş problemi:  
  Banka, temerrüt riski yüksek olan müşterileri önceden tespit edip:
  - Kredi limitini düşürebilir
  - Ek teminat isteyebilir
  - Kampanya / kart tekliflerini kısıtlayabilir

Bu yüzden **false negative** (riskli müşteriyi risksiz sanmak) hatası, false positive’ten daha maliyetlidir.

---

## 2. Veri Seti

- Kaynak: UCI – *Default of Credit Card Clients Dataset*
- Gözlem sayısı: ≈ 30.000 müşteri
- Bazı önemli değişkenler:
  - `LIMIT_BAL` – Toplam kredi limiti
  - `BILL_AMT1–6` – Son 6 aya ait fatura tutarları
  - `PAY_AMT1–6` – Son 6 aya ait ödeme tutarları
  - `PAY_0–PAY_6` – Gecikme durumu kodları
  - `SEX`, `EDUCATION`, `MARRIAGE`, `AGE` – Demografik değişkenler

Ham veri dosyası:
```text
data/raw/default_of_credit_card_clients.csv
````

---

## 3. Proje Yapısı

```text
credit-default-risk-final/
├── data/
│   └── raw/
│       └── default_of_credit_card_clients.csv
├── docs/
│   ├── report.md
│   ├── eda.md
│   ├── modeling.md
│   ├── results.md
│   ├── metrics.json
│   ├── pipeline.png
│   ├── feature_importance.png
│   ├── confusion_matrix.png
│   └── placeholders/
│       ├── eda_plots.png
│       └── metrics_table.png
├── models/
│   └── final_model.pkl
├── notebooks/
│   ├── 1_eda.ipynb
│   ├── 2_baseline.ipynb
│   ├── 3_feature_engineering.ipynb
│   ├── 4_modeling.ipynb
│   ├── 5_evaluation.ipynb
│   └── 6_pipeline.ipynb
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_prep.py
│   ├── pipeline.py
│   └── inference.py
├── tests/
├── README.md
└── requirements.txt
```

* **`src/`** → Tüm asıl kod burada.
* **`notebooks/`** → Raporlama için kullanılan EDA ve modelleme defterleri.
* **`docs/`** → Yazılı raporlar + grafikler.
* **`models/final_model.pkl`** → Eğitilmiş LightGBM pipeline’ı.

---

## 4. Modelleme Özeti

### Feature Engineering

`src/data_prep.py` içinde:

* `PAY_SUM` = `PAY_AMT1–6` toplamı
* `BILL_SUM` = `BILL_AMT1–6` toplamı
* `LIMIT_PER_PAY` = `LIMIT_BAL / (PAY_SUM + 1)`
* `AGE_BIN` = yaşın kategorik versiyonu

### Ön İşleme

Tüm sayısal değişkenler için:

* Eksik değer → `SimpleImputer(strategy="median")`
* Ölçekleme → `StandardScaler()`

Bunlar sklearn `ColumnTransformer + Pipeline` içine gömülüdür.

### Modeller

1. **Logistic Regression (baseline)**
2. **LightGBM (final model)**

Değerlendirme ayarı:

* Eğitim / test oranı: **%80 / %20**
* `stratify=y` → sınıf dengesizliğini korumak için
* Ana metrik: **ROC-AUC**

Detaylı sonuçlar ve metrikler: `docs/results.md` ve `docs/metrics.json`.

---

## 5. Sonuçlar (Özet)

* Logistic Regression ROC-AUC: **≈ log_auc**
* LightGBM ROC-AUC: **≈ lgbm_auc**

> Not: Gerçek skorlar, projeyi tekrar çalıştırdığınızda `docs/metrics.json` dosyasında yer alır.

LightGBM modeli, baseline modele göre daha yüksek ROC-AUC verdiği için **final model** olarak seçilmiştir.
Riskli sınıf için Recall ve Precision da ayrıca izlenmiştir.

---

## 6. Kurulum

Proje klasörünün içinde:

```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Jupyter Notebook açmak için:

```bash
jupyter notebook
```

---

## 7. Nasıl Çalıştırılır?

### 7.1. Notebook Akışı

1. `notebooks/1_eda.ipynb` → Veri yapısı, temel istatistikler, dağılımlar
2. `notebooks/2_baseline.ipynb` → Logistic Regression ile ilk ROC-AUC
3. `notebooks/3_feature_engineering.ipynb` → Yeni feature’ların kontrolü
4. `notebooks/4_modeling.ipynb` → LightGBM eğitimi ve skoru
5. `notebooks/5_evaluation.ipynb` → `metrics.json` üzerinden sonuç okuma
6. `notebooks/6_pipeline.ipynb` → Pipeline diyagramı (pipeline.png)

Tüm defterlerde aynı Python ortamı (aynı kernel) kullanılmalıdır.

### 7.2. Kod Tarafı

`src/pipeline.py` içinden:

```python
from src.pipeline import train_baseline, train_lgbm_with_features

pipe_log, auc_log = train_baseline()
pipe_lgbm, auc_lgbm = train_lgbm_with_features(save=True)
```

`src/inference.py` ile tek müşteri tahmini:

```python
from src.inference import predict_single

sample = {
    "LIMIT_BAL": 20000,
    "SEX": 2,
    "EDUCATION": 2,
    "MARRIAGE": 1,
    "AGE": 35,
    # ... veri setindeki diğer kolonlar
}

proba = predict_single(sample)
print("Default olasılığı:", proba)
```

---

## 8. Geliştirme Fikirleri

* Hiperparametre optimizasyonu (GridSearchCV / Optuna)
* Farklı sınıf ağırlıkları veya `class_weight="balanced"`
* Precision–Recall eğrisi ve farklı threshold senaryoları
* Müşteri segmentlerine göre model performans analizi

````

İçindeki `≈ log_auc`, `≈ lgbm_auc` kısmını istersen gerçek skorlarla elle değiştirirsin.

---

## 2. `.gitignore`

Projeye bir de `.gitignore` ekle. `credit-default-risk-final` klasörüne `.gitignore` oluştur ve şunu koy:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Jupyter
.ipynb_checkpoints/

# Virtual env
venv/
.env/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
````

---

## 3. GitHub’a yükleme adımları

Şimdi asıl iş: bunu internete fırlatmak.

### 3.1. Klasöre gir

CMD’de:

```bat
cd C:\Users\Emre\Desktop\credit-build\credit-default-risk-final
```

### 3.2. Git’i başlat

```bat
git init
git add .
git commit -m "Initial commit - credit default risk project"
```

Eğer ilk kez kullanıyorsan, önce:

```bat
git config --global user.name "Emre"
git config --global user.email "senin_mailin@example.com"
```

### 3.3. GitHub’da repo aç

Tarayıcıda:

* GitHub hesabına gir
* **New repository**
* İsim: `credit-default-risk-final` (aynısı olsun, kafan rahat)
* **README, .gitignore vs oluşturma** → işaretleme, boş repo olsun.

Repo açılınca sana şu tarz bir URL verecek:

```text
https://github.com/KULLANICI_ADI/credit-default-risk-final.git
```

### 3.4. Remote ekle ve push et

CMD’de (hala proje klasöründesin):

```bat
git branch -M main
git remote add origin https://github.com/KULLANICI_ADI/credit-default-risk-final.git
git push -u origin main
```



