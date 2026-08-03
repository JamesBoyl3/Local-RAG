from localrag.ingestion.Embeddings import EmbeddingModel
from localrag.ingestion.Processors import PDFProcessor

import logging
logger = logging.getLogger(__name__)

class IngestionPipeline:
	def __init__(self, embeddingModel: EmbeddingModel) -> None:
		self.embeddingModel = embeddingModel

	@classmethod
	def create(cls, model_loc: str|Path) -> self:
		embeddingModel = EmbeddingModel(model_loc)
		
		return cls(
			embeddingModel=embeddingModel
			)

	def embed(self, content: str) -> None:
		logger.info(embedding := self.embeddingModel.embed(content))
		return embedding

	
	def process_doc(self, url: str) -> list[DocumentChunk]:
		logger.info(f"Doc processed at {url}")

		if url.endswith(".pdf"):
			docs = PDFProcessor.process(url)

		return docs
