from locrag.databases import SQLManager
from locrag.core import DocumentChunk

from langchain_text_splitters import RecursiveCharacterTextSplitter

from abc import ABC, abstractmethod
from pathlib import Path

import fitz
import requests

import logging
logger = logging.getLogger(__name__)

class TextProcessor(ABC):
	@abstractmethod
	def _chunk_text(self) -> list[str]:
		...

	@abstractmethod
	def process(self) -> None:
		...


class PDFProcessor(TextProcessor): 
	@staticmethod
	def _download_pdf(url: str|Path) -> requests.Response:
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
		splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
		return splitter.split_text(content)

	def process(self, url: str|Path) -> list[DocumentChunk]:
		pdf = fitz.open(stream=self._download_pdf(url).content, filetype="pdf")
		pages = self._get_pages(pdf)
		texts = [self._get_text(page) for _, page in pages]
		page_nos = [page_no for page_no, _ in pages]

		docs = []
		for page_no, text in zip(page_nos, texts):
			for chunk in self._chunk_text(text):
				docs.append(DocumentChunk(src=url, content=chunk, page_no=page_no))
	
		return docs
