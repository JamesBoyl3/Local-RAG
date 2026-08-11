from localrag.databases import SQLManager
from localrag.core import DocumentChunk

from langchain_text_splitters import RecursiveCharacterTextSplitter

from abc import ABC, abstractmethod
from pathlib import Path

import fitz
import requests
from bs4 import BeautifulSoup

import logging

logger = logging.getLogger(__name__)


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100


class TextProcessor(ABC):
    @abstractmethod
    def process(self, url: str | Path) -> list[DocumentChunk]: ...


class PDFProcessor(TextProcessor):
    @staticmethod
    def _download_pdf(url: str | Path) -> requests.Response:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response

    @staticmethod
    def _get_pages(pdf: fitz.Document) -> list[tuple[int, fitz.Page]]:
        return [(index, pdf.load_page(index)) for index in range(pdf.page_count)]

    @staticmethod
    def _get_text(page: fitz.Page) -> str:
        return page.get_text()

    @staticmethod
    def _chunk_text(content: str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        return splitter.split_text(content)

    def process(self, url: str | Path) -> list[DocumentChunk]:
        pdf = fitz.open(stream=self._download_pdf(url).content, filetype="pdf")
        pages = self._get_pages(pdf)
        texts = [self._get_text(page) for _, page in pages]
        page_nos = [page_no for page_no, _ in pages]

        docs = []
        for page_no, text in zip(page_nos, texts):
            for chunk in self._chunk_text(text):
                docs.append(DocumentChunk(src=url, content=chunk, page_no=page_no))

        return docs


class TextFileProcessor(TextProcessor):
    @staticmethod
    def _load_text(url: str | Path) -> str:
        path = Path(url)
        if not path.exists():
            raise FileNotFoundError(f"Text file not found: {path}")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _chunk_text(content: str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        return splitter.split_text(content)

    def process(self, url: str | Path) -> list[DocumentChunk]:
        text = self._load_text(url)
        docs = []
        for i, chunk in enumerate(self._chunk_text(text)):
            docs.append(DocumentChunk(src=url, content=chunk, page_no=i))
        return docs


class MarkdownProcessor(TextProcessor):
    @staticmethod
    def _load_markdown(url: str | Path) -> str:
        path = Path(url)
        if not path.exists():
            raise FileNotFoundError(f"Markdown file not found: {path}")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _chunk_text(content: str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        return splitter.split_text(content)

    def process(self, url: str | Path) -> list[DocumentChunk]:
        text = self._load_markdown(url)
        docs = []
        for i, chunk in enumerate(self._chunk_text(text)):
            docs.append(DocumentChunk(src=url, content=chunk, page_no=i))
        return docs


class WebProcessor(TextProcessor):
    @staticmethod
    def _fetch_page(url: str | Path) -> str:
        response = requests.get(str(url), timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)

    @staticmethod
    def _chunk_text(content: str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        return splitter.split_text(content)

    def process(self, url: str | Path) -> list[DocumentChunk]:
        text = self._fetch_page(url)
        docs = []
        for i, chunk in enumerate(self._chunk_text(text)):
            docs.append(DocumentChunk(src=url, content=chunk, page_no=i))
        return docs
