#from __future__ import annotations

from locrag.core import DocumentChunk

from pathlib import Path

import faiss
import numpy as np

import logging
logger = logging.getLogger(__name__)

class FAISSManager:
    """Simple FAISS-backed vector store wrapper for retrieving document chunks."""

    def __init__(self, dimension: int=384, index_path: str|None=None) -> None:
        self.dimension = dimension
        self.index_path = index_path or f"{Path(db_name).stem}.faiss"
	self.index = self._load_or_create_index()

    def _load_or_create_index(self) -> faiss.IndexIDMap:
        if Path(self.index_path).exists():
            index = faiss.read_index(self.index_path)
            if not isinstance(index, faiss.IndexIDMap):
                raise TypeError("Existing index is not a FAISS ID-mapped index")
            return index

        return faiss.IndexIDMap(faiss.IndexFlatL2(self.dimension))

    def add_documents(self, docs: list[DocumentChunk], ids: list[int] | None = None) -> None:
        embeddings = [doc.embedding for doc in docs]
	vector_ids = ids if ids is not None else list(range(len(texts)))
        self.index.add_with_ids(vectors, np.array(vector_ids, dtype=np.int64))
        faiss.write_index(self.index, self.index_path)

#    def search(self, query: str, top_k: int = 4) -> list[tuple[int, float]]:
#        query_vector = self.embedding_model.embedd(query).astype("float32")
#        query_vector = query_vector.reshape(1, -1)
#        distances, doc_ids = self.index.search(query_vector, top_k)
#        return [(int(doc_id), float(distance)) for doc_id, distance in zip(doc_ids[0], distances[0])]

    def search(self, query_vector: np.ndarray, top_k: int=4) -> np.ndarray:
	distances, doc_ids =  self.index.search(query_vector, top_k)
	
	logger.info("Distances: %s\nIDS: %s" % (distances, doc_ids))

	return doc_ids
