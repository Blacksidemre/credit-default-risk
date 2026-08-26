from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

SAMPLE = {
    "LIMIT_BAL": 200000, "SEX": 2, "EDUCATION": 2, "MARRIAGE": 1, "AGE": 35,
    "PAY_0": 0, "PAY_2": 0, "PAY_3": 0, "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
    "BILL_AMT1": 50000, "BILL_AMT2": 48000, "BILL_AMT3": 47000,
    "BILL_AMT4": 45000, "BILL_AMT5": 43000, "BILL_AMT6": 42000,
    "PAY_AMT1": 5000, "PAY_AMT2": 5000, "PAY_AMT3": 5000,
    "PAY_AMT4": 5000, "PAY_AMT5": 5000, "PAY_AMT6": 5000,
}


def test_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "CrediRisk AI" in response.text
    assert "Risk Değerlendirme Formu" in response.text
    assert "/assets/docs/roc_auc_curve.png" in response.text


def test_static_css():
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    assert "--navy" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["model_loaded"] is True


def test_predict():
    response = client.post("/predict", json=SAMPLE)
    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body["default_probability"] <= 1.0
    assert body["prediction"] in [0, 1]
