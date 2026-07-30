from langchain_text_splitters import RecursiveCharacterTextSplitter

from abc import ABC, abstractmethod

import fitz
import requests

class TextProcessor(ABC):
        def __init__(self, file_loc: str, db_name: str) -> None: 
                self.file_loc = file_loc
                self.db_name = db_name

        @abstractmethod
        def process(self) -> None:
                ...


class PDFProcessor(TextProcessor):
    """
    Downloads a PDF, extracts text, splits it into chunks, and stores them.
    """

    def __init__(self, pdf_url: str, db_name: str = "sites.db") -> None:
        super().__init__(pdf_url, db_name)

    def _download_pdf(self, url: str) -> requests.Response:
        assert url.endswith(".pdf"), "Document is not a pdf"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response

    def _get_pages(self, pdf: fitz.Document) -> list[tuple[int, fitz.Page]]:
        return [(index, pdf.load_page(index)) for index in range(pdf.page_count)]

    def _get_text(self, page) -> str:
        return page.get_text()

    def _chunk_text(self, content: str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return splitter.split_text(content)

    def process(self) -> None:
        pdf = fitz.open(stream=self._download_pdf(self.url).content, filetype="pdf")
        pages = self._get_pages(pdf)
        texts = [self._get_text(page) for _, page in pages]
        page_nos = [page_no for page_no, _ in pages]

        with DBManager(self.db_name) as db:
            for page_no, text in zip(page_nos, texts):
                for chunk in self._chunk_text(text):
                    db.add_document({"url": self.url, "content": chunk, "page": page_no})
