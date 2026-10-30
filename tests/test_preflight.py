"""
Tests for backend/experiments/preflight.py
Verifies that preflight validation catches corrupt data, missing manifests,
duplicate queries, missing language variants, mock rows, and invalid document IDs.
"""
import json
import pytest
from pathlib import Path

from backend.experiments.preflight import (
    PreflightValidator,
    PreflightValidationResult,
    generate_corpus_manifest,
    compute_file_sha256,
)


@pytest.fixture
def temp_study_env(tmp_path):
    """Sets up a temporary valid environment for preflight testing."""
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    sample_doc = docs_dir / "sample.txt"
    sample_doc.write_text("This is a sample document for testing.", encoding="utf-8")

    proc_dir = tmp_path / "processed"
    proc_dir.mkdir()
    chunks_file = proc_dir / "chunks.jsonl"
    chunks_file.write_text(
        json.dumps({"chunk_id": "doc1_c0", "document_id": "doc1", "chunk_text": "Sample chunk text."}) + "\n",
        encoding="utf-8"
    )
    docs_file = proc_dir / "documents.jsonl"
    docs_file.write_text(
        json.dumps({"id": "doc1", "title": "Sample Doc", "source_file": "sample.txt"}) + "\n",
        encoding="utf-8"
    )

    vs_dir = tmp_path / "vector_store"
    vs_dir.mkdir()
    index_file = vs_dir / "index.faiss"
    index_file.write_bytes(b"dummy faiss index binary content")
    meta_file = vs_dir / "metadata_map.json"
    meta_file.write_text(
        json.dumps({"0": {"chunk_id": "doc1_c0", "document_id": "doc1", "chunk_text": "Sample chunk text."}}),
        encoding="utf-8"
    )

    manifest_file = proc_dir / "corpus_manifest.json"
    generate_corpus_manifest(
        documents_dir=str(docs_dir),
        processed_dir=str(proc_dir),
        vector_store_dir=str(vs_dir),
        manifest_path=str(manifest_file),
    )

    # Valid dataset
    queries_dir = tmp_path / "queries"
    queries_dir.mkdir()
    valid_dataset = queries_dir / "valid_queries.json"
    valid_dataset.write_text(
        json.dumps([
            {
                "question_id": "PROD-Q01",
                "english": "What is the policy?",
                "tamil_english": "Policy enna?",
                "hindi_english": "Policy kya hai?",
                "expected_document_ids": ["doc1"],
            }
        ]),
        encoding="utf-8"
    )

    return {
        "manifest_path": str(manifest_file),
        "processed_dir": str(proc_dir),
        "vector_store_dir": str(vs_dir),
        "valid_dataset": str(valid_dataset),
        "queries_dir": queries_dir,
        "proc_dir": proc_dir,
    }


def test_preflight_passes_on_valid_setup(temp_study_env):
    validator = PreflightValidator(
        manifest_path=temp_study_env["manifest_path"],
        processed_dir=temp_study_env["processed_dir"],
        vector_store_dir=temp_study_env["vector_store_dir"],
    )
    result = validator.validate(temp_study_env["valid_dataset"])
    assert result.is_valid is True
    assert len(result.errors) == 0
    assert result.total_queries == 1
    assert result.corpus_hash is not None


def test_preflight_fails_on_missing_manifest(temp_study_env):
    validator = PreflightValidator(
        manifest_path="non_existent_manifest.json",
        processed_dir=temp_study_env["processed_dir"],
        vector_store_dir=temp_study_env["vector_store_dir"],
    )
    result = validator.validate(temp_study_env["valid_dataset"])
    assert result.is_valid is False
    assert any("manifest is missing" in err.lower() for err in result.errors)


def test_preflight_fails_on_duplicate_question_id(temp_study_env):
    dup_dataset = temp_study_env["queries_dir"] / "dup_queries.json"
    dup_dataset.write_text(
        json.dumps([
            {
                "question_id": "PROD-Q01",
                "english": "Query one?",
                "tamil_english": "Query one enna?",
                "hindi_english": "Query one kya?",
                "expected_document_ids": ["doc1"],
            },
            {
                "question_id": "PROD-Q01",
                "english": "Query two?",
                "tamil_english": "Query two enna?",
                "hindi_english": "Query two kya?",
                "expected_document_ids": ["doc1"],
            }
        ]),
        encoding="utf-8"
    )
    validator = PreflightValidator(
        manifest_path=temp_study_env["manifest_path"],
        processed_dir=temp_study_env["processed_dir"],
        vector_store_dir=temp_study_env["vector_store_dir"],
    )
    result = validator.validate(str(dup_dataset))
    assert result.is_valid is False
    assert any("duplicate question_id" in err.lower() for err in result.errors)


def test_preflight_fails_on_missing_language_variant(temp_study_env):
    missing_lang_dataset = temp_study_env["queries_dir"] / "missing_lang.json"
    missing_lang_dataset.write_text(
        json.dumps([
            {
                "question_id": "PROD-Q01",
                "english": "Query one?",
                "tamil_english": "",  # Missing!
                "hindi_english": "Query one kya?",
                "expected_document_ids": ["doc1"],
            }
        ]),
        encoding="utf-8"
    )
    validator = PreflightValidator(
        manifest_path=temp_study_env["manifest_path"],
        processed_dir=temp_study_env["processed_dir"],
        vector_store_dir=temp_study_env["vector_store_dir"],
    )
    result = validator.validate(str(missing_lang_dataset))
    assert result.is_valid is False
    assert any("missing required language variant 'tamil_english'" in err.lower() for err in result.errors)


def test_preflight_fails_on_mock_row(temp_study_env):
    mock_dataset = temp_study_env["queries_dir"] / "mock_dataset.json"
    mock_dataset.write_text(
        json.dumps([
            {
                "question_id": "SMOKE-Q01",
                "english": "Smoke test query?",
                "tamil_english": "Smoke test?",
                "hindi_english": "Smoke test kya?",
                "expected_document_ids": ["doc1"],
            }
        ]),
        encoding="utf-8"
    )
    validator = PreflightValidator(
        manifest_path=temp_study_env["manifest_path"],
        processed_dir=temp_study_env["processed_dir"],
        vector_store_dir=temp_study_env["vector_store_dir"],
    )
    result = validator.validate(str(mock_dataset))
    assert result.is_valid is False
    assert any("mock/test item" in err.lower() for err in result.errors)


def test_preflight_fails_on_unknown_expected_doc_id(temp_study_env):
    bad_doc_dataset = temp_study_env["queries_dir"] / "bad_doc.json"
    bad_doc_dataset.write_text(
        json.dumps([
            {
                "question_id": "PROD-Q01",
                "english": "Valid query?",
                "tamil_english": "Valid query enna?",
                "hindi_english": "Valid query kya?",
                "expected_document_ids": ["non_existent_doc_999"],
            }
        ]),
        encoding="utf-8"
    )
    validator = PreflightValidator(
        manifest_path=temp_study_env["manifest_path"],
        processed_dir=temp_study_env["processed_dir"],
        vector_store_dir=temp_study_env["vector_store_dir"],
    )
    result = validator.validate(str(bad_doc_dataset))
    assert result.is_valid is False
    assert any("not present in the active vector index" in err.lower() for err in result.errors)
