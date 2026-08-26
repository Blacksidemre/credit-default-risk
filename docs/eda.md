# Keşifsel Veri Analizi (EDA)

Veri seti 30.000 müşteri ve 25 ham kolondan oluşur. `ID` model dışına alınır; hedef kolon `TARGET` olarak standardize edilir.

- Default oranı: %22,12
- Non-default oranı: %77,88
- Eksik değer: 0
- Ham model girdisi: 23 kolon

Hedef dağılımı `target_distribution.png` içinde `sns.countplot` ile gösterilir. Sınıf dengesizliği nedeniyle accuracy tek başına yeterli değildir; ROC-AUC, Average Precision, Recall, F2 ve False Negative Rate birlikte raporlanır.
