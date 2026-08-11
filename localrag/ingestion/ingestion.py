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
from typing import Self

import logging

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(self, embedding_model: EmbeddingModel) -> None:
        self.embedding_model = embedding_model

    @classmethod
    def create(cls, host: str = "127.0.0.1", port: int = 8081) -> Self:
        embedding_model = EmbeddingModel(host=host, port=port)

        return cls(embedding_model=embedding_model)

    def embed(self, content: str) -> np.ndarray:
        logger.info(f"Embedded {content[:50]}")
        embedding = self.embedding_model.embed(content)
        return embedding

    def process_doc(self, url: str | Path) -> list[DocumentChunk] | None:
        docs = None

        logger.info(f"Docs processed at {url}")

        url_str = str(url)

        # if url_str.startswith("http://") or url_str.startswith("https://"):
        #     docs = WebProcessor().process(url)
        if url_str.endswith(".pdf"):
            docs = PDFProcessor().process(url)
        elif url_str.endswith(".md"):
            docs = MarkdownProcessor().process(url)
        elif url_str.endswith(".txt"):
            docs = TextFileProcessor().process(url)

        return docs
