"""Quick verification of the /api/chat endpoint with 3 test queries."""
import urllib.request
import json

queries = [
    ("English", "How do I activate international roaming on my mobile postpaid connection?"),
    ("Tamil-English", "Ennoda mobile postpaid connection-la international roaming eppadi activate panrathu?"),
    ("Hindi-English", "Mere mobile postpaid connection par international roaming kaise activate karu?"),
]

for label, q in queries:
    print(f"=== {label} ===")
    payload = json.dumps({"query": q, "mitigation_enabled": True}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8001/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            d = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ERROR: {e}")
        print()
        continue

    print(f"  code_mix_detected: {d.get('code_mix_detected')}")
    print(f"  detected_languages: {d.get('detected_languages')}")
    print(f"  mitigation_applied: {d.get('mitigation_applied')}")
    norm = d.get("normalized_query")
    print(f"  normalized_query: {norm if norm else '(not applied)'}")
    print(f"  faithfulness_score: {d.get('faithfulness_score')}")
    print(f"  hallucination_flag: {d.get('hallucination_flag')}")
    print(f"  generator_model: {d.get('generator_model')}")
    print(f"  judge_model: {d.get('judge_model')}")
    print(f"  latency: {d.get('latency')}s")
    ans = d.get("answer", "")
    print(f"  answer: {ans[:150]}...")
    print(f"  retrieval_docs: {len(d.get('retrieved_documents', []))}")
    print(f"  error: {d.get('error')}")
    print()
