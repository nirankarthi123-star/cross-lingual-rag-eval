import os
import sqlite3
import pytest
from pathlib import Path
from backend.dataset.schemas import QueryRecord
from backend.experiments.matrix import generate_matrix, get_language_variant, LANGUAGES, MITIGATION_CONDITIONS
from backend.experiments.runner import ExperimentRunner
from backend.experiments.models import ExperimentConfig, ExperimentResult
from backend.database.sqlite_client import SQLiteClient

@pytest.fixture
def sample_query_records():
    return [
        QueryRecord(
            question_id="Q01",
            domain="Telecom",
            english="English 1",
            tamil_english="Tamil 1",
            hindi_english="Hindi 1",
            script_type="Romanized"
        ),
        QueryRecord(
            question_id="Q02",
            domain="Telecom",
            english="English 2",
            tamil_english="Tamil 2",
            hindi_english="Hindi 2",
            script_type="Romanized"
        )
    ]

def test_get_language_variant(sample_query_records):
    record = sample_query_records[0]
    assert get_language_variant(record, "english") == "English 1"
    assert get_language_variant(record, "tamil_english") == "Tamil 1"
    assert get_language_variant(record, "hindi_english") == "Hindi 1"
    
    with pytest.raises(ValueError):
        get_language_variant(record, "unknown_lang")

def test_generate_matrix_all_conditions(sample_query_records):
    dataset_path = "dummy.json"
    matrix = generate_matrix(sample_query_records, dataset_path)
    
    # 3 languages * 2 mitigations * 2 queries = 12 runs
    assert len(matrix) == 12
    
    # Check that we have exactly 6 unique condition combinations
    configs = {row[0].experiment_id for row in matrix}
    assert len(configs) == 6

def test_generate_matrix_filtered(sample_query_records):
    dataset_path = "dummy.json"
    matrix = generate_matrix(
        sample_query_records, 
        dataset_path, 
        languages=["english"], 
        mitigation_filter="on"
    )
    
    # 1 language * 1 mitigation * 2 queries = 2 runs
    assert len(matrix) == 2
    assert all(row[0].language == "english" for row in matrix)
    assert all(row[0].mitigation_enabled is True for row in matrix)

@pytest.fixture
def test_db(tmp_path):
    db_path = tmp_path / "test_eval.db"
    return SQLiteClient(db_path=str(db_path))

def test_sqlite_client_experiment_results(test_db):
    config = ExperimentConfig(
        experiment_id="test_baseline",
        language="english",
        condition_name="baseline",
        mitigation_enabled=False,
        dataset_path="dummy.json",
        embedding_model="model",
        generator_model="model",
        judge_model="model",
        top_k=5,
        judge_prompt_version="v1",
        hallucination_threshold=0.8,
        created_at="now"
    )
    test_db.save_experiment_config(config)
    
    result = ExperimentResult(
        run_id="run123",
        experiment_id="test_baseline",
        question_id="Q01",
        language="english",
        mitigation_enabled=False,
        original_query="English 1",
        normalized_query=None,
        mitigation_applied=False,
        retrieved_document_ids=["doc1"],
        retrieved_context="context",
        generated_answer="answer",
        faithfulness_score=0.9,
        hallucination_flag=False,
        faithfulness_explanation="ok",
        embedding_model="e",
        generator_model="g",
        judge_model="j",
        started_at="now",
        completed_at="now"
    )
    
    row_id = test_db.save_experiment_result(result)
    assert row_id is not None
    
    completed_keys = test_db.get_completed_run_keys()
    assert ("test_baseline", "Q01", "english", False) in completed_keys

    results = test_db.get_all_experiment_results()
    assert len(results) == 1
    assert results[0]["question_id"] == "Q01"
    assert results[0]["retrieved_document_ids"] == ["doc1"] # parsed back to list
