#!/usr/bin/env python3
"""
Command-line entry point to ingest, clean, chunk, and store documents from data/documents/.
Usage:
    python scripts/ingest_documents.py [--input-dir data/documents] [--output-dir data/processed]
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is in python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.config.logging import setup_logging
from backend.config.settings import get_settings
from backend.retrieval.chunker import TextChunker
from backend.retrieval.loaders import DocumentLoadingError, LoaderRegistry, UnsupportedFileTypeError
from backend.retrieval.storage import ProcessedStorage
from backend.retrieval.validator import validate_dataset


def ingest(
    input_dir: Path,
    output_dir: Path,
    chunk_size: int,
    chunk_overlap: int,
    run_validation: bool = True,
):
    logger = setup_logging()
    logger.info("Initializing document ingestion pipeline...")
    logger.info("Source directory      : %s", input_dir.resolve())
    logger.info("Destination directory : %s", output_dir.resolve())
    logger.info("Chunk configuration   : size=%d, overlap=%d", chunk_size, chunk_overlap)

    if not input_dir.exists():
        logger.error("Input directory does not exist: %s", input_dir)
        sys.exit(1)

    registry = LoaderRegistry()
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    storage = ProcessedStorage(output_dir)

    all_documents = []
    failed_files = []

    input_files = sorted(list(input_dir.iterdir()))
    target_files = [f for f in input_files if f.is_file() and not f.name.startswith(".")]

    if not target_files:
        logger.warning("No files found in %s to ingest.", input_dir)

    for file_path in target_files:
        try:
            logger.info("Ingesting: %s", file_path.name)
            docs = registry.load_file(file_path)
            all_documents.extend(docs)
            logger.info("  -> Loaded %d document(s)", len(docs))
        except UnsupportedFileTypeError as e:
            logger.warning("  [SKIPPED] Unsupported file type: %s", e)
            failed_files.append((file_path.name, str(e)))
        except DocumentLoadingError as e:
            logger.error("  [ERROR] Failed to load %s: %s", file_path.name, e)
            failed_files.append((file_path.name, str(e)))
        except Exception as e:
            logger.error("  [UNEXPECTED ERROR] Could not process %s: %s", file_path.name, e)
            failed_files.append((file_path.name, str(e)))

    logger.info("Total documents parsed across all files: %d", len(all_documents))

    # Chunking
    all_chunks = chunker.chunk_documents(all_documents)
    logger.info("Generated %d chunks from %d documents", len(all_chunks), len(all_documents))

    # Persistence
    doc_path = storage.save_documents(all_documents)
    chk_path = storage.save_chunks(all_chunks)
    logger.info("Saved documents to: %s", doc_path)
    logger.info("Saved chunks to   : %s", chk_path)

    if failed_files:
        print("\nNotice: The following files encountered errors and were skipped:")
        for fname, reason in failed_files:
            print(f"  - {fname}: {reason}")

    if run_validation:
        stats = validate_dataset(documents=all_documents, chunks=all_chunks)
        stats.print_summary()

    return all_documents, all_chunks


def main():
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Ingest, clean, and chunk documents for RAG evaluation.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(settings.DOCUMENTS_DIR),
        help="Path to raw documents directory (default: data/documents)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(settings.PROCESSED_DIR),
        help="Path to store processed jsonl outputs (default: data/processed)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=settings.DEFAULT_CHUNK_SIZE,
        help=f"Chunk character size (default: {settings.DEFAULT_CHUNK_SIZE})",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=settings.DEFAULT_CHUNK_OVERLAP,
        help=f"Chunk character overlap (default: {settings.DEFAULT_CHUNK_OVERLAP})",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Disable automatic post-ingestion validation printout",
    )

    args = parser.parse_args()
    ingest(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        run_validation=not args.no_validate,
    )


if __name__ == "__main__":
    main()
