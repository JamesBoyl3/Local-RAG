from dataclasses import dataclass

@dataclass
class DocumentChunk:
	src: str
	content: str
	page_no: int
	embedding: np.ndarray|None=None
