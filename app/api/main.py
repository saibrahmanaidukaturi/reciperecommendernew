from fastapi import FastAPI, HTTPException

from app.api.schemas import RecommendRequest, RecommendResponse
from app.api.service import get_recommendations

app = FastAPI(title="recipe-recommender-api")


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest) -> RecommendResponse:
    query = (payload.query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    items = get_recommendations(query=query, top_k=payload.top_k)
    return RecommendResponse(query=query, results=items)
