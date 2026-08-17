from localrag.ingestion.Embeddings import EmbeddingModel
from localrag.ingestion.Processors import (
    PDFProcessor,
    TextFileProcessor,
    MarkdownProcessor,
    WebProcessor,
)
from localrag.core import DocumentChunk

import numpy as np

from pathlib import Path

import logging

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(self, embedding_model: EmbeddingModel) -> None:
        self.embedding_model = embedding_model

    def embed(self, content: str) -> np.ndarray:
        embedding = self.embedding_model.embed(content)
        logger.info(f"Embedded {content[:50]}")
        return embedding

    def process_doc(self, url: str) -> list[DocumentChunk] | None:
        docs = None

        # if url_str.startswith("http://") or url_str.startswith("https://"):
        #     docs = WebProcessor().process(url)
        if url.endswith(".pdf"):
            docs = PDFProcessor().process(url)
        elif url.endswith(".md"):
            docs = MarkdownProcessor().process(url)
        elif url.endswith(".txt"):
            docs = TextFileProcessor().process(url)

        logger.info(f"Docs processed at {url}")

        return docs
