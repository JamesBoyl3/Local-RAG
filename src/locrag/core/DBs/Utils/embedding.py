
from sentence_transformers import SentenceTransformer

import numpy as np

class EmbeddingModel:
        def __init__(self) -> None:
                self.__embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")

                return
        
        def embedd(self, texts: str | list[str]) -> "NDArray[float32]":
                vectors = self.__embedder.encode(texts, normalize_embeddings=True, convert_to_numpy=True).astype("float32")
                return vectors

        def get_similarity(self, embeddings_1, embeddings_2):
                return embeddings_1 @ embeddings_2.T


if __name__ == "__main__":
#       embeddingModel = EmbeddingModel()

        #sentences_1 = ["Hello World", "First Coding statement"]
        #sentences_2 = ["Art is cool", "The last art piece"]

        sentences_1 = "Hello World"     
        sentences_2 = "Bye World"

#       embeddings_1 = embeddingModel.embedd(sentences_1)
#       embeddings_2 = embeddingModel.embedd(sentences_2)

        #print(f"{embeddings_1=}\n{embeddings_2=}")

#       similarity = embeddingModel.get_similarity(embeddings_1, embeddings_2)

        #print(f"{similarity}")

        embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
        v = embedder.encode("Hello World!")
        print(v.shape)
