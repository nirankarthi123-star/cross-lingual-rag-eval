import csv
import hashlib
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
import pypdf

from backend.retrieval.cleaner import clean_text
from backend.retrieval.models import Document


class DocumentLoadingError(Exception):
    """Base exception for document loading failures."""
    pass


class UnsupportedFileTypeError(DocumentLoadingError):
    """Raised when encountering an unsupported file extension."""
    pass


def generate_doc_id(source: str, differentiator: str = "") -> str:
    """Generate a stable deterministic document ID based on source path and differentiator."""
    raw = f"{source}:{differentiator}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class BaseLoader(ABC):
    """Abstract base class for all file-type specific document loaders."""

    @abstractmethod
    def load(self, file_path: Path) -> List[Document]:
        """Load and parse the given file into one or more Document instances."""
        pass


class TXTLoader(BaseLoader):
    """Loader for plain text files (.txt)."""

    def load(self, file_path: Path) -> List[Document]:
        if not file_path.exists():
            raise DocumentLoadingError(f"File does not exist: {file_path}")

        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        raw_text = None

        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    raw_text = f.read()
                break
            except (UnicodeDecodeError, OSError):
                continue

        if raw_text is None:
            raise DocumentLoadingError(f"Unable to decode text file with supported encodings: {file_path}")

        cleaned = clean_text(raw_text)
        first_line = cleaned.split("\n")[0].strip() if cleaned else ""
        title = first_line[:100] if first_line else file_path.stem

        doc = Document(
            document_id=generate_doc_id(str(file_path)),
            filename=file_path.name,
            source=str(file_path.resolve()),
            document_type="txt",
            title=title,
            text=cleaned,
            metadata={"byte_size": file_path.stat().st_size}
        )
        return [doc]


class PDFLoader(BaseLoader):
    """Loader for Portable Document Format files (.pdf) using pypdf."""

    def load(self, file_path: Path) -> List[Document]:
        if not file_path.exists():
            raise DocumentLoadingError(f"File does not exist: {file_path}")

        try:
            reader = pypdf.PdfReader(str(file_path))
            if reader.is_encrypted:
                try:
                    # Attempt empty password decryption
                    reader.decrypt("")
                except Exception as e:
                    raise DocumentLoadingError(f"PDF is encrypted and password-protected: {file_path}") from e

            page_texts = []
            for page_idx, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        page_texts.append(page_text)
                except Exception as e:
                    # Continue extracting remaining pages if one fails
                    continue

            combined_raw = "\n\n".join(page_texts)
            cleaned = clean_text(combined_raw)

            # Extract title from metadata if available
            title = None
            if reader.metadata is not None:
                if hasattr(reader.metadata, "title") and reader.metadata.title:
                    title = clean_text(str(reader.metadata.title))
                elif isinstance(reader.metadata, dict):
                    raw_title = reader.metadata.get("/Title") or reader.metadata.get("title")
                    if raw_title:
                        title = clean_text(str(raw_title))

            if not title:
                first_line = cleaned.split("\n")[0].strip() if cleaned else ""
                title = first_line[:100] if first_line else file_path.stem

            doc = Document(
                document_id=generate_doc_id(str(file_path)),
                filename=file_path.name,
                source=str(file_path.resolve()),
                document_type="pdf",
                title=title,
                text=cleaned,
                metadata={
                    "page_count": len(reader.pages),
                    "extracted_pages": len(page_texts),
                    "byte_size": file_path.stat().st_size,
                }
            )
            return [doc]
        except DocumentLoadingError:
            raise
        except Exception as e:
            raise DocumentLoadingError(f"Failed to read PDF file '{file_path}': {str(e)}") from e


class CSVLoader(BaseLoader):
    """
    Loader for tabular CSV files (.csv).
    Automatically maps FAQ columns (question, answer, category) or general text columns.
    Emits one Document per valid record row to support fine-grained FAQ datasets.
    """

    def load(self, file_path: Path) -> List[Document]:
        if not file_path.exists():
            raise DocumentLoadingError(f"File does not exist: {file_path}")

        documents: List[Document] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    # Empty CSV
                    return []

                fieldnames_lower = {name.lower().strip(): name for name in reader.fieldnames if name}

                # Find candidate fields for question/title
                title_col = None
                for candidate in ["title", "question", "query", "topic", "q"]:
                    if candidate in fieldnames_lower:
                        title_col = fieldnames_lower[candidate]
                        break

                # Find candidate fields for answer/text
                text_col = None
                for candidate in ["answer", "text", "content", "body", "description", "a"]:
                    if candidate in fieldnames_lower:
                        text_col = fieldnames_lower[candidate]
                        break

                for row_idx, row in enumerate(reader):
                    row_metadata: Dict[str, Any] = {
                        "row_index": row_idx,
                        "byte_size": file_path.stat().st_size,
                    }

                    if text_col and row.get(text_col):
                        title = clean_text(row.get(title_col, "")) if title_col else f"{file_path.stem} Row {row_idx + 1}"
                        raw_body = row.get(text_col, "")
                        if title_col and title and title not in raw_body:
                            full_text = f"Question: {title}\nAnswer: {raw_body}"
                        else:
                            full_text = raw_body

                        for k, v in row.items():
                            if k not in (title_col, text_col) and v is not None:
                                row_metadata[k] = v
                    else:
                        # Fallback: serialize entire row key-values
                        full_text = "\n".join(f"{k}: {v}" for k, v in row.items() if v)
                        title = f"{file_path.stem} Row {row_idx + 1}"

                    cleaned = clean_text(full_text)
                    if cleaned:
                        doc = Document(
                            document_id=generate_doc_id(str(file_path), str(row_idx)),
                            filename=file_path.name,
                            source=str(file_path.resolve()),
                            document_type="csv",
                            title=title or f"{file_path.stem} Row {row_idx + 1}",
                            text=cleaned,
                            metadata=row_metadata,
                        )
                        documents.append(doc)

            return documents
        except Exception as e:
            raise DocumentLoadingError(f"Malformed or unreadable CSV file '{file_path}': {str(e)}") from e


class JSONLoader(BaseLoader):
    """
    Loader for structured JSON files (.json).
    Supports a list of document objects or a single document object.
    """

    def load(self, file_path: Path) -> List[Document]:
        if not file_path.exists():
            raise DocumentLoadingError(f"File does not exist: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DocumentLoadingError(f"Malformed JSON syntax in '{file_path}': {str(e)}") from e
        except Exception as e:
            raise DocumentLoadingError(f"Failed to read JSON file '{file_path}': {str(e)}") from e

        items = data if isinstance(data, list) else [data]
        documents: List[Document] = []

        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                # Plain string or primitive in list
                cleaned = clean_text(str(item))
                if cleaned:
                    doc = Document(
                        document_id=generate_doc_id(str(file_path), str(idx)),
                        filename=file_path.name,
                        source=str(file_path.resolve()),
                        document_type="json",
                        title=f"{file_path.stem} Item {idx + 1}",
                        text=cleaned,
                        metadata={"index": idx}
                    )
                    documents.append(doc)
                continue

            # Identify title & text fields
            item_lower = {k.lower(): k for k in item.keys()}

            title_key = None
            for candidate in ["title", "question", "topic", "name", "header"]:
                if candidate in item_lower:
                    title_key = item_lower[candidate]
                    break

            text_key = None
            for candidate in ["text", "content", "body", "answer", "description"]:
                if candidate in item_lower:
                    text_key = item_lower[candidate]
                    break

            title = str(item[title_key]).strip() if title_key and item.get(title_key) else None
            if text_key and item.get(text_key):
                body = str(item[text_key])
                if title and title not in body:
                    raw_text = f"{title}\n\n{body}"
                else:
                    raw_text = body
            else:
                raw_text = json.dumps(item, indent=2, ensure_ascii=False)

            cleaned = clean_text(raw_text)
            if cleaned:
                meta = {k: v for k, v in item.items() if k not in (title_key, text_key)}
                meta["index"] = idx
                doc = Document(
                    document_id=generate_doc_id(str(file_path), str(idx)),
                    filename=file_path.name,
                    source=str(file_path.resolve()),
                    document_type="json",
                    title=title or f"{file_path.stem} #{idx + 1}",
                    text=cleaned,
                    metadata=meta,
                )
                documents.append(doc)

        return documents


class LoaderRegistry:
    """Registry to resolve appropriate loader based on file extension."""

    def __init__(self):
        self._loaders: Dict[str, BaseLoader] = {
            ".txt": TXTLoader(),
            ".pdf": PDFLoader(),
            ".csv": CSVLoader(),
            ".json": JSONLoader(),
        }

    def register(self, extension: str, loader: BaseLoader) -> None:
        """Register a custom loader for a specific extension."""
        self._loaders[extension.lower()] = loader

    def get_loader(self, file_path: Path) -> BaseLoader:
        """Retrieve the loader mapped to the file's suffix."""
        ext = file_path.suffix.lower()
        if ext not in self._loaders:
            supported = ", ".join(self._loaders.keys())
            raise UnsupportedFileTypeError(
                f"Unsupported file type '{ext}' for file '{file_path.name}'. Supported formats: {supported}"
            )
        return self._loaders[ext]

    def load_file(self, file_path: Path) -> List[Document]:
        """Convenience method to resolve loader and load documents."""
        loader = self.get_loader(file_path)
        return loader.load(file_path)
