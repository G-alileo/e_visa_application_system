import hashlib
import os
import re
import threading
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

from apps.chatbot.embedding.embedding_generator import EmbeddingGenerator
from apps.chatbot.llm.llm_client import LLMClient
from apps.chatbot.vector_database.chroma_db import ChromaVectorStore


@dataclass
class ChatbotResult:
    answer: str
    sources: list[dict]


class RAGChatbot:
    def __init__(self):
        self._knowledgebase_path = self._resolve_knowledgebase_path()
        self._top_k = self._resolve_top_k()
        chroma_path = Path(
            os.getenv(
                "CHROMA_DB_PATH",
                str(settings.BASE_DIR / "apps" / "chatbot" / "vector_database" / "chroma_store"),
            )
        )
        self._embedding_generator = EmbeddingGenerator()
        self._vector_store = ChromaVectorStore(persist_dir=chroma_path)
        self._llm_client = LLMClient()
        self._index_lock = threading.Lock()

    def ask(self, question: str) -> ChatbotResult:
        question_text = question.strip()
        if not question_text:
            raise ValueError("Question cannot be empty.")

        self._ensure_index()
        query_embedding = self._embedding_generator.embed_query(question_text)
        retrieved_chunks = self._vector_store.search(query_embedding=query_embedding, top_k=self._top_k)

        contexts = [chunk.text for chunk in retrieved_chunks]
        answer = self._llm_client.generate_answer(question=question_text, contexts=contexts)
        sources = [
            {
                "chunk_index": chunk.metadata.get("chunk_index"),
                "source_path": chunk.metadata.get("source_path"),
                "score": chunk.score,
                "excerpt": chunk.text[:220].strip(),
            }
            for chunk in retrieved_chunks
        ]
        return ChatbotResult(answer=answer, sources=sources)

    def _ensure_index(self) -> None:
        with self._index_lock:
            knowledge_text = self._read_knowledgebase_text()
            knowledge_hash = hashlib.sha256(knowledge_text.encode("utf-8")).hexdigest()
            if self._vector_store.is_index_current(knowledge_hash):
                return

            chunks = self._chunk_text(knowledge_text)
            if not chunks:
                raise RuntimeError(
                    f"Knowledge base file is empty: {self._knowledgebase_path}. "
                    "Add content before using the chatbot."
                )

            embeddings = self._embedding_generator.embed_texts(chunks)
            self._vector_store.rebuild_index(
                chunks=chunks,
                embeddings=embeddings,
                knowledgebase_hash=knowledge_hash,
                source_path=str(self._knowledgebase_path),
            )

    def _read_knowledgebase_text(self) -> str:
        if not self._knowledgebase_path.exists():
            raise RuntimeError(f"Knowledge base file not found: {self._knowledgebase_path}")
        return self._knowledgebase_path.read_text(encoding="utf-8")

    def _resolve_knowledgebase_path(self) -> Path:
        configured = os.getenv("CHATBOT_KNOWLEDGEBASE_PATH", "").strip()
        if configured:
            return Path(configured)

        default_upper = settings.BASE_DIR / "apps" / "chatbot" / "document_processing" / "knowledgebase.MD"
        default_lower = settings.BASE_DIR / "apps" / "chatbot" / "document_processing" / "knowledgebase.md"
        if default_upper.exists():
            return default_upper
        return default_lower

    def _resolve_top_k(self) -> int:
        raw_value = os.getenv("CHATBOT_TOP_K", "4").strip()
        if raw_value.isdigit():
            return max(1, min(int(raw_value), 10))
        return 4

    def _chunk_text(self, raw_text: str, *, max_chars: int = 900, overlap: int = 120) -> list[str]:
        normalized = raw_text.strip()
        if not normalized:
            return []

        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
        chunks: list[str] = []
        current = ""

        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
            if len(candidate) <= max_chars:
                current = candidate
                continue

            if current:
                chunks.append(current)
                current = ""

            if len(paragraph) <= max_chars:
                current = paragraph
                continue

            start = 0
            while start < len(paragraph):
                end = min(start + max_chars, len(paragraph))
                window = paragraph[start:end].strip()
                if window:
                    chunks.append(window)
                if end == len(paragraph):
                    break
                start = max(end - overlap, 0)

        if current:
            chunks.append(current)
        return chunks


_rag_instance: RAGChatbot | None = None
_rag_instance_lock = threading.Lock()


def get_rag_chatbot() -> RAGChatbot:
    global _rag_instance
    if _rag_instance is None:
        with _rag_instance_lock:
            if _rag_instance is None:
                _rag_instance = RAGChatbot()
    return _rag_instance
