import json
from dataclasses import dataclass
from pathlib import Path

import chromadb


@dataclass
class RetrievedChunk:
    text: str
    metadata: dict
    score: float


class ChromaVectorStore:
    def __init__(self, persist_dir: Path, collection_name: str = "evisa_knowledge_base"):
        self._persist_dir = Path(persist_dir)
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self._persist_dir / "index_state.json"
        self._client = chromadb.PersistentClient(path=str(self._persist_dir))
        self._collection_name = collection_name
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def is_index_current(self, knowledgebase_hash: str) -> bool:
        state = self._read_state()
        if state is None:
            return False
        if state.get("knowledgebase_hash") != knowledgebase_hash:
            return False
        if int(state.get("chunk_count", 0)) != self._collection.count():
            return False
        return self._collection.count() > 0

    def rebuild_index(
        self,
        *,
        chunks: list[str],
        embeddings: list[list[float]],
        knowledgebase_hash: str,
        source_path: str,
    ) -> None:
        self._client.delete_collection(name=self._collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        metadatas = [
            {
                "chunk_index": index,
                "knowledgebase_hash": knowledgebase_hash,
                "source_path": source_path,
            }
            for index, _ in enumerate(chunks)
        ]
        chunk_ids = [f"{knowledgebase_hash}:{index}" for index, _ in enumerate(chunks)]
        self._collection.upsert(
            ids=chunk_ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        self._write_state({
            "knowledgebase_hash": knowledgebase_hash,
            "chunk_count": len(chunks),
        })

    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        output: list[RetrievedChunk] = []
        for text, metadata, distance in zip(documents, metadatas, distances):
            similarity = 1 - float(distance)
            output.append(
                RetrievedChunk(
                    text=text,
                    metadata=metadata or {},
                    score=round(similarity, 4),
                )
            )
        return output

    def _read_state(self) -> dict | None:
        if not self._state_file.exists():
            return None
        raw_content = self._state_file.read_text(encoding="utf-8").strip()
        if not raw_content:
            return None
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Invalid vector index state file at {self._state_file}. "
                "Delete the file and re-run indexing."
            ) from exc

    def _write_state(self, state: dict) -> None:
        self._state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
