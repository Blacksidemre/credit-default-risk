-----

```markdown
# Credit Default Risk Prediction 💳

Bu proje, UCI **"Default of Credit Card Clients"** veri seti kullanılarak bir kredi kartı müşterisinin bir sonraki ay temerrüde düşme ihtimalini tahmin etmek için hazırlanmıştır. 

**Amaç:** Bankaların risk yönetim süreçlerinde kullanılabilecek uçtan uca, ölçeklenebilir bir makine öğrenmesi pipeline’ı inşa etmektir.

---

## 1. Problem Tanımı
Bu proje, bankacılık sektörünün en temel problemlerinden biri olan **Kredi Riski Tahmini** üzerine odaklanır. Bir müşterinin bir sonraki ay borcunu ödeyip ödemeyeceğini önceden tahmin etmek, bankanın şu kritik kararlarını doğrudan etkiler:

* **Limit Yönetimi:** Kredi limitlerinin dinamik ayarlanması.
* **Riskli Müşteri Segmentasyonu:** Erken uyarı sistemleri.
* **Kampanya ve Ürün Uygunluğu:** Doğru müşteriye doğru ürün sunumu.
* **Zarar Minimizasyonu:** Temerrüt (default) kayıplarının azaltılması.

> **⚠️ Kritik İş Kuralı:** Hedef değişken (TARGET) sınıf dengesizliğine sahiptir. İş problemi açısından **"False Negative"** (riskli müşteriyi risksiz sanmak) en maliyetli hatadır. Bu nedenle model başarısında ROC-AUC ve Recall metrikleri önceliklidir.

---

## 2. Baseline Süreci ve Skoru
Modelleme sürecine referans bir performans noktası oluşturmak amacıyla **Logistic Regression** seçilmiştir. Sadece ham değişkenler ve minimal veri ön işleme ile yapılan eğitim sonucunda:

* **Model:** Logistic Regression
* **ROC-AUC Skoru:** `~0.71 – 0.73`
* *(Detaylı gerçek skorlar `docs/metrics.json` dosyasındadır.)*

---

## 3. Feature Engineering Denemeleri ve Sonuçları
Veri setine domain bilgisini yansıtmak ve modelin öğrenme kapasitesini artırmak amacıyla yeni özellikler türetilmiştir:

* `PAY_SUM`: Son 6 ay ödeme toplamı
* `BILL_SUM`: Son 6 ay fatura toplamı
* `LIMIT_PER_PAY`: Limit / (Ödeme Toplamı + 1)
* `AGE_BIN`: Yaşın kategorik versiyonu

**Sonuç:**
Bu özelliklerin eklenmesiyle modelin ayrıştırma gücü artmış, özellikle **LightGBM** performansı baseline modele göre belirgin şekilde yükselmiştir. Feature Importance analizlerinde `LIMIT_PER_PAY` ve `BILL_SUM` değişkenleri yüksek önem düzeyine ulaşmıştır.

---

## 4. Seçilen Validasyon Şeması ve Nedeni
Veri seti yaklaşık 30.000 gözlemden oluştuğu için **Hold-out Stratified Split** (%80 Eğitim, %20 Test) yöntemi tercih edilmiştir.

**Neden Stratified Split?**
1.  TARGET sınıfı dengesizdir (Imbalanced Dataset).
2.  Sınıf oranının (Default/Non-default) hem train hem de test setinde korunması gerekir.
3.  Modelin gerçek performansını rastgele bölmeye göre daha doğru temsil eder.

*(Not: Bu veri boyutu için Cross-Validation maliyeti yüksek görüldüğünden hold-out stratejisi yeterli bulunmuştur.)*

---

## 5. Final Pipeline ve Ön İşleme Stratejisi
Geliştirilen pipeline tamamen otomatik ve yeniden üretilebilir (reproducible) yapıdadır. İzlenen adımlar:

1.  **Imputation:** Tüm sayısal kolonlardaki eksik veriler için `Median` imputasyon.
2.  **Scaling:** Değişkenlerin aynı ölçeğe getirilmesi için `StandardScaler`.
3.  **Feature Selection:** Türetilmiş özelliklerin tamamı dahil edilmiştir.
4.  **Cleaning:** Ek veya gereksiz kolon bulunmadığı için manuel feature dropping yapılmamıştır.

Bu kombinasyon, LightGBM modeli ile en yüksek ROC-AUC skorunu sağlamıştır.

---

## 6. Final Model vs. Baseline Başarı Farkı

| Model | ROC-AUC Skoru |
| :--- | :--- |
| **Baseline (Logistic Reg.)** | `~0.71 – 0.73` |
| **Final Model (LightGBM)** | `~0.78 – 0.80` |

**Farkın Ana Kaynakları:**
* Ağaç tabanlı modelin (LightGBM) non-linear (doğrusal olmayan) ilişkileri yakalayabilmesi.
* Feature Engineering ile üretilen güçlü değişkenler.
* LightGBM'in boosting yapısının zayıf öğrenicilerden güçlü bir model çıkarması.

Final model, özellikle default sınıfında daha yüksek **recall** sağlayarak iş kararları için çok daha güvenilir hale gelmiştir.

---

## 7. Business Gereksinimleri ile Uyum
**Sonuç: Evet, model iş gereksinimleri ile uyumludur.**

* ✅ Default sınıfını baseline modele göre daha iyi yakalamaktadır.
* ✅ Yüksek maliyetli "yanlış negatif" (riskliyi kaçırma) hatalarını azaltmaktadır.
* ✅ ROC-AUC artışı, karar destek mekanizmalarını kuvvetlendirmektedir.
* ✅ Sektör için kabul edilen hız–performans dengesini sağlamaktadır (LightGBM inference süresi düşüktür).

---

## 8. Canlıya Alma (Deployment) ve İzleme (Monitoring)

### Canlıya Alma Stratejisi
1.  Model dosyası (`final_model.pkl`) bir API üzerinden servis edilir.
2.  **Streamlit** veya **FastAPI** kullanılarak bir REST endpoint oluşturulur.
3.  Girdi değişkenleri, eğitimdeki preprocessing pipeline’ından geçirilir.
4.  Model tahmini (olasılık skoru) gerçek zamanlı olarak döndürülür.

### İzleme (Monitoring) Planı
Model canlıya alındıktan sonra performansın düşmemesi için şu metrikler takip edilmelidir:
* 📅 **Aylık ROC-AUC Takibi**
* 📊 **Default Rate Değişimi**
* ⚠️ **Data Drift:** Veri dağılımlarındaki kaymaların kontrolü.
* 📈 **Feature Importance:** Özellik önemlerinin zamansal değişimi.
* 👥 **Segment Bazlı Performans:** Yaş, limit seviyesi vb. kırılımlarda hata analizi.

*Metriklerde bozulma tespit edildiğinde model yeniden eğitilmelidir (Retraining).*

---

## 🏁 Proje Özeti
Bu çalışma, bankacılık sektöründe temerrüt riskini tahmin eden profesyonel bir ML pipeline’ı içerir. Veri hazırlama, feature engineering, modelleme, validasyon, değerlendirme ve dokümantasyon aşamalarının tamamı uçtan uca yerine getirilmiştir.

* **Final Model:** LightGBM Classifier
* **Final Metrik:** ROC-AUC ≈ 0.78–0.80
* **Statü:** Tamamlandı & Kullanıma Hazır
```
