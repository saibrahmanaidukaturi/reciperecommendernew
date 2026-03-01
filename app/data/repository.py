# app/data/repository.py
import os
import json
import pickle
from pathlib import Path
from typing import Tuple

import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data(show_spinner=False)
def load_recipes() -> pd.DataFrame:
    """Load recipes from CSV file."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    csv_path = base_dir / "data" / "food.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Recipe file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Ensure required columns exist
    required_cols = [
        "RecipeName", "Ingredients", "TotalTimeInMins",
        "Cuisine", "Course", "Diet", "Instructions", "URL"
    ]
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
    
    # Clean numeric columns
    df["TotalTimeInMins"] = pd.to_numeric(df["TotalTimeInMins"], errors="coerce").fillna(0).astype(int)
    
    return df


@st.cache_data(show_spinner=False)
def load_precomputed_embeddings() -> Tuple[np.ndarray, dict]:
    """
    Load precomputed embeddings from disk.
    
    Returns:
        Tuple of (embeddings_array, metadata_dict)
    
    Raises:
        FileNotFoundError: If embeddings don't exist (run precomputation script first)
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    embeddings_dir = base_dir / "data" / "embeddings"
    
    # Try pickle first (faster)
    pickle_path = embeddings_dir / "embeddings.pkl"
    if pickle_path.exists():
        with open(pickle_path, "rb") as f:
            data = pickle.load(f)
        return data["embeddings"], data["metadata"]
    
    # Fallback to numpy + json
    embeddings_path = embeddings_dir / "embeddings.npy"
    metadata_path = embeddings_dir / "metadata.json"
    
    if not embeddings_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            f"Precomputed embeddings not found at {embeddings_dir}. "
            "Run: python -m scripts.precompute_embeddings"
        )
    
    embeddings = np.load(embeddings_path)
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    return embeddings, metadata


def get_embedding_for_query(query_text: str) -> np.ndarray:
    """
    Compute embedding for a single query text (user's search).
    This is still done on-the-fly, but only for ONE query, not all recipes.
    
    Args:
        query_text: User's search query (ingredients or recipe name)
    
    Returns:
        1D numpy array (embedding_dim,)
    """
    from sentence_transformers import SentenceTransformer
    from app.core.config import CONFIG
    
    # Load model (cached by Streamlit)
    model = _load_embedding_model()
    
    # Compute embedding for single query
    embedding = model.encode(
        [query_text],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )[0]
    
    return embedding


@st.cache_resource(show_spinner=False)
def _load_embedding_model():
    """Load embedding model (cached across sessions)."""
    from sentence_transformers import SentenceTransformer
    from app.core.config import CONFIG
    
    return SentenceTransformer(CONFIG.EMBED_MODEL_NAME)
