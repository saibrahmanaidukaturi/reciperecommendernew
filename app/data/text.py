# app/data/text.py
"""Text processing utilities for building recipe input for embeddings."""

from typing import Union
import pandas as pd


def build_combined_text(row: Union[pd.Series, dict]) -> str:
    """
    Build a combined text string from recipe fields for embedding.
    
    Combines: RecipeName, Ingredients, Cuisine, Course, Diet, TotalTimeInMins
    
    Args:
        row: A row from the recipes DataFrame (or dict with same keys)
    
    Returns:
        Combined text string (lowercased, cleaned)
    """
    fields = [
        str(row.get("RecipeName", "")),
        str(row.get("Ingredients", "")),
        str(row.get("Cuisine", "")),
        str(row.get("Course", "")),
        str(row.get("Diet", "")),
        str(row.get("TotalTimeInMins", "")),
    ]
    
    combined = " ".join(f for f in fields if f and f.lower() != "nan")
    return combined.lower().strip()


def preprocess_text(text: str) -> str:
    """
    Basic text preprocessing for embeddings.
    
    - Lowercase
    - Remove extra whitespace
    - Remove special characters (keep alphanumeric and spaces)
    """
    import re
    
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = " ".join(text.split())
    return text
