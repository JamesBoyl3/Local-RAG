from sentence_transformers import SentenceTransformer
from pathlib import Path

import numpy as np

import logging

logger = logging.getLogger(__name__)


class EmbeddingModel:
    def __init__(self, model_loc: str | Path) -> None:
        logger.debug(f"Loading Embedding Model at {model_loc}")
        self._embedder = SentenceTransformer(str(model_loc))

    def embed(self, texts: str | list[str]) -> "NDArray[float32]":
        vectors = self._embedder.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True
        ).astype("float32")
        return vectors

    def save_model(self, new_model_loc: str | Path) -> str | Path:
        self._embedder.save(new_model_loc)

        return new_model_loc
