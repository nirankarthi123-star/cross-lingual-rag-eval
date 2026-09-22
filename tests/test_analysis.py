import pytest
from backend.evaluation.analysis import (
    load_and_validate_data,
    compute_descriptive_stats,
    run_paired_comparisons,
    evaluate_success_criterion,
    SCIPY_AVAILABLE
)

def get_base_record(qid="Q1", lang="english", mit=False, score=0.8, hal=False):
    return {
        "experiment_id": "exp1",
        "question_id": qid,
        "language": lang,
        "mitigation_enabled": mit,
        "faithfulness_score": score,
        "hallucination_flag": hal,
        "generated_answer": "answer",
        "retrieved_context": "context"
    }

def test_validation_logic():
    # Valid
    valid, excluded = load_and_validate_data([get_base_record()])
    assert len(valid) == 1
    assert len(excluded) == 0

    # Missing fields
    missing_ans = get_base_record()
    del missing_ans["generated_answer"]
    
    missing_score = get_base_record()
    del missing_score["faithfulness_score"]
    
    valid, excluded = load_and_validate_data([missing_ans, missing_score])
    assert len(valid) == 0
    assert len(excluded) == 2

    # Bounds
    out_of_bounds = get_base_record(score=1.5)
    valid, excluded = load_and_validate_data([out_of_bounds])
    assert len(valid) == 0
    assert len(excluded) == 1
    assert excluded[0]["_exclusion_reason"] == "invalid faithfulness score outside [0.0, 1.0]"

    # Duplicates
    dup1 = get_base_record()
    dup2 = get_base_record() # same exact keys
    valid, excluded = load_and_validate_data([dup1, dup2])
    assert len(valid) == 1
    assert len(excluded) == 1
    assert excluded[0]["_exclusion_reason"] == "duplicate record"

def test_descriptive_stats():
    records = [
        get_base_record(score=0.8, hal=False),
        get_base_record(score=0.4, hal=True),
    ]
    stats = compute_descriptive_stats(records)
    
    eng_base = stats["english_baseline"]
    assert eng_base["n"] == 2
    assert eng_base["mean"] == 0.6
    assert eng_base["hallucination_rate"] == 0.5
    assert eng_base["min"] == 0.4
    assert eng_base["max"] == 0.8
    assert eng_base["median"] == 0.6

    # Missing condition handled gracefully
    eng_mit = stats["english_mitigated"]
    assert eng_mit["n"] == 0
    assert eng_mit["mean"] is None

def test_wilcoxon_paired_comparisons():
    # Setup paired records
    records = [
        # Q1: Eng Base vs Tamil Base
        get_base_record("Q1", "english", False, 0.9),
        get_base_record("Q1", "tamil_english", False, 0.7),
        # Q2: Eng Base vs Tamil Base
        get_base_record("Q2", "english", False, 0.8),
        get_base_record("Q2", "tamil_english", False, 0.6),
        # Q3 (missing pair)
        get_base_record("Q3", "english", False, 0.8),
    ]
    
    results, missing_pairs = run_paired_comparisons(records)
    
    # Eng vs Tamil base
    eng_vs_tam = [r for r in results if r["comparison"] == "English baseline vs Tamil-English baseline"][0]
    assert eng_vs_tam["n"] == 2
    assert eng_vs_tam["mean_diff"] == pytest.approx(0.2)
    
    if SCIPY_AVAILABLE:
        # With n=2, wilcoxon might throw a warning or just run. It might not be significant.
        assert eng_vs_tam["status"] == "TESTED"
    else:
        assert eng_vs_tam["status"] == "NOT TESTABLE"

    # Missing pair should be logged
    missing_q3 = [m for m in missing_pairs if m["question_id"] == "Q3"]
    assert len(missing_q3) > 0
    assert missing_q3[0]["missing_cond2"] is True

def test_wilcoxon_zero_variance():
    records = [
        get_base_record("Q1", "english", False, 0.8),
        get_base_record("Q1", "tamil_english", False, 0.8),
        get_base_record("Q2", "english", False, 0.8),
        get_base_record("Q2", "tamil_english", False, 0.8),
    ]
    results, _ = run_paired_comparisons(records)
    eng_vs_tam = [r for r in results if r["comparison"] == "English baseline vs Tamil-English baseline"][0]
    
    # Diffs are zero, Wilcoxon should skip and report NOT TESTABLE
    assert eng_vs_tam["status"] == "NOT TESTABLE"
    assert eng_vs_tam["reason"] == "All paired differences are zero"
    assert eng_vs_tam["mean_diff"] == 0.0

def test_success_criterion():
    stats = {
        "english_baseline": {"mean": 0.85},
        "tamil_english_mitigated": {"mean": 0.80}, # Diff: 0.05 (MET)
        "hindi_english_mitigated": {"mean": 0.70}, # Diff: 0.15 (NOT MET)
        "hindi_english_baseline": {"mean": 0.60}
    }
    
    results = evaluate_success_criterion(stats)
    
    tamil = [r for r in results if "Tamil" in r["comparison"]][0]
    hindi = [r for r in results if "Hindi" in r["comparison"]][0]
    
    assert tamil["difference"] == pytest.approx(0.05)
    assert tamil["decision"] == "MET"
    
    assert hindi["difference"] == pytest.approx(0.15)
    assert hindi["decision"] == "NOT MET"
    
def test_success_criterion_insufficient_data():
    stats = {
        "english_baseline": {"mean": 0.85},
        "tamil_english_mitigated": {"mean": None}, 
    }
    results = evaluate_success_criterion(stats)
    tamil = [r for r in results if "Tamil" in r["comparison"]][0]
    assert tamil["decision"] == "INSUFFICIENT DATA"
    assert tamil["difference"] is None
