import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from backend.dataset.loader import QueryLoader

def validate_dataset(file_path: str):
    path = Path(file_path)
    print(f"[INFO] Validating dataset: {path.name} ...")
    
    try:
        records = QueryLoader.load(path)
    except Exception as e:
        print(f"[ERROR] Failed to load dataset. It may be malformed. Error: {e}")
        sys.exit(1)
        
    print(f"[INFO] Successfully parsed {len(records)} records. Checking constraints...")
    
    seen_ids = set()
    seen_english = set()
    seen_tamil = set()
    seen_hindi = set()
    
    errors = []
    
    for idx, rec in enumerate(records):
        # 1. Unique Question IDs
        if rec.question_id in seen_ids:
            errors.append(f"Row {idx+1}: Duplicate question_id found -> {rec.question_id}")
        seen_ids.add(rec.question_id)
        
        # 2. Check for exact duplicate query variants (which suggests a bad copy-paste or lack of diversity)
        if rec.english.lower() in seen_english:
            errors.append(f"Row {idx+1}: Duplicate English query found -> {rec.english}")
        seen_english.add(rec.english.lower())
        
        if rec.tamil_english.lower() in seen_tamil:
            errors.append(f"Row {idx+1}: Duplicate Tamil-English query found -> {rec.tamil_english}")
        seen_tamil.add(rec.tamil_english.lower())
        
        if rec.hindi_english.lower() in seen_hindi:
            errors.append(f"Row {idx+1}: Duplicate Hindi-English query found -> {rec.hindi_english}")
        seen_hindi.add(rec.hindi_english.lower())
        
        # 3. Pydantic schema validation handles empty strings automatically (via @field_validator in schemas.py)

    if errors:
        print("\n[FAILED] Validation failed with the following errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Dataset passed all validation checks!")
        print(f"Total Unique Base Questions: {len(records)}")
        print(f"Total Query Variants: {len(records) * 3}")

def main():
    parser = argparse.ArgumentParser(description="Validate a query dataset CSV or JSON file.")
    parser.add_argument("file_path", type=str, help="Path to the dataset file (.json or .csv)")
    
    args = parser.parse_args()
    validate_dataset(args.file_path)

if __name__ == "__main__":
    main()
