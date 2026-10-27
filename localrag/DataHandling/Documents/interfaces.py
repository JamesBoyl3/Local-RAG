from dataclasses import dataclass
from typing import Protocol, Self


@dataclass
class DocumentChunk:
    """
    This dataclass contains the information needed so that the RAG Application can use and citate the information within the chunk.
    """

    id: int
    src: str
    title: str
    content: str
    page_no: str


class DocumentManager(Protocol):
    """
    This Protocol sets out what a document manager should do.
    """

    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type, exc_value, traceback) -> None: ...
    def get_database(self) -> list[DocumentChunk]: ...
    def get_documents(self, ids: list[int]) -> list[DocumentChunk]: ...
    def add_document(self, documents: list[DocumentChunk] | DocumentChunk) -> None: ...
