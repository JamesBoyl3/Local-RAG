
from localRAG.core.DBs import DBManager

from abc import ABC, abstractmethod


class WebCrawler(ABC):
	def __init__(self, db_name: str, url: str) -> None:
		self.db = DBManager(db_name)
		self.url = url
	
	@abstractmethod
	def scrape_page() -> None:
		...

	@abstractmethod
	def crawl_site() -> None:
		...

	

class PDFCrawler(WebCrawler):
    """
    Basic crawler that discovers PDF links from a single page.
    """

    def __init__(self, db_name: str, url: str | None = None) -> None:
        super().__init__(db_name, url if url is not None else "https://www.iea-dhc.org/home")

    def _get_unvisited_links(self, url: str) -> list[str]:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(response.text, "html.parser")
        page_links: list[str] = [
            str(href)
            for href in (a.get("href") for a in soup.find_all("a"))
            if href is not None
        ]
        visited = set(self._get_visited_links())
        return [link for link in page_links if link not in visited]

    def _get_visited_links(self) -> list[str]:
        with self.db as db:
            return [row["url"] for row in db.get_documents("url")]

    def scrape_page(self) -> None:
        links = self._get_unvisited_links(self.url)
        pdf_links = [link for link in links if link.endswith(".pdf")]

        for pdf_link in pdf_links:
            PDFProcessor(pdf_link).process()

        return

    def crawl_site(self) -> None:
        ...
