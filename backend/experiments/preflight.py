"""
backend/experiments/preflight.py

Corpus and dataset safety preflight validator for research-grade RAG evaluation.
Enforces strict immutability, provenance, ground-truth alignment, and safety checks.
"""
import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


def compute_file_sha256(filepath: Path) -> str:
    """Computes SHA-256 hash of a file efficiently in 64KB chunks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_corpus_manifest(
    documents_dir: str = "data/documents",
    processed_dir: str = "data/processed",
    vector_store_dir: str = "data/vector_store",
    manifest_path: str = "data/processed/corpus_manifest.json",
) -> Dict[str, Any]:
    """
    Generates a deterministic SHA-256 manifest of the active corpus,
    processed artifacts, and vector index.
    """
    docs_path = Path(documents_dir)
    proc_path = Path(processed_dir)
    vs_path = Path(vector_store_dir)

    source_files = []
    if docs_path.exists():
        for f in sorted(docs_path.iterdir()):
            if f.is_file() and not f.name.startswith("."):
                source_files.append({
                    "filename": f.name,
                    "sha256": compute_file_sha256(f),
                    "size_bytes": f.stat().st_size,
                })

    chunks_file = proc_path / "chunks.jsonl"
    docs_file = proc_path / "documents.jsonl"
    index_file = vs_path / "index.faiss"
    meta_file = vs_path / "metadata_map.json"

    chunks_sha256 = compute_file_sha256(chunks_file) if chunks_file.exists() else None
    docs_sha256 = compute_file_sha256(docs_file) if docs_file.exists() else None
    index_sha256 = compute_file_sha256(index_file) if index_file.exists() else None
    meta_sha256 = compute_file_sha256(meta_file) if meta_file.exists() else None

    # Count chunks and logical documents
    num_chunks = 0
    if chunks_file.exists():
        with open(chunks_file, "r", encoding="utf-8") as f:
            num_chunks = sum(1 for line in f if line.strip())

    num_docs = 0
    if docs_file.exists():
        with open(docs_file, "r", encoding="utf-8") as f:
            num_docs = sum(1 for line in f if line.strip())

    # Overall corpus hash based on sorted source hashes + chunks hash
    h_combined = hashlib.sha256()
    for s in source_files:
        h_combined.update(f"{s['filename']}:{s['sha256']}".encode("utf-8"))
    if chunks_sha256:
        h_combined.update(chunks_sha256.encode("utf-8"))
    corpus_hash = h_combined.hexdigest()

    manifest = {
        "manifest_version": "1.0",
        "corpus_id": "corpus-v1-banking-telecom",
        "corpus_hash": corpus_hash,
        "num_source_documents": len(source_files),
        "source_documents": source_files,
        "num_logical_documents": num_docs,
        "documents_file_sha256": docs_sha256,
        "num_chunks": num_chunks,
        "chunks_file_sha256": chunks_sha256,
        "vector_store": {
            "embedding_model": "intfloat/multilingual-e5-base",
            "embedding_dimension": 768,
            "index_file_sha256": index_sha256,
            "metadata_file_sha256": meta_sha256,
        }
    }

    out_p = Path(manifest_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info(f"Generated corpus manifest at {manifest_path} (corpus_hash={corpus_hash[:16]}...)")
    return manifest


@dataclass
class PreflightValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    corpus_hash: Optional[str] = None
    dataset_hash: Optional[str] = None
    total_queries: int = 0
    total_chunks: int = 0

    def print_report(self):
        print(f"\n{'='*70}")
        print("Preflight Safety and Research-Readiness Validation")
        print(f"{'='*70}")
        if self.is_valid:
            print("[PASS] All preflight safety checks passed.")
            print(f"  Corpus SHA-256 Hash  : {self.corpus_hash}")
            print(f"  Dataset SHA-256 Hash : {self.dataset_hash}")
            print(f"  Valid Queries        : {self.total_queries} (Base information needs)")
            print(f"  Corpus Chunks        : {self.total_chunks}")
        else:
            print("[FAIL] Preflight validation failed! Errors must be resolved:")
            for err in self.errors:
                print(f"  - ERROR: {err}")
        if self.warnings:
            print("Warnings:")
            for w in self.warnings:
                print(f"  - WARNING: {w}")
        print(f"{'='*70}\n")


class PreflightValidationError(RuntimeError):
    """Raised when preflight safety validation fails before starting an experiment."""
    pass


class PreflightValidator:
    """
    Enforces research integrity rules before any experiment execution.
    Refuses execution if corpus, dataset, or ground-truth constraints are violated.
    """

    def __init__(
        self,
        manifest_path: str = "data/processed/corpus_manifest.json",
        processed_dir: str = "data/processed",
        vector_store_dir: str = "data/vector_store",
    ):
        self.manifest_path = Path(manifest_path)
        self.processed_dir = Path(processed_dir)
        self.vector_store_dir = Path(vector_store_dir)

    def validate(
        self,
        dataset_path: str,
        require_retrieval_metrics: bool = True,
    ) -> PreflightValidationResult:
        errors = []
        warnings = []
        d_path = Path(dataset_path)

        # ------------------------------------------------------------------ #
        # Check 1: Dataset file existence and hash                            #
        # ------------------------------------------------------------------ #
        if not d_path.exists():
            errors.append(f"Query dataset file does not exist at '{dataset_path}'.")
            return PreflightValidationResult(is_valid=False, errors=errors)

        try:
            dataset_hash = compute_file_sha256(d_path)
        except Exception as e:
            errors.append(f"Failed to compute SHA-256 hash for dataset '{dataset_path}': {e}")
            return PreflightValidationResult(is_valid=False, errors=errors)

        # ------------------------------------------------------------------ #
        # Check 2: Corpus manifest existence & matching active files          #
        # ------------------------------------------------------------------ #
        if not self.manifest_path.exists():
            errors.append(
                f"Corpus manifest is missing at '{self.manifest_path}'. "
                "Production experiments require a recorded corpus manifest. "
                "Generate one via preflight tools or rerun ingestion."
            )
            return PreflightValidationResult(is_valid=False, errors=errors, dataset_hash=dataset_hash)

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception as e:
            errors.append(f"Corpus manifest at '{self.manifest_path}' is corrupted or unreadable: {e}")
            return PreflightValidationResult(is_valid=False, errors=errors, dataset_hash=dataset_hash)

        corpus_hash = manifest.get("corpus_hash")
        if not corpus_hash:
            errors.append(f"Corpus manifest at '{self.manifest_path}' is missing 'corpus_hash'.")

        # Verify active files match manifest hashes
        chunks_file = self.processed_dir / "chunks.jsonl"
        index_file = self.vector_store_dir / "index.faiss"
        meta_file = self.vector_store_dir / "metadata_map.json"

        if not chunks_file.exists():
            errors.append(f"Processed chunks file missing at '{chunks_file}'.")
        else:
            current_chunks_sha = compute_file_sha256(chunks_file)
            expected_chunks_sha = manifest.get("chunks_file_sha256")
            if expected_chunks_sha and current_chunks_sha != expected_chunks_sha:
                errors.append(
                    f"Active chunks.jsonl SHA-256 mismatch!\n"
                    f"  Expected from manifest: {expected_chunks_sha}\n"
                    f"  Current on disk:        {current_chunks_sha}\n"
                    f"  Action: Re-index or regenerate corpus manifest."
                )

        if not index_file.exists():
            errors.append(f"Vector store index file missing at '{index_file}'.")
        else:
            current_idx_sha = compute_file_sha256(index_file)
            expected_idx_sha = manifest.get("vector_store", {}).get("index_file_sha256")
            if expected_idx_sha and current_idx_sha != expected_idx_sha:
                errors.append(
                    f"Active index.faiss SHA-256 mismatch!\n"
                    f"  Expected from manifest: {expected_idx_sha}\n"
                    f"  Current on disk:        {current_idx_sha}\n"
                    f"  Action: Rebuild index via scripts/build_index.py."
                )

        if not meta_file.exists():
            errors.append(f"Vector store metadata map missing at '{meta_file}'.")
        else:
            current_meta_sha = compute_file_sha256(meta_file)
            expected_meta_sha = manifest.get("vector_store", {}).get("metadata_file_sha256")
            if expected_meta_sha and current_meta_sha != expected_meta_sha:
                errors.append(
                    f"Active metadata_map.json SHA-256 mismatch!\n"
                    f"  Expected from manifest: {expected_meta_sha}\n"
                    f"  Current on disk:        {current_meta_sha}\n"
                    f"  Action: Rebuild index via scripts/build_index.py."
                )

        # Load metadata map to validate expected_document_ids
        indexed_ids: Set[str] = set()
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta_dict = json.load(f)
                    for val in meta_dict.values():
                        if isinstance(val, dict):
                            if val.get("document_id"):
                                indexed_ids.add(val["document_id"])
                            if val.get("chunk_id"):
                                indexed_ids.add(val["chunk_id"])
            except Exception as e:
                errors.append(f"Failed to parse vector store metadata map: {e}")

        # ------------------------------------------------------------------ #
        # Check 3: Query dataset parsing and integrity                        #
        # ------------------------------------------------------------------ #
        try:
            with open(d_path, "r", encoding="utf-8") as f:
                queries = json.load(f)
        except Exception as e:
            errors.append(f"Failed to parse query dataset JSON: {e}")
            return PreflightValidationResult(
                is_valid=False, errors=errors, corpus_hash=corpus_hash, dataset_hash=dataset_hash
            )

        if not isinstance(queries, list) or len(queries) == 0:
            errors.append(f"Dataset must contain a non-empty list of query records. Got {type(queries)}.")
            return PreflightValidationResult(
                is_valid=False, errors=errors, corpus_hash=corpus_hash, dataset_hash=dataset_hash
            )

        seen_ids = set()
        for i, q in enumerate(queries, start=1):
            qid = q.get("question_id")
            if not qid or not str(qid).strip():
                errors.append(f"Row {i}: Missing or empty 'question_id'.")
                continue

            # Duplicate question ID check
            if qid in seen_ids:
                errors.append(f"Duplicate question_id '{qid}' detected at row {i}.")
            seen_ids.add(qid)

            # Check 4: Three language variants required
            for lang in ["english", "tamil_english", "hindi_english"]:
                val = q.get(lang)
                if not val or not str(val).strip():
                    errors.append(f"Question '{qid}' is missing required language variant '{lang}'.")

            # Check 5: Mock/Test row mixing check
            qid_upper = str(qid).upper()
            if "SMOKE" in qid_upper or "MOCK" in qid_upper or "TEST" in qid_upper:
                errors.append(
                    f"Question '{qid}' is flagged as a mock/test item. "
                    "Production datasets must never mix mock/smoke tests with research queries."
                )

            # Check 6: Ground truth document IDs validation
            if require_retrieval_metrics:
                expected_docs = q.get("expected_document_ids")
                if not expected_docs or not isinstance(expected_docs, list) or len(expected_docs) == 0:
                    errors.append(
                        f"Question '{qid}' is missing 'expected_document_ids'. "
                        "Retrieval evaluation (Recall@K) requires non-empty expected document IDs."
                    )
                else:
                    for doc_id in expected_docs:
                        if doc_id not in indexed_ids:
                            errors.append(
                                f"Question '{qid}' specifies expected_document_id '{doc_id}' "
                                f"which is not present in the active vector index metadata."
                            )

        num_chunks = manifest.get("num_chunks", len(indexed_ids))
        is_valid = len(errors) == 0
        return PreflightValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            corpus_hash=corpus_hash,
            dataset_hash=dataset_hash,
            total_queries=len(queries),
            total_chunks=num_chunks,
        )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run preflight validation on corpus and dataset.")
    parser.add_argument("--dataset", default="data/queries/sample_queries.json", help="Path to query dataset.")
    parser.add_argument("--generate-manifest", action="store_true", help="Generate corpus_manifest.json if missing.")
    args = parser.parse_args()

    if args.generate_manifest or not Path("data/processed/corpus_manifest.json").exists():
        print("[INFO] Generating corpus manifest from active corpus...")
        generate_corpus_manifest()

    validator = PreflightValidator()
    res = validator.validate(args.dataset)
    res.print_report()
    if not res.is_valid:
        exit(1)
