import pytest
from backend.retrieval.chunker import TextChunker
from backend.retrieval.models import Document


def test_chunker_parameter_validation():
    # overlap >= chunk_size must fail
    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, chunk_overlap=100)

    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, chunk_overlap=120)

    with pytest.raises(ValueError):
        TextChunker(chunk_size=-50, chunk_overlap=10)

    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, chunk_overlap=-10)


def test_chunker_sliding_window_and_metadata():
    doc = Document(
        document_id="doc_123",
        filename="test_doc.txt",
        source="/path/to/test_doc.txt",
        document_type="txt",
        title="Test Academic Policy",
        text=(
            "First paragraph explaining undergraduate admission requirements and standards in detail.\n\n"
            "Second paragraph covering scholarship renewals, CGPA minimum criteria, and deadlines.\n\n"
            "Third paragraph outlining examination rules, integrity codes, and disciplinary actions."
        ),
        metadata={"department": "Admissions", "author": "Registrar"},
    )

    chunker = TextChunker(chunk_size=120, chunk_overlap=30)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) >= 2
    for i, chunk in enumerate(chunks):
        assert chunk.document_id == "doc_123"
        assert chunk.chunk_id == f"doc_123_c{i}"
        assert chunk.chunk_index == i
        assert len(chunk.chunk_text) > 0
        assert chunk.metadata["title"] == "Test Academic Policy"
        assert chunk.metadata["department"] == "Admissions"
        assert chunk.metadata["filename"] == "test_doc.txt"


def test_chunker_empty_document():
    doc = Document(
        document_id="empty_doc",
        filename="empty.txt",
        source="empty.txt",
        document_type="txt",
        title="Empty",
        text="",
    )
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    chunks = chunker.chunk_document(doc)
    assert chunks == []
