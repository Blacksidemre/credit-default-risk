# Keşifsel Veri Analizi (EDA)

Bu bölümde veri setinin yapısı ve hedef değişkenin dağılımı incelenmiştir.

## Değişkenler

- LIMIT_BAL: Müşterinin toplam kredi limiti
- BILL_AMT1–6: Son 6 aya ait fatura tutarları
- PAY_AMT1–6: Son 6 aya ait ödeme tutarları
- PAY_0–PAY_6: Gecikme durumu kodları
- Demografik değişkenler: Cinsiyet, eğitim, medeni durum, AGE

## Hedef Değişken

`TARGET` değişkeni dengesizdir; default olmayan müşteriler çoğunluktadır. Bu nedenle doğruluk (accuracy) tek başına yeterli bir metrik değildir. ROC-AUC, sınıf dengesizliği altında daha anlamlı karşılaştırma imkanı verdiği için ana metrik olarak kullanılmıştır.

`docs/placeholders/eda_plots.png` dosyasında LIMIT_BAL dağılımı ve hedef değişkenin sınıf dağılımı görsel olarak verilmiştir.
