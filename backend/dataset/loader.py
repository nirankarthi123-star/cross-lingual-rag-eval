import csv
import json
from pathlib import Path
from typing import List

from backend.dataset.schemas import QueryRecord

class QueryLoader:
    """
    Loads query datasets from CSV or JSON/JSONL formats into QueryRecord objects.
    """
    
    @staticmethod
    def load(file_path: str | Path) -> List[QueryRecord]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")

        ext = path.suffix.lower()
        if ext == ".csv":
            return QueryLoader._load_csv(path)
        elif ext in [".json", ".jsonl"]:
            return QueryLoader._load_json(path)
        else:
            raise ValueError(f"Unsupported dataset format: {ext}. Use .csv, .json, or .jsonl")

    @staticmethod
    def _load_csv(path: Path) -> List[QueryRecord]:
        records = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert expected_document_ids from a comma-separated string if it exists
                expected_ids_str = row.get("expected_document_ids", "")
                if expected_ids_str:
                    row["expected_document_ids"] = [x.strip() for x in expected_ids_str.split(",") if x.strip()]
                else:
                    row["expected_document_ids"] = []
                
                # Parse the record via Pydantic
                records.append(QueryRecord.model_validate(row))
        return records

    @staticmethod
    def _load_json(path: Path) -> List[QueryRecord]:
        records = []
        with open(path, "r", encoding="utf-8") as f:
            # First try parsing as a standard JSON array
            try:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        records.append(QueryRecord.model_validate(item))
                    return records
            except json.JSONDecodeError:
                # If it fails, assume it's JSONL (one JSON object per line)
                pass

        # Parse as JSONL
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    item = json.loads(line)
                    records.append(QueryRecord.model_validate(item))
        return records
