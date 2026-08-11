from localrag.core import DocumentChunk
from localrag.databases.documentDBs import DocumentDB, SQLManager
from localrag.databases.vectorDBs import VectorDB, FAISSManager

import numpy as np


class DBManager:
    def __init__(self, document_db: DocumentDB, vector_db: VectorDB) -> None:
        self._doc_db = document_db
        self._vector_db = vector_db

    def add_documents(self, docs: list[DocumentChunk]) -> None:

        with self._doc_db as db:
            doc_ids = db.add_documents(docs)
            self._vector_db.add_documents(docs, doc_ids)

    def get_documents_by_search(self, query_vector: np.ndarray) -> list[DocumentChunk]:
        with self._doc_db as db:
            doc_ids = self._vector_db.search(query_vector)
            docs = db.get_documents_by_ids(doc_ids)

        return docs
