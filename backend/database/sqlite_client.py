import csv
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class SQLiteClient:
    def __init__(self, db_path: str = "data/rag_eval.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes all database tables if they don't exist."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Phase 8: ad-hoc faithfulness evaluations
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS evaluations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        query TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        context TEXT NOT NULL,
                        faithfulness_score REAL NOT NULL,
                        hallucination_flag BOOLEAN NOT NULL,
                        explanation TEXT,
                        judge_model TEXT,
                        prompt_version TEXT
                    )
                ''')

                # Phase 9: structured experiment results
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS experiment_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        run_id TEXT NOT NULL UNIQUE,
                        experiment_id TEXT NOT NULL,
                        question_id TEXT NOT NULL,
                        language TEXT NOT NULL,
                        mitigation_enabled BOOLEAN NOT NULL,
                        original_query TEXT NOT NULL,
                        normalized_query TEXT,
                        mitigation_applied BOOLEAN NOT NULL DEFAULT 0,
                        retrieved_document_ids TEXT,
                        retrieved_context TEXT,
                        generated_answer TEXT,
                        faithfulness_score REAL,
                        hallucination_flag BOOLEAN,
                        faithfulness_explanation TEXT,
                        embedding_model TEXT,
                        generator_model TEXT,
                        judge_model TEXT,
                        started_at TEXT,
                        completed_at TEXT,
                        error TEXT
                    )
                ''')

                # Phase 9: experiment configs (for reproducibility)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS experiment_configs (
                        experiment_id TEXT PRIMARY KEY,
                        language TEXT NOT NULL,
                        condition_name TEXT NOT NULL,
                        mitigation_enabled BOOLEAN NOT NULL,
                        dataset_path TEXT,
                        embedding_model TEXT,
                        generator_model TEXT,
                        judge_model TEXT,
                        top_k INTEGER,
                        judge_prompt_version TEXT,
                        hallucination_threshold REAL,
                        created_at TEXT
                    )
                ''')

                conn.commit()
                logger.info(f"SQLite database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite DB: {e}")
            raise RuntimeError(f"Database initialization failed: {e}")

    # ------------------------------------------------------------------ #
    # Phase 8 API                                                          #
    # ------------------------------------------------------------------ #

    def save_evaluation(self,
                        query: str,
                        answer: str,
                        context: str,
                        score: float,
                        flag: bool,
                        explanation: str,
                        model: str,
                        version: str) -> Optional[int]:
        """Saves a single ad-hoc evaluation record (Phase 8)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO evaluations
                    (query, answer, context, faithfulness_score, hallucination_flag,
                     explanation, judge_model, prompt_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (query, answer, context, score, flag, explanation, model, version))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to save evaluation: {e}")
            return None

    # ------------------------------------------------------------------ #
    # Phase 9 API                                                          #
    # ------------------------------------------------------------------ #

    def save_experiment_config(self, config) -> None:
        """Save (or ignore if exists) an ExperimentConfig record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO experiment_configs
                    (experiment_id, language, condition_name, mitigation_enabled,
                     dataset_path, embedding_model, generator_model, judge_model,
                     top_k, judge_prompt_version, hallucination_threshold, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    config.experiment_id,
                    config.language,
                    config.condition_name,
                    config.mitigation_enabled,
                    config.dataset_path,
                    config.embedding_model,
                    config.generator_model,
                    config.judge_model,
                    config.top_k,
                    config.judge_prompt_version,
                    config.hallucination_threshold,
                    config.created_at,
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save experiment config: {e}")

    def save_experiment_result(self, result) -> Optional[int]:
        """Save a single ExperimentResult row. Returns the inserted row ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO experiment_results
                    (run_id, experiment_id, question_id, language, mitigation_enabled,
                     original_query, normalized_query, mitigation_applied,
                     retrieved_document_ids, retrieved_context, generated_answer,
                     faithfulness_score, hallucination_flag, faithfulness_explanation,
                     embedding_model, generator_model, judge_model,
                     started_at, completed_at, error)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', (
                    result.run_id,
                    result.experiment_id,
                    result.question_id,
                    result.language,
                    result.mitigation_enabled,
                    result.original_query,
                    result.normalized_query,
                    result.mitigation_applied,
                    json.dumps(result.retrieved_document_ids),
                    result.retrieved_context,
                    result.generated_answer,
                    result.faithfulness_score,
                    result.hallucination_flag,
                    result.faithfulness_explanation,
                    result.embedding_model,
                    result.generator_model,
                    result.judge_model,
                    result.started_at,
                    result.completed_at,
                    result.error,
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to save experiment result: {e}")
            return None

    def get_completed_run_keys(self) -> Set[Tuple[str, str, str, bool]]:
        """
        Return the set of (experiment_id, question_id, language, mitigation_enabled)
        for runs that are already stored and completed without error.
        Used for resume logic.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT experiment_id, question_id, language, mitigation_enabled
                    FROM experiment_results
                    WHERE error IS NULL AND completed_at IS NOT NULL
                ''')
                rows = cursor.fetchall()
                return {(r[0], r[1], r[2], bool(r[3])) for r in rows}
        except Exception as e:
            logger.error(f"Failed to fetch completed run keys: {e}")
            return set()

    def get_all_experiment_results(self, experiment_id: str = None) -> List[Dict[str, Any]]:
        """Fetch all (or filtered) experiment results as dicts."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if experiment_id:
                    cursor.execute(
                        "SELECT * FROM experiment_results WHERE experiment_id = ?",
                        (experiment_id,)
                    )
                else:
                    cursor.execute("SELECT * FROM experiment_results ORDER BY experiment_id, question_id")
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    d = dict(row)
                    # Deserialize the JSON list
                    if d.get("retrieved_document_ids"):
                        try:
                            d["retrieved_document_ids"] = json.loads(d["retrieved_document_ids"])
                        except Exception:
                            d["retrieved_document_ids"] = []
                    results.append(d)
                return results
        except Exception as e:
            logger.error(f"Failed to fetch experiment results: {e}")
            return []

    # ------------------------------------------------------------------ #
    # Export methods                                                        #
    # ------------------------------------------------------------------ #

    def export_to_csv(self, output_path: str, experiment_id: str = None) -> None:
        """Export experiment_results to a CSV file."""
        results = self.get_all_experiment_results(experiment_id)
        if not results:
            logger.warning("No results to export.")
            return
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            for row in results:
                row["retrieved_document_ids"] = json.dumps(row.get("retrieved_document_ids", []))
                writer.writerow(row)
        logger.info(f"Exported {len(results)} rows to {output_path}")

    def export_to_json(self, output_path: str, experiment_id: str = None) -> None:
        """Export experiment_results to a JSON file."""
        results = self.get_all_experiment_results(experiment_id)
        if not results:
            logger.warning("No results to export.")
            return
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Exported {len(results)} rows to {output_path}")
