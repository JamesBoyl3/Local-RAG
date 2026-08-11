from __future__ import annotations

from pathlib import Path

import numpy as np
import requests

from localrag.core.llama_server import get_session

import logging

logger = logging.getLogger(__name__)


class EmbeddingModel:
    def __init__(self, host: str = "127.0.0.1", port: int = 8081) -> None:
        self._host = host
        self._port = port
        self._url = f"http://{host}:{port}/v1/embeddings"
        self._session = get_session()

    def embed(self, texts: str | list[str]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        response = self._session.post(
            self._url,
            json={"input": texts},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        vectors = [np.array(item["embedding"], dtype=np.float32) for item in data["data"]]

        stacked = np.stack(vectors, axis=0)
        norms = np.linalg.norm(stacked, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        normalized = stacked / norms

        return normalized
