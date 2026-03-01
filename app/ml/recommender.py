# app/ml/recommender.py
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import CONFIG
from app.data.repository import load_recipes, load_precomputed_embeddings, get_embedding_for_query
from app.data.text import build_combined_text


def recommend(query: str, df: pd.DataFrame = None, top_k: int = None) -> pd.DataFrame:
    """
    Get recipe recommendations for a query using precomputed embeddings.
    
    Args:
        query: User's search query (ingredients or recipe name)
        df: Recipes DataFrame (optional, loads from disk if not provided)
        top_k: Number of recommendations to return (default: CONFIG.TOP_K_DEFAULT)
    
    Returns:
        DataFrame of recommended recipes (top_k rows)
    """
    if top_k is None:
        top_k = CONFIG.TOP_K_DEFAULT
    
    if df is None:
        df = load_recipes()
    
    # Load precomputed embeddings
    embeddings, metadata = load_precomputed_embeddings()
    
    # Get embedding for query
    query_embedding = get_embedding_for_query(query)
    
    # Compute cosine similarity
    similarities = cosine_similarity(
        query_embedding.reshape(1, -1),
        embeddings
    )[0]
    
    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    # Return top-k recipes
    return df.iloc[top_indices].reset_index(drop=True)


def filter_recipes(
    df: pd.DataFrame,
    cuisine: str = "Any",
    course: str = "Any",
    diet: str = "Any",
    max_time: int = None,
) -> pd.DataFrame:
    """
    Filter recipes by cuisine, course, diet, and max cooking time.
    
    Args:
        df: Recipes DataFrame
        cuisine: Filter by cuisine (or "Any")
        course: Filter by course (or "Any")
        diet: Filter by diet (or "Any")
        max_time: Maximum cooking time in minutes
    
    Returns:
        Filtered DataFrame
    """
    results = df.copy()
    
    if cuisine != "Any":
        results = results[results["Cuisine"] == cuisine]
    
    if course != "Any":
        results = results[results["Course"] == course]
    
    if diet != "Any":
        results = results[results["Diet"] == diet]
    
    if max_time is not None:
        results = results[results["TotalTimeInMins"] <= max_time]
    
    return results.reset_index(drop=True)
