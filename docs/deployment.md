# Render Deployment Rehberi

## Dosyalar

Deployment için gerekli dosyalar repo kökünde hazırdır:

- `app.py`
- `requirements.txt`
- `render.yaml`
- `Procfile`
- `.python-version`
- `models/final_model.pkl`

## Render Ayarları

- Runtime: Python
- Python: 3.11.11 (`.python-version`)
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Health Check: `/health`

## Beklenen Sağlık Cevabı

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "LightGBM",
  "threshold": 0.29844278293849474
}
```

## Demo URL

`https://credit-default-risk-dbuk.onrender.com/`

Deployment tamamlandıktan sonra aşağıdaki yollar kontrol edilmelidir:

- `/`
- `/health`
- `/docs`
- `POST /predict`

## Sık Hata Kaynakları

1. `models/final_model.pkl` repository'ye eklenmemişse startup fail eder.
2. Python/sklearn/lightgbm sürümleri model artifact ile uyuşmazsa deserialize hatası oluşabilir; bu yüzden sürümler pinlenmiştir.
3. Start command içinde `$PORT` kullanılmalıdır.
4. Health check `/health` 2xx dönmelidir.
5. Root directory yanlış ayarlanırsa `app:app` import edilemez.

## Web Dashboard

Deployment sonrasında ana URL (`/`) son kullanıcıya yönelik **CrediRisk AI** dashboard'unu açar. Dashboard aynı FastAPI uygulaması içinde çalıştığı için ayrı bir frontend servisi gerektirmez.

- `/` → Görsel kredi temerrüt riski dashboard'u
- `/docs` → Swagger API dokümantasyonu
- `/health` → Render health check
- `/predict` → Dashboard ve harici istemcilerin kullandığı tahmin endpoint'i
- `/assets/docs/*` → Eğitim sırasında üretilen model performans grafikleri

Dashboard `templates/index.html`, `static/styles.css` ve `static/app.js` dosyalarından oluşur. Tahmin formu tarayıcıdan aynı origin üzerindeki `/predict` endpoint'ine JSON gönderir; bu nedenle ek bir CORS veya Node.js katmanı gerekmez.
