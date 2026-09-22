from typing import List, Optional
from backend.config.settings import get_settings
from backend.retrieval.models import Chunk, Document


class TextChunker:
    """
    Configurable boundary-aware text chunker with sliding window overlap.
    Preserves natural sentence and paragraph boundaries when slicing documents.
    """

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        settings = get_settings()
        self.chunk_size = chunk_size if chunk_size is not None else settings.DEFAULT_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else settings.DEFAULT_CHUNK_OVERLAP

        if self.chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {self.chunk_size}")
        if self.chunk_overlap < 0:
            raise ValueError(f"chunk_overlap cannot be negative, got {self.chunk_overlap}")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be strictly less than chunk_size ({self.chunk_size})"
            )

    def _find_breakpoint(self, text: str, start: int, end: int) -> int:
        """
        Find the best natural breakpoint before or at 'end' starting from start + chunk_overlap.
        Prefers paragraph breaks, newlines, sentence ends, and whitespace in order.
        """
        min_split = start + self.chunk_overlap
        search_window = text[min_split:end]

        # 1. Paragraph break (\n\n)
        last_para = search_window.rfind("\n\n")
        if last_para != -1:
            return min_split + last_para + 2

        # 2. Line break (\n)
        last_newline = search_window.rfind("\n")
        if last_newline != -1:
            return min_split + last_newline + 1

        # 3. Sentence boundaries (., ?, !, or Devanagari danda ।)
        for punct in [". ", "? ", "! ", "। ", ".\n", "?\n", "!\n"]:
            last_punct = search_window.rfind(punct)
            if last_punct != -1:
                return min_split + last_punct + len(punct)

        # 4. Word boundary (space)
        last_space = search_window.rfind(" ")
        if last_space != -1:
            return min_split + last_space + 1

        # Fallback to hard character cutoff
        return end

    def chunk_document(self, document: Document) -> List[Chunk]:
        """
        Slice a single Document into a sequence of overlapping Chunks.
        """
        text = document.text.strip()
        if not text:
            return []

        text_len = len(text)
        chunks: List[Chunk] = []
        start = 0
        chunk_index = 0

        while start < text_len:
            target_end = min(start + self.chunk_size, text_len)

            if target_end == text_len:
                actual_end = text_len
            else:
                actual_end = self._find_breakpoint(text, start, target_end)

            chunk_slice = text[start:actual_end].strip()
            if chunk_slice:
                chunk_meta = dict(document.metadata)
                chunk_meta.update({
                    "title": document.title,
                    "filename": document.filename,
                    "source": document.source,
                    "document_type": document.document_type,
                    "chunk_size_chars": len(chunk_slice),
                })

                chunk = Chunk(
                    chunk_id=f"{document.document_id}_c{chunk_index}",
                    document_id=document.document_id,
                    chunk_index=chunk_index,
                    chunk_text=chunk_slice,
                    char_start=start,
                    char_end=actual_end,
                    metadata=chunk_meta,
                )
                chunks.append(chunk)
                chunk_index += 1

            if actual_end >= text_len:
                break

            # Calculate next start position using overlap
            next_start = actual_end - self.chunk_overlap
            # Guarantee forward progress
            if next_start <= start:
                next_start = start + 1
            start = next_start

        return chunks

    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        """
        Slice a list of Documents into Chunks.
        """
        all_chunks: List[Chunk] = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks
