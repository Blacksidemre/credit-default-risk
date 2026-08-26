"""FastAPI entry point for the CrediRisk AI dashboard and prediction API."""
from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field

from src.config import DOCS_DIR, PROJECT_ROOT
from src.inference import load_model, predict_batch, predict_single

APP_VERSION = "2.2.0"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"
METRICS_FILE = DOCS_DIR / "metrics.json"

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("credirisk")


def _load_metrics() -> dict:
    """Load model metrics used by the dashboard without making startup depend on them."""
    if not METRICS_FILE.exists():
        logger.warning("Metrics file not found: %s", METRICS_FILE)
        return {}
    try:
        return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.exception("Metrics file could not be read: %s", METRICS_FILE)
        return {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Load and validate the model once when the service starts."""
    logger.info("Starting CrediRisk AI v%s", APP_VERSION)
    try:
        bundle = load_model(force_reload=True)
        logger.info(
            "Model loaded successfully | model=%s threshold=%.6f",
            bundle.get("model_name", "LightGBM"),
            float(bundle.get("threshold", 0.5)),
        )
    except Exception:
        logger.exception("Model initialization failed")
        raise
    yield
    logger.info("CrediRisk AI shutdown complete")


app = FastAPI(
    title="CrediRisk AI API",
    version=APP_VERSION,
    description=(
        "LightGBM-based credit default risk demonstration trained on the UCI "
        "Default of Credit Card Clients dataset. The root path serves the web dashboard."
    ),
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1024)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add lightweight security headers suitable for a public demonstration service."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/assets/docs", StaticFiles(directory=DOCS_DIR), name="docs_assets")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


class CreditClient(BaseModel):
    """Raw feature schema expected by the serialized ML pipeline."""

    model_config = ConfigDict(extra="forbid")

    LIMIT_BAL: Annotated[float, Field(ge=0, examples=[200000])]
    SEX: Annotated[int, Field(ge=1, le=2, examples=[2])]
    EDUCATION: Annotated[int, Field(ge=0, le=6, examples=[2])]
    MARRIAGE: Annotated[int, Field(ge=0, le=3, examples=[1])]
    AGE: Annotated[int, Field(ge=18, le=120, examples=[35])]
    PAY_0: Annotated[int, Field(ge=-2, le=9, examples=[0])]
    PAY_2: Annotated[int, Field(ge=-2, le=9, examples=[0])]
    PAY_3: Annotated[int, Field(ge=-2, le=9, examples=[0])]
    PAY_4: Annotated[int, Field(ge=-2, le=9, examples=[0])]
    PAY_5: Annotated[int, Field(ge=-2, le=9, examples=[0])]
    PAY_6: Annotated[int, Field(ge=-2, le=9, examples=[0])]
    BILL_AMT1: float = 50000
    BILL_AMT2: float = 48000
    BILL_AMT3: float = 47000
    BILL_AMT4: float = 45000
    BILL_AMT5: float = 43000
    BILL_AMT6: float = 42000
    PAY_AMT1: Annotated[float, Field(ge=0)] = 5000
    PAY_AMT2: Annotated[float, Field(ge=0)] = 5000
    PAY_AMT3: Annotated[float, Field(ge=0)] = 5000
    PAY_AMT4: Annotated[float, Field(ge=0)] = 5000
    PAY_AMT5: Annotated[float, Field(ge=0)] = 5000
    PAY_AMT6: Annotated[float, Field(ge=0)] = 5000


class PredictionResponse(BaseModel):
    default_probability: float
    prediction: int
    threshold: float
    risk_label: str


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request):
    """Render the browser-facing risk dashboard."""
    metrics = _load_metrics()
    lightgbm_metrics = metrics.get("models", {}).get("LightGBM", {})
    dataset_metrics = metrics.get("dataset", {})
    final_model = metrics.get("final_model", {})
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "metrics": lightgbm_metrics,
            "dataset": dataset_metrics,
            "final_model": final_model,
            "app_version": APP_VERSION,
        },
    )


@app.get("/api", tags=["system"])
def api_info() -> dict:
    """Return machine-readable service metadata."""
    return {
        "service": "CrediRisk AI",
        "version": APP_VERSION,
        "status": "ok",
        "model": "LightGBM",
        "dashboard": "/",
        "docs": "/docs",
        "health": "/health",
        "predict": "POST /predict",
        "batch_predict": "POST /predict/batch",
    }


@app.get("/health", tags=["system"])
def health() -> dict:
    """Render readiness endpoint; returns 2xx only when the model can be loaded."""
    bundle = load_model()
    commit = os.getenv("RENDER_GIT_COMMIT", "local")
    return {
        "status": "healthy",
        "service": "CrediRisk AI",
        "version": APP_VERSION,
        "model_loaded": True,
        "model_name": bundle.get("model_name", "LightGBM"),
        "threshold": float(bundle.get("threshold", 0.5)),
        "deployment": {
            "platform": "render" if os.getenv("RENDER") == "true" else "local",
            "branch": os.getenv("RENDER_GIT_BRANCH", "local"),
            "commit": commit[:12] if commit != "local" else commit,
            "repository": os.getenv("RENDER_GIT_REPO_SLUG", "local"),
        },
    }


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(payload: CreditClient) -> PredictionResponse:
    try:
        result = predict_single(payload.model_dump())
        return PredictionResponse(**result)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error during single prediction")
        raise HTTPException(status_code=500, detail="Tahmin sırasında beklenmeyen bir hata oluştu.") from exc


@app.post("/predict/batch", response_model=list[PredictionResponse], tags=["prediction"])
def predict_many(payload: list[CreditClient]) -> list[PredictionResponse]:
    if not payload:
        raise HTTPException(status_code=400, detail="En az bir kayıt gönderilmelidir.")
    if len(payload) > 1000:
        raise HTTPException(status_code=413, detail="Tek istekte en fazla 1000 kayıt gönderilebilir.")
    try:
        results = predict_batch([row.model_dump() for row in payload])
        return [PredictionResponse(**result) for result in results]
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error during batch prediction")
        raise HTTPException(status_code=500, detail="Batch tahmin sırasında beklenmeyen bir hata oluştu.") from exc
