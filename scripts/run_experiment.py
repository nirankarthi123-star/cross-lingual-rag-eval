"""
run_experiment.py — Phase 9 Experiment Runner CLI

Usage:
    # Dry-run: show all 6 conditions without making API calls
    python scripts/run_experiment.py --all --dry-run

    # Run all 6 conditions
    python scripts/run_experiment.py --all

    # Run a specific language only
    python scripts/run_experiment.py --language english
    python scripts/run_experiment.py --language tamil_english
    python scripts/run_experiment.py --language hindi_english

    # Run a specific mitigation condition only
    python scripts/run_experiment.py --mitigation on
    python scripts/run_experiment.py --mitigation off

    # Combine filters
    python scripts/run_experiment.py --language english --mitigation off

    # Use a custom dataset file
    python scripts/run_experiment.py --all --dataset data/queries/sample_queries.json

    # Export results
    python scripts/run_experiment.py --export-csv results/output.csv
    python scripts/run_experiment.py --export-json results/output.json
"""
import argparse
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.logging import setup_logging
from backend.database.sqlite_client import SQLiteClient
from backend.dataset.loader import QueryLoader
from backend.experiments.matrix import generate_matrix, LANGUAGES
from backend.experiments.runner import ExperimentRunner

setup_logging()
logger = logging.getLogger("run_experiment")


DEFAULT_DATASET = "data/queries/sample_queries.json"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the cross-lingual RAG faithfulness experiment.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # What to run
    parser.add_argument(
        "--all", action="store_true",
        help="Run all 6 experimental conditions (3 languages × 2 mitigation settings)."
    )
    parser.add_argument(
        "--language", choices=LANGUAGES, default=None,
        help="Filter to a single language condition."
    )
    parser.add_argument(
        "--mitigation", choices=["on", "off"], default=None,
        help="Filter to a single mitigation condition."
    )

    # Options
    parser.add_argument(
        "--dataset", default=DEFAULT_DATASET,
        help=f"Path to query dataset JSON/CSV. Default: {DEFAULT_DATASET}"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be executed without making any API calls."
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="Seconds to sleep between API calls (rate-limit buffer). Default: 0.5"
    )

    # Export
    parser.add_argument(
        "--export-csv", metavar="PATH", default=None,
        help="Export experiment results to a CSV file and exit."
    )
    parser.add_argument(
        "--export-json", metavar="PATH", default=None,
        help="Export experiment results to a JSON file and exit."
    )
    parser.add_argument(
        "--experiment-id", default=None,
        help="Filter exports to a specific experiment_id."
    )

    return parser.parse_args()


def main():
    args = parse_args()
    db = SQLiteClient()

    # ── Export mode ──────────────────────────────────────────────────────
    if args.export_csv:
        db.export_to_csv(args.export_csv, args.experiment_id)
        print(f"Exported to {args.export_csv}")
        return

    if args.export_json:
        db.export_to_json(args.export_json, args.experiment_id)
        print(f"Exported to {args.export_json}")
        return

    # ── Validate: at least one condition selector is provided ────────────
    if not args.all and args.language is None and args.mitigation is None:
        print("ERROR: Specify --all, --language, --mitigation, or an export flag.")
        print("       Run with --help for usage.")
        sys.exit(1)

    # ── Load dataset ─────────────────────────────────────────────────────
    logger.info(f"Loading query dataset: {args.dataset}")
    try:
        query_records = QueryLoader.load(args.dataset)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info(f"Loaded {len(query_records)} query records.")

    # ── Determine language filter ─────────────────────────────────────────
    language_filter = None
    if args.language:
        language_filter = [args.language]
    # --all with no --language → all languages

    # ── Generate matrix ───────────────────────────────────────────────────
    matrix = generate_matrix(
        query_records=query_records,
        dataset_path=args.dataset,
        languages=language_filter,
        mitigation_filter=args.mitigation,
    )

    if not matrix:
        print("No runs matched the given filters. Check --language and --mitigation flags.")
        sys.exit(0)

    runner = ExperimentRunner(db=db)

    # ── Dry-run ────────────────────────────────────────────────────────────
    if args.dry_run:
        runner.dry_run(matrix)
        return

    # ── Persist configs for reproducibility ──────────────────────────────
    seen_configs = set()
    for config, _, _ in matrix:
        if config.experiment_id not in seen_configs:
            db.save_experiment_config(config)
            seen_configs.add(config.experiment_id)

    # ── Run ────────────────────────────────────────────────────────────────
    print(f"\nStarting experiment: {len(matrix)} total runs.")
    results = runner.run_all(matrix, delay_between_runs=args.delay)

    # ── Summary ────────────────────────────────────────────────────────────
    completed = [r for r in results if not r.error]
    failed    = [r for r in results if r.error]

    print(f"\n{'='*60}")
    print("Experiment Complete")
    print(f"{'='*60}")
    print(f"  Runs executed : {len(results)}")
    print(f"  Completed     : {len(completed)}")
    print(f"  Failed        : {len(failed)}")

    if completed:
        scores = [r.faithfulness_score for r in completed if r.faithfulness_score is not None]
        if scores:
            print(f"  Avg faith. score : {sum(scores)/len(scores):.4f}")
        halluc = [r for r in completed if r.hallucination_flag is True]
        print(f"  Hallucinations   : {len(halluc)}/{len(completed)}")

    if failed:
        print(f"\n  Failed runs:")
        for r in failed[:5]:
            print(f"    [{r.experiment_id}] q={r.question_id}: {r.error[:100]}")

    print(f"\nResults stored in: data/rag_eval.db")
    print(f"Export with: python scripts/run_experiment.py --export-csv results/output.csv")


if __name__ == "__main__":
    main()
