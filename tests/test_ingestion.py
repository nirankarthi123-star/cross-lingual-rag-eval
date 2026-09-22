from pathlib import Path
from backend.retrieval.chunker import TextChunker
from backend.retrieval.loaders import LoaderRegistry
from backend.retrieval.storage import ProcessedStorage
from backend.retrieval.validator import validate_dataset


def test_end_to_end_ingestion(tmp_path: Path):
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    proc_dir = tmp_path / "processed"

    # Create dummy files of different types
    (doc_dir / "note.txt").write_text("General policy on working hours and break times.", encoding="utf-8")
    (doc_dir / "faq.csv").write_text("question,answer\nWhat is OTP?,One time password", encoding="utf-8")

    registry = LoaderRegistry()
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    storage = ProcessedStorage(proc_dir)

    all_docs = []
    for f in doc_dir.iterdir():
        all_docs.extend(registry.load_file(f))

    assert len(all_docs) == 2

    chunks = chunker.chunk_documents(all_docs)
    assert len(chunks) >= 2

    storage.save_documents(all_docs)
    storage.save_chunks(chunks)

    # Validate output
    stats = validate_dataset(processed_dir=proc_dir)
    assert stats.num_documents == 2
    assert stats.num_chunks == len(chunks)
    assert stats.empty_documents == 0
    assert stats.empty_chunks == 0
    assert stats.avg_chunk_length > 0
    assert stats.min_chunk_length > 0
