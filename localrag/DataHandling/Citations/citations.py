
from localrag.core import DocumentChunk

from typing import Protocol

class CitationGenerator(Protocol):
	def in_text(self) -> str: ...
	def bibliography(self) -> str: ...


class APAGenerator(CitiationGenerator):
	def in_text(self) -> str: ...

	def bibliography(self, answer: str, documents: list[DocumentChunk]) -> str:
		answer += "\n\nSources:\n"

		for document in documents:
			answer += f"[{i}] {document.author} ({document.year}) {document.title} p.{document.page_no}\n"

		return answer
