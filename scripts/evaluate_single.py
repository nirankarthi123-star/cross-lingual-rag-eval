"""
evaluate_single.py - Phase 8 Development Evaluation Script
Usage:
    python scripts/evaluate_single.py

Demonstrates a single faithfulness evaluation call using mock data.
Requires GROQ_API_KEY to be set in .env for real LLM calls.
"""
import json
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.settings import get_settings

# ─── Sample data ─────────────────────────────────────────────────────────────

SAMPLE_QUERY = "What is the eligibility for undergraduate admission?"

SAMPLE_CONTEXT = """--- Document 1 ---
To be eligible for undergraduate admission, candidates must have completed their 10+2 
(Higher Secondary) examination with a minimum of 60% aggregate marks from a recognized board.
Candidates appearing in the qualifying examination are also eligible to apply.

--- Document 2 ---
The minimum age requirement for admission is 17 years as of the date of admission.
There is no upper age limit for most programmes."""

SAMPLE_ANSWER_FAITHFUL = (
    "Candidates must have completed 10+2 with at least 60% aggregate marks. "
    "The minimum age is 17 years and there is no upper age limit."
)

SAMPLE_ANSWER_WITH_HALLUCINATION = (
    "Candidates need a minimum of 75% in their 12th grade exams. "
    "They must also have completed an entrance exam like JEE."
)


def run_evaluation(answer: str, context: str, label: str):
    settings = get_settings()
    print(f"\n{'='*60}")
    print(f"Evaluation: {label}")
    print(f"{'='*60}")
    print(f"JUDGE MODEL       : {settings.JUDGE_LLM_MODEL}")
    print(f"JUDGE PROMPT VER  : {settings.JUDGE_PROMPT_VERSION}")
    print(f"HALLUC. THRESHOLD : {settings.HALLUCINATION_THRESHOLD}")
    print()

    try:
        from backend.llm.groq_provider import GroqProvider
        from backend.evaluation.llm_judge import LLMFaithfulnessJudge

        llm = GroqProvider()
        judge = LLMFaithfulnessJudge(llm=llm)
        result = judge.evaluate(answer=answer, context=context)

        print(f"FAITHFULNESS SCORE : {result.faithfulness_score:.4f}")
        print(f"HALLUCINATION FLAG : {result.hallucination_flag}")
        print(f"EXPLANATION        :")
        print(f"  {result.explanation}")
        return result

    except ValueError as e:
        print(f"[ERROR] {e}")
        print("  → Set GROQ_API_KEY in your .env file to run a live evaluation.")
        sys.exit(1)


def main():
    print("Phase 8: Faithfulness Evaluation Demo")
    print("Using two sample answers — one faithful, one with hallucinations.")

    # Test 1: Faithful answer
    result_good = run_evaluation(
        answer=SAMPLE_ANSWER_FAITHFUL,
        context=SAMPLE_CONTEXT,
        label="Faithful Answer (expected score ≥ 0.8)"
    )

    # Test 2: Hallucinated answer
    result_bad = run_evaluation(
        answer=SAMPLE_ANSWER_WITH_HALLUCINATION,
        context=SAMPLE_CONTEXT,
        label="Hallucinated Answer (expected score < 0.8)"
    )

    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"Faithful answer   → score={result_good.faithfulness_score:.4f} | hallucination={result_good.hallucination_flag}")
    print(f"Hallucinated ans. → score={result_bad.faithfulness_score:.4f} | hallucination={result_bad.hallucination_flag}")

    # Optionally persist results to SQLite
    from backend.database.sqlite_client import SQLiteClient
    db = SQLiteClient()
    for answer, result, label in [
        (SAMPLE_ANSWER_FAITHFUL, result_good, "faithful"),
        (SAMPLE_ANSWER_WITH_HALLUCINATION, result_bad, "hallucinated"),
    ]:
        row_id = db.save_evaluation(
            query=SAMPLE_QUERY,
            answer=answer,
            context=SAMPLE_CONTEXT,
            score=result.faithfulness_score,
            flag=result.hallucination_flag,
            explanation=result.explanation,
            model=result.judge_model,
            version=result.judge_prompt_version,
        )
        print(f"  Saved [{label}] evaluation → row_id={row_id}")

    print(f"\nResults persisted to: data/rag_eval.db")
    print("Done.")


if __name__ == "__main__":
    main()
