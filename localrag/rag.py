from collections.abc import Generator
from pathlib import Path
from typing import Self

from localrag.core import Conversation, DocumentChunk, LLamaServerConfig, LLMConfig
from localrag.core.llama_server import get_embedding_dim
from localrag.databases import DBManager, FAISSManager, SQLManager
from localrag.generation import LLM
from localrag.ingestion import EmbeddingModel, IngestionPipeline
from localrag.DataHandling import APAGenerator


class RAGModel:
    """
    An orchestator class that manages the different constituents of a RAG system.

    It coordinates the requests to the embedding and generation model to generate answers, and the embedding model and ingestion method to store new documents.
    """

    def __init__(
        self,
        llm: LLM,
        doc_db: SQLManager,
        vector_db: FAISSManager,
        ingestion_pipeline: IngestionPipeline,
    ) -> None:
        self._llm = llm
        self._db_manager = DBManager(doc_db, vector_db)
        self._ingestion_pipeline = ingestion_pipeline
        self._conversation = Conversation()
	self._citation_gen = APAGenerator()

    @classmethod
    def create(
        cls,
        llm_config: LLMConfig,
        llama_server_config: LLamaServerConfig,
        doc_db_path: str | Path = Path("./documents.db"),
        vector_db_path: str | Path = Path("./embedding.faiss"),
    ) -> Self:
        """
        A higher level method to instantiate a RAG class.
        """
        llm = LLM(llama_server_config.HOST_IP, llama_server_config.GEN_PORT, llm_config)

        embedding_model = EmbeddingModel(
            llama_server_config.HOST_IP, llama_server_config.EMBED_PORT
        )

        doc_db = SQLManager(db_path=Path("/srv/documents/documents.db"))

        vector_db = FAISSManager(
            dimension=get_embedding_dim(
                llama_server_config.HOST_IP, llama_server_config.EMBED_PORT
            ),
            index_path=Path("/srv//vectors/vectors.faiss"),
        )

        ingestion_pipeline = IngestionPipeline(embedding_model)

        return cls(
            llm=llm,
            doc_db=doc_db,
            vector_db=vector_db,
            ingestion_pipeline=ingestion_pipeline,
        )

    def _build_prompt(
        self, query: str, relevant_docs: list[DocumentChunk]
    ) -> dict[str, str]:
        context = "Context:\n"

        for i, doc in enumerate(relevant_docs):
            context += f"Source {i}:\n\nDocument source: {doc.src}\nSourced page: {doc.page_no}\nSource content: {doc.content}\n\n"

        context += f"Query:\n{query}"

        return {"role": "user", "content": context}

    def ingest_src(self, src: str | Path) -> None:
        docs = self._ingestion_pipeline.process_doc(src)
        try:
            for doc in docs:
                doc.embedding = self._ingestion_pipeline.embed(doc.content)
            self._db_manager.add_documents(docs)
        except TypeError as e:
            print(e)

    def generate_response(self, query: str) -> str:
        query_vector = self._ingestion_pipeline.embed(query)
        relevant_docs = self._db_manager.get_documents_by_search(query_vector)

        messages = self._conversation.messages.copy()
        
	answer = self.citation_gen.bibliography(self._build_prompt(query, relevant_docs), relevant_docs)

	messages.append(self._build_prompt(query, relevant_docs))

	

        self._conversation.add_message("user", query)
        self._conversation.add_message(
            "assistant", answer := self._llm.get_answer(messages)
        )

        return answer

    def stream_response(self, query: str) -> Generator[str, None, str]:
        query_vector = self._ingestion_pipeline.embed(query)
        relevant_docs = self._db_manager.get_documents_by_search(query_vector)

        messages = self._conversation.messages.copy()
        messages.append(self._build_prompt(query, relevant_docs))

        self._conversation.add_message("user", query)

        full_response = []
        for token in self._llm.stream_answer(messages):
            full_response.append(token)
            yield token

        answer = "".join(full_response)
        self._conversation.add_message("assistant", answer)
        return answer
