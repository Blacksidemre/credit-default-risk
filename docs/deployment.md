# Render Deployment

## Public endpoints

- Dashboard: `https://credit-default-risk-dbuk.onrender.com/`
- API docs: `https://credit-default-risk-dbuk.onrender.com/docs`
- Health: `https://credit-default-risk-dbuk.onrender.com/health`

## Runtime configuration

The service is designed for Python 3.11.11. The version is pinned in `.python-version`.

Recommended Render service settings:

- Repository: `https://github.com/Blacksidemre/credit-default-risk`
- Branch: `main`
- Runtime: Python
- Root directory: repository root
- Build command: `python -m pip install --upgrade pip && python -m pip install -r requirements.txt && python scripts/render_smoke_test.py`
- Start command: `python -m uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1`
- Health check path: `/health`
- Auto deploy: on commit

The build smoke test loads `models/final_model.pkl` and executes a sample prediction. This catches package/artifact incompatibilities before the deployment is promoted.

## Expected health response

```json
{
  "status": "healthy",
  "service": "CrediRisk AI",
  "version": "2.1.0",
  "model_loaded": true,
  "model_name": "LightGBM",
  "threshold": 0.29844278293849474
}
```

## Troubleshooting

If the public URL returns `503 Service Unavailable`:

1. Open the service in Render and inspect the latest deploy logs.
2. Confirm the service is linked to the correct repository and `main` branch.
3. Confirm Python 3.11.11 is selected from `.python-version` or `PYTHON_VERSION`.
4. Confirm the build command completes the smoke test successfully.
5. Confirm the start command binds to `0.0.0.0` and `$PORT`.
6. Confirm `/health` returns HTTP 2xx within the Render health-check timeout.
7. Trigger **Deploy latest commit** after correcting service settings.

The `render.yaml` Blueprint uses the current `autoDeployTrigger: commit` field and can be used to synchronize supported service settings.
