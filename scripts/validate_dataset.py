#!/usr/bin/env python3
"""
Command-line entry point to validate processed documents and chunks in data/processed/.
Usage:
    python scripts/validate_dataset.py [--processed-dir data/processed]
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is in python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.config.settings import get_settings
from backend.retrieval.validator import validate_dataset


def main():
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Validate processed RAG dataset documents and chunks.")
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path(settings.PROCESSED_DIR),
        help="Path to processed directory containing documents.jsonl and chunks.jsonl",
    )

    args = parser.parse_args()
    if not args.processed_dir.exists():
        print(f"Error: Processed directory '{args.processed_dir}' does not exist.")
        sys.exit(1)

    stats = validate_dataset(processed_dir=args.processed_dir)
    stats.print_summary()

    if stats.empty_documents > 0 or stats.empty_chunks > 0:
        print("[!] Validation completed with warnings/empty items.")
        sys.exit(1)
    else:
        print("[PASS] All dataset integrity checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
