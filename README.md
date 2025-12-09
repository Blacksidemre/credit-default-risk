-----

````markdown
# 🏦 Kredi Temerrüt Riski Tahmini (Credit Default Risk Prediction)

Bu proje, UCI "Default of Credit Card Clients" veri seti kullanılarak, bir kredi kartı müşterisinin bir sonraki ay temerrüde düşme ihtimalini tahmin etmek için hazırlanmış **uçtan uca bir Makine Öğrenmesi (ML) pipeline'ıdır.**

**Amaç:** Bankaların risk yönetim süreçlerinde kullanabileceği, yanlış negatif oranı düşük, güvenilir bir tahmin modeli sunmaktır.

---

## ❓ Proje Taslağındaki Cevaplar (8 Kritik Soru)

Aşağıda, projenin teknik ve iş odaklı tüm zorunlu sorularına ait detaylı yanıtlar bulunmaktadır.

### 1. Problem Tanımı ve İş Kararı
Bu, bankacılık sektöründeki **Kredi Riski Tahmini** problemidir. Bir müşterinin temerrüt riskini tahmin etmek, bankanın **limit yönetimi, riskli müşteri segmentasyonu** ve **temerrüt zararını azaltma** gibi kritik kararlarını doğrudan etkiler. Hedef sınıf dengesiz olduğu için **yanlış negatif (False Negative)** en maliyetli hatadır.

### 2. Baseline Süreci ve Skoru
* **Model:** Logistic Regression kullanılmıştır.
* **Veri:** Sadece ham değişkenler ve minimal ön işleme.
* **Sonuç:** Baseline ROC-AUC skoru **yaklaşık 0.71–0.73** aralığındadır. Bu skor, sonraki modelleme aşamaları için referans bir performans noktası oluşturmuştur.

### 3. Feature Engineering (FE) Denemeleri ve Sonuçları
Veri setine domain bilgisi katmak için dört ana özellik türetilmiştir:
* `PAY_SUM` (Son 6 ay ödeme toplamı)
* `BILL_SUM` (Son 6 ay fatura toplamı)
* `LIMIT_PER_PAY` (Limit / Ödeme toplamı oranı)
* `AGE_BIN` (Yaşın kategorik versiyonu)

**Sonuç:** Bu özelliklerin eklenmesi, modelin **ayrıştırma gücünü önemli ölçüde artırmış** ve LightGBM modelinin performansını baseline'a göre belirgin şekilde yükseltmiştir. Özellikle `LIMIT_PER_PAY` yüksek önem ağırlığına ulaşmıştır.

### 4. Seçilen Validasyon Şeması ve Nedeni
* **Şema:** Hold-out Stratified Split (%80 Eğitim, %20 Test).
* **Neden Stratified?** `TARGET` sınıfının dengesiz olması nedeniyle, sınıf oranının hem eğitim hem de test kümelerinde korunması zorunludur. Bu, modelin gerçek performansını daha doğru temsil etmesini sağlar.

### 5. Final Pipeline'daki Özellik Seti ve Ön İşleme
Final pipeline, otomasyon ve yeniden üretilebilirlik sağlayacak şekilde yapılandırılmıştır:
* **İmputasyon:** Tüm sayısal kolonlara **median imputasyon**.
* **Ölçekleme:** Tüm sayısal kolonlara **StandardScaler** ile ölçekleme.
* **Özellik Seti:** Orijinal kolonlar ve **türetilen dört özelliğin tamamı** dahil edilmiştir.
* Bu kombinasyon, LightGBM ile en yüksek ROC-AUC skorunu vermiştir.

### 6. Final Model ile Baseline Arasındaki Başarı Farkı
| Model | Metrik | Skor |
| :--- | :--- | :--- |
| **Baseline (LogReg)** | ROC-AUC | $\approx 0.71–0.73$ |
| **Final Model (LightGBM)** | ROC-AUC | $\approx 0.78–0.80$ |

**Farkın Kaynakları:**
1.  **Ağaç Yapısı:** LightGBM'in doğrusal olmayan (non-linear) ilişkileri yakalama yeteneği.
2.  **Özellik Mühendisliği:** Türetilen yeni özelliklerin katkısı.
3.  **Boosting:** LightGBM'in performansı maksimize eden güçlü yükseltme (boosting) yapısı.

### 7. Final Modelin İş Gereksinimleriyle Uyumu
**Uyumlu.** Final LightGBM modeli:
* Yüksek maliyetli **yanlış negatifleri azaltarak** (daha yüksek Recall sağlayarak) default sınıfını baseline'a göre daha iyi yakalamaktadır.
* Elde edilen ROC-AUC artışı, karar süreçlerini güçlendirir.
* LightGBM'in düşük tahmin süresi (**inference latency**) sayesinde canlı sistemlerde kullanıma uygundur.

### 8. Modelin Canlıya Alınması ve İzlenmesi
#### Canlıya Alma (Deployment)
Model dosyası (`final_model.pkl`), **FastAPI** veya Streamlit kullanılarak bir **REST endpoint** üzerinden servis edilir. Girdi verileri, tahminden önce eğitimdeki aynı preprocessing pipeline'dan geçirilir.

#### Canlı İzleme (Monitoring)
Model performansının zamanla düşmemesi için düzenli olarak izlenmesi gereken metrikler:
* **Model Performansı:** Aylık ROC-AUC takibi ve segment bazlı performans raporları (yaş, limit vb.).
* **Veri Kalitesi (Data Drift):** Girdi veri dağılımlarındaki kaymaların (özellikle ödeme ve limit değişkenleri) kontrolü.
* **İş Metrikleri:** Default oranındaki değişimin izlenmesi.

Bu metrikler bozulmaya başladığında modelin **yeniden eğitilmesi** zorunludur.

---

## 🛠 Proje Klasör Yapısı (Özet)
Bu yapı, profesyonel veri bilimi projelerinde kullanılan standart bir mimaridir.

```text
credit-default-risk-final
├── data/
│   └── raw/ → Ham veri
├── docs/
│   └── *.md, *.png → Raporlar, grafikler (Confusion Matrix, Feature Importance vb.)
├── models/
│   └── final_model.pkl → Eğitilmiş LightGBM modeli
├── notebooks/
│   └── 1_eda.ipynb, 2_baseline.ipynb, ... → Tüm analiz ve modelleme akışı
├── src/
│   └── data_prep.py, pipeline.py, inference.py → Tüm Python modülleri
└── requirements.txt
````

-----

## 💻 Kurulum ve Çalıştırma

Proje klasörünün içinde:

1.  **Sanal Ortam Oluştur:**
    ```bash
    python -m venv venv
    ```
2.  **Ortamı Aktifleştir:**
    ```bash
    venv\Scripts\activate  # Windows
    # source venv/bin/activate # Mac/Linux
    ```
3.  **Paketleri Yükle:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Notebook'ları Başlat:**
    ```bash
    jupyter notebook
    ```

<!-- end list -->

```
```
