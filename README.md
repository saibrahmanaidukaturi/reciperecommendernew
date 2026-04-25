# Recipe Recommender (Production / Kubernetes)

This repository contains:

- Streamlit UI (Firebase auth)
- FastAPI service exposing recommendation endpoints
- Kubernetes manifests (kustomize) to run UI + API as separate workloads

## Services

### UI (Streamlit)

- Port: `8501`
- Health: `/_stcore/health`

### API (FastAPI)

- Port: `8000`
- Health: `/healthz`
- Recommend: `POST /recommend`

Example request:

```bash
curl -X POST http://localhost:8000/recommend \
  -H 'content-type: application/json' \
  -d '{"query":"chicken spinach garlic","top_k":12}'
```

## Local development

### 1) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run the API

```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

### 3) Run the UI

```bash
streamlit run app/ui/streamlit_app.py --server.address=0.0.0.0 --server.port=8501
```

## Docker

The `Dockerfile` builds a single image that can run either:

- the Streamlit UI (default `CMD`)
- the API (override the container command in Kubernetes)

Build:

```bash
docker build -t recipe-recommender:latest .
```

Run UI:

```bash
docker run -p 8501:8501 recipe-recommender:latest
```

Run API:

```bash
docker run -p 8000:8000 recipe-recommender:latest \
  python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

## Kubernetes (kustomize)

Manifests are in `k8s/base`.

- `recipe-recommender-ui` Deployment + Service
- `recipe-recommender-api` Deployment + Service
- `Ingress` routes:
  - `/` -> UI
  - `/api` -> API

### Configure Firebase secret (required for UI auth)

Update the placeholder in:

- `k8s/base/secret-streamlit.yaml`

Replace:

- `FIREBASE_WEB_API_KEY = "REPLACE_ME"`

### Apply

```bash
kubectl apply -k k8s/base
```

### TLS / HTTPS

The current Ingress is **HTTP only**. To enable TLS you’ll typically add one of:

- cert-manager + Let’s Encrypt
- a cloud provider managed certificate

## Notes

- The API currently returns recommendations based on the same underlying embedding pipeline used by the UI.
- The UI is not yet wired to call the API; it still runs recommendations in-process.
