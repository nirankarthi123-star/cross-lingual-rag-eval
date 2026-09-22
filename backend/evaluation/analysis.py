import statistics
import math
import logging
from typing import List, Dict, Any, Tuple
try:
    from scipy.stats import wilcoxon
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

logger = logging.getLogger(__name__)

# The 6 required conditions
REQUIRED_CONDITIONS = [
    ("english", False),
    ("tamil_english", False),
    ("hindi_english", False),
    ("english", True),
    ("tamil_english", True),
    ("hindi_english", True),
]

def format_condition_name(language: str, mitigation_enabled: bool) -> str:
    mit = "mitigated" if mitigation_enabled else "baseline"
    return f"{language}_{mit}"

def load_and_validate_data(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validates experiment records.
    Returns (valid_records, excluded_records).
    """
    valid = []
    excluded = []
    seen = set()

    for r in records:
        reason = None
        
        # Check required fields
        if not r.get("question_id"):
            reason = "missing question_id"
        elif not r.get("language"):
            reason = "missing language"
        elif r.get("mitigation_enabled") is None:
            reason = "missing mitigation condition"
        elif r.get("faithfulness_score") is None:
            reason = "missing faithfulness score"
        elif r.get("hallucination_flag") is None:
            reason = "missing hallucination flag"
        elif not r.get("generated_answer"):
            reason = "missing answer"
        elif not r.get("retrieved_context"):
            reason = "missing retrieved context"
        else:
            # Check bounds
            score = float(r["faithfulness_score"])
            if score < 0.0 or score > 1.0:
                reason = "invalid faithfulness score outside [0.0, 1.0]"
            
            # Check duplicates (experiment_id, question_id, language, mitigation_enabled)
            exp_id = r.get("experiment_id", "unknown")
            qid = r["question_id"]
            lang = r["language"]
            mit = bool(r["mitigation_enabled"])
            key = (exp_id, qid, lang, mit)
            
            if key in seen:
                reason = "duplicate record"
            else:
                seen.add(key)
        
        if reason:
            r["_exclusion_reason"] = reason
            excluded.append(r)
        else:
            # Normalize boolean flag
            r["mitigation_enabled"] = bool(r["mitigation_enabled"])
            r["hallucination_flag"] = bool(r["hallucination_flag"])
            r["faithfulness_score"] = float(r["faithfulness_score"])
            valid.append(r)
            
    return valid, excluded

def compute_descriptive_stats(valid_records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Computes mean, median, std_dev, min, max, hallucination rate for all 6 conditions.
    """
    # Group by condition
    groups = {format_condition_name(lang, mit): [] for lang, mit in REQUIRED_CONDITIONS}
    
    for r in valid_records:
        cond = format_condition_name(r["language"], r["mitigation_enabled"])
        if cond in groups:
            groups[cond].append(r)
            
    stats = {}
    for cond_name, group in groups.items():
        n = len(group)
        if n == 0:
            stats[cond_name] = {
                "n": 0, "mean": None, "median": None, "std_dev": None, 
                "hallucination_rate": None, "min": None, "max": None
            }
            continue
            
        scores = [r["faithfulness_score"] for r in group]
        hallucinations = sum(1 for r in group if r["hallucination_flag"])
        
        mean_val = statistics.mean(scores)
        median_val = statistics.median(scores)
        std_dev = statistics.stdev(scores) if n > 1 else 0.0
        hal_rate = hallucinations / n
        min_val = min(scores)
        max_val = max(scores)
        
        stats[cond_name] = {
            "n": n,
            "mean": round(mean_val, 4),
            "median": round(median_val, 4),
            "std_dev": round(std_dev, 4),
            "hallucination_rate": round(hal_rate, 4),
            "min": round(min_val, 4),
            "max": round(max_val, 4)
        }
        
    return stats

def run_paired_comparisons(valid_records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Runs Wilcoxon signed-rank tests for required pairs.
    Matches strictly on question_id.
    Returns (results, missing_pairs_log).
    """
    # Organize by (question_id) -> condition -> record
    q_map = {}
    for r in valid_records:
        qid = r["question_id"]
        cond = format_condition_name(r["language"], r["mitigation_enabled"])
        if qid not in q_map:
            q_map[qid] = {}
        q_map[qid][cond] = r

    comparisons_to_run = [
        ("English baseline vs Tamil-English baseline", "english_baseline", "tamil_english_baseline"),
        ("English baseline vs Hindi-English baseline", "english_baseline", "hindi_english_baseline"),
        ("Tamil-English baseline vs Tamil-English mitigated", "tamil_english_baseline", "tamil_english_mitigated"),
        ("Hindi-English baseline vs Hindi-English mitigated", "hindi_english_baseline", "hindi_english_mitigated"),
        ("Tamil-English mitigated vs English baseline", "tamil_english_mitigated", "english_baseline"),
        ("Hindi-English mitigated vs English baseline", "hindi_english_mitigated", "english_baseline"),
    ]
    
    results = []
    missing_pairs_log = []
    
    for comp_name, cond1, cond2 in comparisons_to_run:
        pairs1 = []
        pairs2 = []
        
        for qid, c_dict in q_map.items():
            if cond1 in c_dict and cond2 in c_dict:
                pairs1.append(c_dict[cond1]["faithfulness_score"])
                pairs2.append(c_dict[cond2]["faithfulness_score"])
            else:
                if cond1 in c_dict or cond2 in c_dict:
                    missing_pairs_log.append({
                        "comparison": comp_name,
                        "question_id": qid,
                        "missing_cond1": cond1 not in c_dict,
                        "missing_cond2": cond2 not in c_dict
                    })
                    
        n_pairs = len(pairs1)
        if n_pairs < 2:
            results.append({
                "comparison": comp_name,
                "n": n_pairs,
                "status": "INSUFFICIENT DATA",
                "reason": "n < 2 pairs",
                "mean_diff": None, "median_diff": None, "statistic": None, "p_value": None, "interpretation": None
            })
            continue
            
        diffs = [x - y for x, y in zip(pairs1, pairs2)]
        mean_diff = statistics.mean(diffs)
        median_diff = statistics.median(diffs)
        
        # Check if all diffs are zero
        if all(d == 0 for d in diffs):
            results.append({
                "comparison": comp_name,
                "n": n_pairs,
                "status": "NOT TESTABLE",
                "reason": "All paired differences are zero",
                "mean_diff": round(mean_diff, 4), "median_diff": round(median_diff, 4), 
                "statistic": None, "p_value": None, "interpretation": None
            })
            continue
            
        if not SCIPY_AVAILABLE:
            results.append({
                "comparison": comp_name,
                "n": n_pairs,
                "status": "NOT TESTABLE",
                "reason": "scipy not installed",
                "mean_diff": round(mean_diff, 4), "median_diff": round(median_diff, 4), 
                "statistic": None, "p_value": None, "interpretation": None
            })
            continue
            
        # Run Wilcoxon
        try:
            # We use two-sided
            stat, p_val = wilcoxon(pairs1, pairs2, zero_method="wilcox", correction=False)
            is_sig = bool(p_val < 0.05)
            interp = "statistically significant" if is_sig else "not significant"
            
            results.append({
                "comparison": comp_name,
                "n": n_pairs,
                "status": "TESTED",
                "reason": None,
                "mean_diff": round(mean_diff, 4),
                "median_diff": round(median_diff, 4),
                "statistic": float(stat),
                "p_value": float(p_val),
                "interpretation": interp
            })
        except Exception as e:
            results.append({
                "comparison": comp_name,
                "n": n_pairs,
                "status": "NOT TESTABLE",
                "reason": f"wilcoxon error: {str(e)}",
                "mean_diff": round(mean_diff, 4), "median_diff": round(median_diff, 4), 
                "statistic": None, "p_value": None, "interpretation": None
            })
            
    return results, missing_pairs_log

def evaluate_success_criterion(stats: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Evaluates: English baseline mean - mitigated code-mixed mean <= 0.10
    For Tamil-English mitigated vs English baseline
    For Hindi-English mitigated vs English baseline
    """
    results = []
    
    eng_base = stats.get("english_baseline", {})
    eng_base_mean = eng_base.get("mean")
    
    targets = [
        ("Tamil-English mitigated versus English baseline", "tamil_english_mitigated"),
        ("Hindi-English mitigated versus English baseline", "hindi_english_mitigated")
    ]
    
    for name, cond_key in targets:
        mit_cond = stats.get(cond_key, {})
        mit_mean = mit_cond.get("mean")
        
        if eng_base_mean is None or mit_mean is None:
            results.append({
                "comparison": name,
                "english_baseline_mean": eng_base_mean,
                "mitigated_mean": mit_mean,
                "difference": None,
                "decision": "INSUFFICIENT DATA"
            })
        else:
            diff = eng_base_mean - mit_mean
            decision = "MET" if diff <= 0.10 else "NOT MET"
            results.append({
                "comparison": name,
                "english_baseline_mean": eng_base_mean,
                "mitigated_mean": mit_mean,
                "difference": round(diff, 4),
                "decision": decision
            })
            
    return results
