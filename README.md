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
