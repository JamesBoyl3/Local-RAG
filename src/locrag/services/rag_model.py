
from typing import Any

from localRAG.DBs import DBManager, vectorDB
from localRAG.DataScraping import PDFCrawler
from localRAG.DataProcessing import PDFProcessor

from .embedding import EmbeddingModel

class RAGModel:
    """Coordinate document processing, storage, retrieval and answer generation."""

    def __init__(self, db_name: str = "sites.db", llm: Any | None = None) -> None:
        self.db_name = db_name
        self.db = DBManager(db_name)
        self.processor = PDFProcessor(pdf_url="", db_name=db_name)
        self.vector_db = vectorDB(db_name=db_name)
        self.embedding_model = EmbeddingModel()
        self.llm = llm
        self.crawler = PDFCrawler(db_name=db_name)

    def index_pdf(self, pdf_url: str) -> None:
        self.processor.url = pdf_url
        self.processor.process()

    def index_url(self, url: str) -> None:
        self.crawler.url = url
        self.crawler.crawl_page()

    def add_documents(self, documents: list[dict[str, Any]]) -> None:
        with DBManager(self.db_name) as db:
            stored_docs = []
            vector_ids = []

            for doc in documents:
                doc_id = db.add_document(doc)
                stored_docs.append({**doc, "id": doc_id})
                vector_ids.append(doc_id)

        self.vector_db.add_documents(stored_docs, ids=vector_ids)

    def retrieve(self, query: str, top_k: int = 4) -> list[dict[str, Any]]:
        with DBManager(self.db_name) as db:
            rows = db.get_documents()

        if not rows:
            return []

        ranked_ids = self.vector_db.search(query, top_k=top_k)
        matches = []
        for doc_id, _ in ranked_ids:
            row = next((row for row in rows if row["id"] == doc_id), None)
            if row is None:
                continue
            matches.append(
                {
                    "id": row["id"],
                    "url": row["url"],
                    "content": row["content"],
                    "page": row["page"],
                }
            )
        return matches

    def answer(self, query: str) -> str:
        context_docs = self.retrieve(query)
        context = "\n\n".join(
            f"Source: {doc['url']} | Page: {doc['page']}\n{doc['content']}"
            for doc in context_docs
        )

        if self.llm is not None:
            return self.llm.answer(f"Context:\n{context}\n\nQuestion:\n{query}")

        return context if context else "No relevant documents found."


