import os


def _as_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


ENABLE_EXPERIMENTAL_RECOMMENDER = _as_bool("ENABLE_EXPERIMENTAL_RECOMMENDER")
ENABLE_NEW_UI = _as_bool("ENABLE_NEW_UI")
ENABLE_API_BACKEND = _as_bool("ENABLE_API_BACKEND")
