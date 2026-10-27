# Interfaces
# Logging
import logging
import os

# File handling
from pathlib import Path

# Embedding Manipulation
import faiss
import numpy as np

from ..Documents.interfaces import DocumentChunk
from .interfaces import EmbeddingDB

logger = logging.getLogger(__name__)


class FAISSManager(EmbeddingDB):
    """This class uses FAISS to implement the EmbeddingDB Protocol."""

    def __init__(self, dimension: int, index_path: Path | str) -> None:
        self.dimension = dimension
        self.index_path = str(index_path)
        self.index = self._load_or_create_index(str(index_path))

    def _load_or_create_index(self) -> faiss.IndexIDMap:
        """
        A
        """
        if os.path.exists(Path(self.index_path)):
            index = faiss.read_index(self.index_path)

            if not isinstance(index, faiss.IndexIDMap):
                raise TypeError("Existing index is not a FAISS ID-mapped index")

            inner = faiss.downcast_index(index.index)
            if inner.d != self.dimension:
                raise ValueError(
                    f"Loaded index dimension {inner.d} does not match expected {self.dimension}"
                )

            logger.info("Loaded existing FAISS index from %s", self.index_path)
            return index

        logger.info("Creating new FAISS index with dimension %d", self.dimension)
        return faiss.IndexIDMap(faiss.IndexFlatIP(self.dimension))

    def add_documents(
        self, docs: list[DocumentChunk], ids: list[int] | None = None
    ) -> None:
        embeddings = [doc.embedding for doc in docs]
        embedding_ids = ids if ids is not None else list(range(len(docs)))

        embeddings_arr = np.array(embeddings, dtype=np.float32)
        ids_arr = np.array(embedding_ids, dtype=np.int64)
        logger.info(
            "embeddings shape: %s, ids shape: %s", embeddings_arr.shape, ids_arr.shape
        )

        self.index.add_with_ids(embeddings_arr, ids_arr)
        self.save()

    def search(self, query_vector: np.ndarray, top_k: int = 4) -> list[int]:
        query_vector = query_vector.reshape(1, -1).astype(np.float32)
        logger.debug(query_vector.shape)
        distances, doc_ids = self.index.search(query_vector, top_k)

        logger.info("Distances: %s\nIDS: %s" % (distances, doc_ids))

        flat_ids = doc_ids.flatten().tolist()
        return [doc_id for doc_id in flat_ids if doc_id != -1]

    def save(self) -> None:
        faiss.write_index(self.index, self.index_path)
        logger.debug("FAISS index saved to %s", self.index_path)

    def __del__(self) -> None:
        if hasattr(self, "index") and hasattr(self, "index_path"):
            try:
                self.save()
            except Exception:
                pass
