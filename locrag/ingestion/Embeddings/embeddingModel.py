
from sentence_transformers import SentenceTransformer
from pathlib import Path

import numpy as np

class EmbeddingModel:
        def __init__(self, model_loc: Path) -> None:
                self._embedder = SenetenceTransformer(str(model_loc))

	def embed(self, texts: str | list[str]) -> "NDArray[float32]":
                vectors = self.__embedder.encode(texts, normalize_embeddings=True, convert_to_numpy=True).astype("float32")
                return vectors
