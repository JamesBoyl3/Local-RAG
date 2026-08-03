from locrag.ingestion.Embeddings import EmbeddingModel
from locrag.ingestion.Processors import PDFProcessor
from locrag.core import DocumentChunk


from pathlib import Path
from typing import Self

import logging
logger = logging.getLogger(__name__)


class IngestionPipeline:
	def __init__(self, embeddingModel: EmbeddingModel) -> None:
		self.embeddingModel = embeddingModel

	@classmethod
	def create(cls, model_loc: str|Path) -> Self:
		embeddingModel = EmbeddingModel(model_loc)
		
		return cls(
			embeddingModel=embeddingModel
			)

	def embed(self, content: str) -> None:
		logger.info(f"Embedded {content[:50]}")
		embedding = self.embeddingModel.embed(content)
		return embedding

	
	def process_doc(self, url: str) -> list[DocumentChunk]:
		logger.info(f"Doc processed at {url}")

		if url.endswith(".pdf"):
			docs = PDFProcessor.process(url)

		return docs
