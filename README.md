-----

````markdown
# Credit Default Risk Prediction 💳

Bu proje, UCI **"Default of Credit Card Clients"** veri seti kullanılarak, kredi kartı müşterilerinin bir sonraki ay temerrüde düşme riskini tahmin etmek için hazırlanmış uçtan uca bir makine öğrenmesi çalışmasıdır.

**Amaç:** Bankaların riskli müşterileri önceden tespit ederek kredi stratejilerini daha güvenli ve veri odaklı bir şekilde yönetebilmesini sağlamaktır.

---

## 📌 Problem Tanımı

Projenin temel amacı `TARGET` değişkenini tahmin etmektir:

* **1 = Default:** Riski yüksek müşteri (Temerrüde düşen)
* **0 = Normal:** Ödemelerini düzenli yapan müşteri

> **Kritik Not:** Gerçek hayattaki iş problemi açısından **"False Negative"** (riskli müşteriyi risksiz sanmak) en tehlikeli hatadır. Bu nedenle model başarısı değerlendirilirken **ROC-AUC** ve **Recall** metrikleri ön planda tutulmuştur.

---

## 📂 Veri Seti

* **Kaynak:** UCI – Default of Credit Card Clients
* **Boyut:** Yaklaşık 30.000 müşteri kaydı
* **Ham Veri Yolu:** `data/raw/default_of_credit_card_clients.csv`

### Ana Değişken Grupları
* **LIMIT_BAL:** Kredi limiti
* **BILL_AMT1–6:** Son 6 aya ait fatura tutarları
* **PAY_AMT1–6:** Son 6 aya ait ödeme tutarları
* **PAY_0–PAY_6:** Geçmiş ödeme/gecikme durumları
* **Demografik:** Cinsiyet, eğitim, medeni durum ve yaş bilgileri

---

## 🏗 Proje Klasör Yapısı

Profesyonel veri bilimi standartlarına uygun proje mimarisi:

```text
credit-default-risk-final
│
├── data/
│   └── raw/                     # Ham veri dosyası
│
├── docs/                        # Dokümantasyon ve Görseller
│   ├── report.md                # Genel proje raporu
│   ├── eda.md                   # Keşifsel analiz raporu
│   ├── modeling.md              # Modelleme süreci
│   ├── results.md               # Final sonuçlar
│   ├── pipeline.png             # Pipeline diyagramı
│   ├── feature_importance.png   # Değişken önem düzeyleri
│   ├── confusion_matrix.png     # Karışıklık matrisi
│   ├── metrics.json             # Model skorları
│   └── placeholders/            # Ek EDA görselleri
│
├── models/
│   └── final_model.pkl          # Eğitilmiş LightGBM modeli
│
├── notebooks/                   # Analiz ve Geliştirme Notları
│   ├── 1_eda.ipynb              # Veri inceleme
│   ├── 2_baseline.ipynb         # Logistic Regression (Baz Model)
│   ├── 3_feature_engineering.ipynb # Yeni değişken üretimi
│   ├── 4_modeling.ipynb         # LightGBM eğitimi
│   ├── 5_evaluation.ipynb       # Sonuç değerlendirme
│   └── 6_pipeline.ipynb         # Pipeline görselleştirme
│
├── src/                         # Python Kaynak Kodları
│   ├── data_prep.py             # Veri ön işleme
│   ├── pipeline.py              # Model boru hattı
│   ├── inference.py             # Tahminleme modülü
│   ├── config.py                # Konfigürasyon ayarları
│   └── __init__.py
│
└── requirements.txt             # Gerekli kütüphaneler
````

-----

## ⚙️ Özellik Mühendisliği (Feature Engineering)

Modelin ayrıştırma gücünü artırmak adına aşağıdaki türetilmiş değişkenler oluşturulmuştur:

  * `PAY_SUM`: PAY\_AMT1–6 (Ödemeler) toplamı
  * `BILL_SUM`: BILL\_AMT1–6 (Faturalar) toplamı
  * `LIMIT_PER_PAY`: LIMIT\_BAL / (PAY\_SUM + 1) oranı
  * `AGE_BIN`: Yaş değişkeninin kategorik gruplandırılması

-----

## 🚀 Modelleme Yaklaşımı

### 1\. Baseline Model (Referans)

  * **Model:** Logistic Regression
  * **Amaç:** Hızlı, yorumlanabilir ve karşılaştırma için bir taban puan oluşturmak.

### 2\. Final Model (Seçilen)

  * **Model:** LightGBM Classifier
  * **Neden Seçildi?** Baseline modele göre daha yüksek ROC-AUC skoru elde etmesi ve karmaşık veri yapısını daha iyi genellemesi.
  * **Hiperparametreler:**
      * `n_estimators = 300`
      * `learning_rate = 0.05`
      * `num_leaves = 50`
      * `subsample = 0.9`

### Değerlendirme Metrikleri

Tüm skorlar `docs/metrics.json` içerisinde kayıt altına alınmıştır.

  * **ROC-AUC (Ana Metrik)**
  * Recall & Precision
  * Accuracy
  * Confusion Matrix

-----

## 💻 Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

**1. Sanal ortam oluşturun:**

```bash
python -m venv venv
```

**2. Ortamı aktifleştirin:**

  * Windows için:
    ```bash
    venv\Scripts\activate
    ```
  * Mac/Linux için:
    ```bash
    source venv/bin/activate
    ```

**3. Gerekli paketleri yükleyin:**

```bash
pip install -r requirements.txt
```

**4. Notebook'ları inceleyin:**

```bash
jupyter notebook
```

> **Not:** Tekil tahmin yapmak isteyenler için `src/inference.py` içindeki `predict_single` fonksiyonu kullanılabilir.

-----

## ✅ Sonuç

Proje uçtan uca; **veri hazırlama, özellik mühendisliği, modelleme, değerlendirme ve dokümantasyon** süreçlerini eksiksiz kapsayan, yeniden üretilebilir (reproducible) bir pipeline sunmaktadır.

LightGBM modeli, performans metriklerindeki başarısı nedeniyle **Final Model** olarak belirlenmiş ve `models/` klasörüne kaydedilmiştir.

````

