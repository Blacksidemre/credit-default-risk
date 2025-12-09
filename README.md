# credit-default-risk-final

Bu proje, UCI kredi kartı default veri seti ile geliştirilmiş uçtan uca bir kredi risk tahmin modelidir.

## Genel Özellikler

- Sektör: Bankacılık, kredi kartı default riski
- Veri seti: Default of Credit Card Clients (UCI)
- Amaç: Bir sonraki ay temerrüde düşme olasılığını tahmin etmek
- Modeller: Logistic Regression (baseline), LightGBM (final)
- Ana metrik: ROC-AUC

## Kurulum (Local)

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
jupyter notebook
# veya
streamlit run app.py
```
