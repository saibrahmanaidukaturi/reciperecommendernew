# app/ml/recommender.py
import os
import hashlib
import numpy as np
import pandas as pd
import streamlit as st

from app.core.config import CONFIG
from app.data.text import build_combined_text
from app.ml.embedder import embed_texts


def _project_root() -> str:
    # app/ml/recommender.py -> app/ml -> app -> project root
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _hash_texts(texts: list[str]) -> str:
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8", errors="ignore"))
    return h.hexdigest()


def _emb_path(texts_hash: str) -> str:
    # store embeddings under ./data so they persist across runs
    return os.path.join(_project_root(), "data", f"embeddings_{texts_hash}.npy")


@st.cache_data(show_spinner=False)
def compute_recipe_embeddings(combined_texts: list[str]) -> np.ndarray:
    """
    Loads embeddings from disk if present; otherwise computes once and saves.
    Cached by Streamlit too, but disk makes it persist across restarts.
    """
    data_dir = os.path.join(_project_root(), "data")
    os.makedirs(data_dir, exist_ok=True)

    texts_hash = _hash_texts(combined_texts)
    path = _emb_path(texts_hash)

    if os.path.exists(path):
        return np.load(path)

    embeddings = embed_texts(combined_texts)
    np.save(path, embeddings)
    return embeddings


def recommend(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if "combined" not in df.columns:
        df = df.copy()
        df["combined"] = build_combined_text(df)

    combined_list = df["combined"].fillna("").tolist()

    # dataset embeddings (fast to load after first compute)
    recipe_embeddings = compute_recipe_embeddings(combined_list)

    # query embedding (very fast)
    q_emb = embed_texts([query.strip()])[0]  # shape (dim,)

    # Since embeddings are normalized, cosine similarity == dot product
    scores = recipe_embeddings @ q_emb  # shape (n,)

    k = min(CONFIG.TOP_K_DEFAULT, len(df))
    idx = np.argpartition(scores, -k)[-k:]          # top-k unsorted
    idx = idx[np.argsort(scores[idx])[::-1]]        # sort top-k descending

    return df.iloc[idx].reset_index(drop=True)


def filter_recipes(
    df: pd.DataFrame,
    cuisine: str,
    course: str,
    diet: str,
    max_total_time: int,
) -> pd.DataFrame:
    results = df[df["TotalTimeInMins"] <= int(max_total_time)]
    if cuisine != "Any":
        results = results[results["Cuisine"] == cuisine]
    if course != "Any":
        results = results[results["Course"] == course]
    if diet != "Any":
        results = results[results["Diet"] == diet]
    return results.reset_index(drop=True)