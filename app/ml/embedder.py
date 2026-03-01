# app/ml/embedder.py
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

from app.core.config import CONFIG


@st.cache_resource(show_spinner=False)
def load_embedder() -> SentenceTransformer:
    # Fast, retrieval-tuned sentence embedding model
    model = SentenceTransformer(CONFIG.EMBED_MODEL_NAME)
    return model


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Returns float32 numpy embeddings of shape (n_texts, dim).
    """
    model = load_embedder()
    # normalize_embeddings=True makes cosine similarity faster & stable
    emb = model.encode(
        texts,
        batch_size=CONFIG.BATCH_SIZE,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return emb.astype("float32")