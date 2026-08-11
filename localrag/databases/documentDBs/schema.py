from localrag.core import DocumentChunk

from abc import ABC, abstractmethod
from typing import Self


class DocumentDB(ABC):
    def __init__(self) -> None: ...

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return

    @abstractmethod
    def get_documents(self) -> list[DocumentChunk]: ...

    @abstractmethod
    def get_documents_by_ids(self) -> list[DocumentChunk]: ...

    @abstractmethod
    def add_document(self) -> None: ...
