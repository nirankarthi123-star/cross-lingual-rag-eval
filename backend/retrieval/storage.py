import json
from pathlib import Path
from typing import List
from backend.retrieval.models import Chunk, Document


class ProcessedStorage:
    """
    Handles saving and loading processed Documents and Chunks in JSONL format.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.documents_file = self.output_dir / "documents.jsonl"
        self.chunks_file = self.output_dir / "chunks.jsonl"

    def _ensure_dir(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_documents(self, documents: List[Document]) -> Path:
        """Save documents to documents.jsonl."""
        self._ensure_dir()
        temp_file = self.documents_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            for doc in documents:
                f.write(doc.model_dump_json() + "\n")
        temp_file.replace(self.documents_file)
        return self.documents_file

    def save_chunks(self, chunks: List[Chunk]) -> Path:
        """Save chunks to chunks.jsonl."""
        self._ensure_dir()
        temp_file = self.chunks_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            for chunk in chunks:
                f.write(chunk.model_dump_json() + "\n")
        temp_file.replace(self.chunks_file)
        return self.chunks_file

    def load_documents(self) -> List[Document]:
        """Load documents from documents.jsonl."""
        if not self.documents_file.exists():
            return []
        documents: List[Document] = []
        with open(self.documents_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    documents.append(Document.model_validate_json(line))
        return documents

    def load_chunks(self) -> List[Chunk]:
        """Load chunks from chunks.jsonl."""
        if not self.chunks_file.exists():
            return []
        chunks: List[Chunk] = []
        with open(self.chunks_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    chunks.append(Chunk.model_validate_json(line))
        return chunks
