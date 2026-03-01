# scripts/precompute_embeddings.py
"""
Precompute embeddings for all recipes and save to disk.
Run this script whenever the recipe dataset changes.

Usage:
    python -m scripts.precompute_embeddings
"""
import os
import sys
import json
import pickle
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import CONFIG
from app.data.repository import load_recipes
from app.data.text import build_combined_text


def get_project_root() -> Path:
    """Get project root directory."""
    return PROJECT_ROOT


def compute_embeddings(model: SentenceTransformer, texts: list[str], batch_size: int = 32) -> np.ndarray:
    """
    Compute embeddings for a list of texts using batching.
    
    Args:
        model: SentenceTransformer model
        texts: List of text strings to embed
        batch_size: Number of texts to process in each batch
    
    Returns:
        Numpy array of embeddings (n_texts x embedding_dim)
    """
    all_embeddings = []
    
    print(f"Computing embeddings for {len(texts)} recipes...")
    print(f"Batch size: {batch_size}, Model: {CONFIG.EMBED_MODEL_NAME}")
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        print(f"  Processing batch {batch_num}/{total_batches}...")
        embeddings = model.encode(
            batch,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,  # L2 normalize for cosine similarity
        )
        all_embeddings.append(embeddings)
    
    result = np.vstack(all_embeddings)
    print(f"✓ Generated embeddings with shape: {result.shape}")
    return result


def save_embeddings(embeddings: np.ndarray, texts: list[str], recipe_ids: list[str], output_dir: Path) -> None:
    """
    Save embeddings and metadata to disk.
    
    Creates:
        - embeddings.npy: The embedding matrix
        - metadata.json: Mapping of recipe indices to recipe IDs and texts
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save embeddings as numpy array
    embeddings_path = output_dir / "embeddings.npy"
    np.save(embeddings_path, embeddings)
    print(f"✓ Saved embeddings to {embeddings_path}")
    
    # Save metadata
    metadata = {
        "model_name": CONFIG.EMBED_MODEL_NAME,
        "embedding_dim": embeddings.shape[1],
        "num_recipes": len(embeddings),
        "recipes": [
            {"id": recipe_id, "text": text}
            for recipe_id, text in zip(recipe_ids, texts)
        ]
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved metadata to {metadata_path}")
    
    # Also save a pickle version for faster loading (optional)
    pickle_path = output_dir / "embeddings.pkl"
    with open(pickle_path, "wb") as f:
        pickle.dump({
            "embeddings": embeddings,
            "metadata": metadata,
        }, f)
    print(f"✓ Saved pickle cache to {pickle_path}")


def main():
    """Main precomputation pipeline."""
    print("=" * 60)
    print("Recipe Embedding Precomputation")
    print("=" * 60)
    
    # Load recipes
    print("\n1. Loading recipes...")
    df = load_recipes()
    print(f"   Loaded {len(df)} recipes")
    
    if len(df) == 0:
        print("ERROR: No recipes found. Check your data file.")
        sys.exit(1)
    
    # Build combined text for each recipe
    print("\n2. Building combined text for embeddings...")
    texts = []
    recipe_ids = []
    
    for idx, row in df.iterrows():
        combined_text = build_combined_text(row)
        texts.append(combined_text)
        recipe_ids.append(str(idx))  # Use row index as ID
    
    print(f"   Built {len(texts)} text entries")
    
    # Load embedding model
    print(f"\n3. Loading embedding model: {CONFIG.EMBED_MODEL_NAME}")
    model = SentenceTransformer(CONFIG.EMBED_MODEL_NAME)
    print(f"   ✓ Model loaded (embedding dim: {model.get_sentence_embedding_dimension()})")
    
    # Compute embeddings
    print("\n4. Computing embeddings...")
    embeddings = compute_embeddings(model, texts, batch_size=CONFIG.BATCH_SIZE)
    
    # Determine output directory
    output_dir = get_project_root() / "data" / "embeddings"
    
    # Save embeddings
    print(f"\n5. Saving embeddings to {output_dir}...")
    save_embeddings(embeddings, texts, recipe_ids, output_dir)
    
    # Verify
    print("\n6. Verifying saved embeddings...")
    loaded = np.load(output_dir / "embeddings.npy")
    assert loaded.shape == embeddings.shape, "Embedding shape mismatch!"
    print(f"   ✓ Verification passed: {loaded.shape}")
    
    print("\n" + "=" * 60)
    print("✓ Precomputation complete!")
    print(f"  Embeddings saved to: {output_dir}")
    print(f"  Total recipes: {len(embeddings)}")
    print(f"  Embedding dimension: {embeddings.shape[1]}")
    print("=" * 60)


if __name__ == "__main__":
    main()
