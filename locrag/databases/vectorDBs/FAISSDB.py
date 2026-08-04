#from __future__ import annotations

from locrag.core import DocumentChunk

from pathlib import Path
import os 

import faiss
import numpy as np

import logging
logger = logging.getLogger(__name__)

class FAISSManager:
	"""Simple FAISS-backed vector store wrapper for retrieving document chunks."""

	def __init__(self, dimension: int=384, index_path: str|None=None) -> None:
		self.dimension = dimension
		self.index_path = str(index_path) or "embeddings.faiss"
		self.index = self._load_or_create_index()

	def _load_or_create_index(self) -> faiss.IndexIDMap:
		if os.path.exists(Path(self.index_path)):
			index = faiss.read_index(self.index_path)

			if not isinstance(index, faiss.IndexIDMap):
				raise TypeError("Existing index is not a FAISS ID-mapped index")

			return index

		return faiss.IndexIDMap(faiss.IndexFlatL2(self.dimension))

	def add_documents(self, docs: list[DocumentChunk], ids: list[int] | None = None) -> None:
		embeddings = [doc.embedding for doc in docs]
		embedding_ids = ids if ids is not None else list(range(len(texts)))
		self.index.add_with_ids(np.array(embeddings, dtype=np.float32), np.array(embedding_ids, dtype=np.int64))
		faiss.write_index(self.index, self.index_path)

	def search(self, query_vector: np.ndarray, top_k: int=4) -> np.ndarray:
		query_vector = query_vector.reshape(1, -1)
		logger.debug(query_vector.shape)
		distances, doc_ids =  self.index.search(query_vector, top_k)

		logger.info("Distances: %s\nIDS: %s" % (distances, doc_ids))

		return doc_ids
