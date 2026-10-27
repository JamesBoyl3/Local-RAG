from typing import Protocol

import numpy as np


class EmbeddingDB(Protocol):
    """
    This Protocol sets out what an Embedding Manager should do.
    """

    def add_embedding(self, embedding: np.ndarray) -> None: ...
    def search_db(self, query_embedding: np.ndarray) -> list[int]: ...
