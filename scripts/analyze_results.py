"""
analyze_results.py — Phase 10 Analysis Pipeline CLI
"""
import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.logging import setup_logging
from backend.database.sqlite_client import SQLiteClient
from backend.evaluation.analysis import (
    load_and_validate_data,
    compute_descriptive_stats,
    run_paired_comparisons,
    evaluate_success_criterion
)

setup_logging()
logger = logging.getLogger("analyze_results")

def parse_args():
    parser = argparse.ArgumentParser(description="Run statistical analysis on experiment results.")
    parser.add_argument("--db", default="data/rag_eval.db", help="Path to SQLite DB.")
    parser.add_argument("--experiment-id", default=None, help="Filter to a specific experiment ID.")
    parser.add_argument("--output-dir", default="results/analysis", help="Directory for analysis outputs.")
    parser.add_argument("--mock-data", action="store_true", help="Acknowledge analyzing mock/test data.")
    return parser.parse_args()

def write_csv(filepath, data, fieldnames=None):
    if not data:
        return
    if not fieldnames:
        fieldnames = data[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def generate_markdown_report(filepath, summary_data):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Phase 10 Analysis Summary\n\n")
        f.write(f"**Generated:** {summary_data['timestamp']}\n")
        f.write(f"**Data Classification:** {summary_data['data_classification']}\n\n")
        
        if summary_data['data_classification'] == "MOCK/TEST":
            f.write("> **WARNING:** This analysis was run on mock/test data. These are NOT research findings.\n\n")
            
        f.write("## Validation Summary\n")
        f.write(f"- Source Records: {summary_data['source_record_count']}\n")
        f.write(f"- Valid Records: {summary_data['valid_record_count']}\n")
        f.write(f"- Excluded Records: {summary_data['excluded_record_count']}\n\n")
        
        f.write("## Descriptive Statistics\n")
        f.write("| Condition | n | Mean | Median | Std Dev | Hal. Rate | Min | Max |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for cond, stats in summary_data["condition_summaries"].items():
            f.write(f"| {cond} | {stats['n']} | {stats['mean']} | {stats['median']} | {stats['std_dev']} | {stats['hallucination_rate']} | {stats['min']} | {stats['max']} |\n")
            
        f.write("\n## Paired Comparisons (Wilcoxon)\n")
        f.write("| Comparison | n | Mean Diff | p-value | Interpretation | Status | Reason |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for comp in summary_data["paired_comparisons"]:
            f.write(f"| {comp['comparison']} | {comp['n']} | {comp['mean_diff']} | {comp['p_value']} | {comp['interpretation']} | {comp['status']} | {comp.get('reason', '')} |\n")
            
        f.write("\n## Success Criterion\n")
        f.write("> Criterion: English baseline mean - Mitigated code-mixed mean <= 0.10\n\n")
        f.write("| Comparison | Eng Base Mean | Mitigated Mean | Difference | Decision |\n")
        f.write("|---|---|---|---|---|\n")
        for sc in summary_data["success_criterion"]:
            f.write(f"| {sc['comparison']} | {sc['english_baseline_mean']} | {sc['mitigated_mean']} | {sc['difference']} | **{sc['decision']}** |\n")


def generate_dashboard_data(filepath, stats):
    """Generates chart-ready JSON data for dashboards."""
    chart_data = {
        "mean_faithfulness_by_condition": {k: v["mean"] for k, v in stats.items()},
        "hallucination_rate_by_condition": {k: v["hallucination_rate"] for k, v in stats.items()}
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chart_data, f, indent=2)


def main():
    args = parse_args()
    
    if not os.path.exists(args.db):
        logger.error(f"Database not found at {args.db}")
        sys.exit(1)
        
    db = SQLiteClient(args.db)
    raw_records = db.get_all_experiment_results(args.experiment_id)
    
    source_count = len(raw_records)
    if source_count == 0:
        logger.error("No experiment records found.")
        sys.exit(1)
        
    # Check mock data heuristic (if any record contains "SMOKE" or "test", or explicit flag)
    is_mock = args.mock_data
    if not is_mock:
        for r in raw_records:
            if "SMOKE" in r.get("question_id", "") or "test" in r.get("experiment_id", ""):
                is_mock = True
                break
                
    classification = "MOCK/TEST" if is_mock else "ACTUAL"
    if classification == "MOCK/TEST" and not args.mock_data:
        logger.warning("Detected mock/test data in the DB. Treating analysis as MOCK.")

    valid_records, excluded_records = load_and_validate_data(raw_records)
    
    stats = compute_descriptive_stats(valid_records)
    paired_results, missing_pairs = run_paired_comparisons(valid_records)
    success_results = evaluate_success_criterion(stats)
    
    # Create outputs
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. CSV files
    stats_rows = [{"condition": k, **v} for k, v in stats.items()]
    write_csv(out_dir / "condition_summary.csv", stats_rows)
    write_csv(out_dir / "paired_comparisons.csv", paired_results)
    write_csv(out_dir / "success_criterion.csv", success_results)
    write_csv(out_dir / "excluded_records.csv", excluded_records)
    write_csv(out_dir / "missing_pairs.csv", missing_pairs)
    
    # 2. JSON Summary
    summary_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_db": args.db,
        "experiment_id_filter": args.experiment_id,
        "source_record_count": source_count,
        "valid_record_count": len(valid_records),
        "excluded_record_count": len(excluded_records),
        "data_classification": classification,
        "condition_summaries": stats,
        "paired_comparisons": paired_results,
        "success_criterion": success_results,
        "missing_pairs": missing_pairs,
        "generated_files": [
            str(out_dir / "condition_summary.csv"),
            str(out_dir / "paired_comparisons.csv"),
            str(out_dir / "success_criterion.csv"),
            str(out_dir / "excluded_records.csv"),
            str(out_dir / "phase10_summary.md"),
            str(out_dir / "chart_data.json")
        ]
    }
    
    with open(out_dir / "analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
        
    # 3. Markdown Report
    generate_markdown_report(out_dir / "phase10_summary.md", summary_data)
    
    # 4. Chart Data
    generate_dashboard_data(out_dir / "chart_data.json", stats)
    
    # Log completion
    logger.info(f"Analysis complete. Found {len(valid_records)} valid records.")
    logger.info(f"Data Classification: {classification}")
    logger.info(f"Outputs written to {args.output_dir}")

if __name__ == "__main__":
    main()
