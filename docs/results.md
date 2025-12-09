# Sonuçlar ve Değerlendirme

## Performans Karşılaştırması

**Logistic Regression**

- ROC-AUC: 0.718
- Accuracy: 0.809
- Precision: 0.687
- Recall: 0.253

**LightGBM (Final Model)**

- ROC-AUC: 0.772
- Accuracy: 0.816
- Precision: 0.653
- Recall: 0.358

LightGBM modeli, baseline Logistic modele göre ROC-AUC açısından daha iyi performans göstermiştir ve final model olarak seçilmiştir.

## Validasyon Şeması

- Eğitim / test ayrımı: %80 / %20, stratified split
- Neden: Veri seti görece büyük ve Kaggle benzeri değerlendirme mantığına yakın şekilde tek bir hold-out set üzerinde skor üretmek yeterlidir. Sınıf dengesizliği nedeniyle stratified seçilmiştir.

## İş Zekası / İş Gereksinimi Açısından Değerlendirme

- Banka açısından **false negative** (riski yüksek müşteriyi risksiz sanmak) daha maliyetlidir.
- Bu nedenle:
  - ROC-AUC ile genel ayrıştırma gücü ölçülmüş,
  - Recall ve Precision metrikleri ile riskli sınıfın yakalanma oranı incelenmiştir.

## Canlı Kullanım ve İzleme (Monitoring) Fikri

Model canlıya alınsaydı aşağıdaki metrikler düzenli izlenirdi:

- Aylık ROC-AUC ve accuracy
- Default oranı (gerçek verilerde)
- Girdi değişkenlerinin dağılımı (data drift)
- Segment bazlı performans (yaş grubu, limit seviyesi vb.)

## Karışıklık Matrisi

`docs/confusion_matrix.png` dosyası, LightGBM modelinin test seti üzerindeki karışıklık matrisini göstermektedir. Eşik değeri 0.5 alınmıştır.

## Özellik Önemi

`docs/feature_importance.png` grafiği, model kararlarında en etkili 15 özelliği göstermektedir. Kredi limiti, son fatura tutarları ve ödeme miktarlarının risk tahmini için kritik olduğu gözlemlenmiştir.
