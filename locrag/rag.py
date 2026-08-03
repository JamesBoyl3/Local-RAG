
from locrag.databases import DBManager, SQLManager, FAISSManager
from locrag.generation import LLM
from locrag.ingestion import IngestionPipeline, EmbeddingModel
from locrag.core import Conversation

from pathlib import Path
from typing import Self


class RAGModel:
	def __init__(self, llm: LLM, doc_db: SQLManager, vector_db: FAISSManager, ingestion_pipeline: IngestionPipeline) -> None:
		self._llm = llm
		self._db_manager = DBManager(doc_db, vector_db)
		self._ingestion_pipeline = ingestion_pipeline

		self._conversation = Conversation()

	@classmethod
	def create(cls, gen_model_loc: str|Path, embedding_model_loc: str|Path,  doc_db_loc: str|Path=Path("./documents.db"), vector_db_loc: str|Path=Path("./embedding.faiss")) -> Self:
		llm = LLM(Path(gen_model_loc))
		doc_db = SQLManager(Path(doc_db_loc))
		vector_db = FAISSManager(Path(vector_db_loc))
		ingestion_pipeline = IngestionPipeline(EmbeddingModel(Path(embedding_model_loc)))

		return cls(
			llm=llm,
			doc_db=doc_db,
			vector_db=vector_db,
			ingestion_pipeline=ingestion_pipeline
			)

	def _build_prompt(self, query: str, relevant_docs: list[DocumentChunk]) -> str:
		context = f"Context:\n"

		for i, doc in enumerate(relevant_docs):
			context += f"Source {i}:\n\nDocument source: {doc.src}\nSourced page: {doc.page_no}\nSource content: {doc.content}\n\n"
		
		context += f"Query:\n{query}"

		return context

	def ingest_src(self, src: str | Path) -> None:
		docs = self._ingestion_pipeline.process(src)
		
		for doc in docs:
			doc.embedding = self._ingestion_pipeline.embed(doc.content)

		self._db_manager.add_documents(docs)


	def generate_response(self, query: str) -> str:
		query_vector = self._ingestion_pipeline.embed(query)
		relevant_doc_ids = self._db_manager.get_documents_by_search(query_vector)
		
		relevant_docs = self._db_manager.get_documents_by_ids(relevant_doc_ids)

		messages = self._conversation.messages.copy()
		messages.append(self._build_prompt(query, relevant_docs))
		
		self.conversation.add_message("user", query)
		self._conversation.add_message("assistant", answer := self._llm.answer(messages))

		return answer
