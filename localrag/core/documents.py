from dataclasses import dataclass

import numpy as np


@dataclass
class DocumentChunk:
    src: str
    author: str
    content: str
    page_no: int
    embedding: np.ndarray | None = None
