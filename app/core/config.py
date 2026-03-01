# app/core/config.py
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    TOP_K_DEFAULT: int = 12
    DEFAULT_MAX_TIME: int = 360

    # Sentence embedding model (FAST)
    EMBED_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    BATCH_SIZE: int = 128  # MiniLM can handle large batches on CPU

CONFIG = AppConfig()