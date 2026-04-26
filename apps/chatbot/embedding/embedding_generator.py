import os

from fastembed import TextEmbedding


class EmbeddingGenerator:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        self._embedder = TextEmbedding(model_name=self.model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [vector.tolist() for vector in self._embedder.embed(texts)]

    def embed_query(self, query: str) -> list[float]:
        query_text = query.strip()
        if not query_text:
            raise ValueError("Query text cannot be empty.")
        return self.embed_texts([query_text])[0]
