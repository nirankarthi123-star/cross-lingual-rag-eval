"""
Build and verify the frozen production corpus release (corpus_v_final).
Reads from data/documents, writes to research/releases/corpus_v_final,
and builds an isolated versioned index.
"""
import os
import shutil
import hashlib
import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "data" / "documents"
RELEASE_DIR = BASE_DIR / "research" / "releases" / "corpus_v_final"
RELEASE_DOCS_DIR = RELEASE_DIR / "documents"
PROCESSED_DIR = RELEASE_DIR / "processed"
VECTOR_DIR = RELEASE_DIR / "vector_store"

RELEASE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR.mkdir(parents=True, exist_ok=True)

DOC_METADATA = {
    "banking_faq.json": {
        "source": "Author-created synthetic academic evaluation data (AI assistant, 2026-09-09)",
        "access_date": "2026-09-09",
        "license": "Author-created synthetic fixture; internal academic project use only",
        "domain": "Retail Banking",
        "decision": "INCLUDED_AS_SYNTHETIC_FIXTURE",
        "role": "Retail banking test fixture & distractor"
    },
    "campus_library_guide.pdf": {
        "source": "Author-created synthetic test fixture (scripts/create_sample_pdf.py, 2026-09-09)",
        "access_date": "2026-09-09",
        "license": "Author-created synthetic fixture; internal academic project use only",
        "domain": "Academic/Library",
        "decision": "INCLUDED_AS_SYNTHETIC_FIXTURE",
        "role": "Pilot loader test fixture & domain distractor"
    },
    "code_of_ethics.txt": {
        "source": "Researcher-curated abridged extract derived from official State Bank of India Code of Ethics source (https://sbi.bank.in/documents/17826/20624/251024-ABRIDGED%2BCODE%2BOF%2BETHICS%2BV-2.0.pdf/ab38b9e2-f39a-cd00-4550-569bf5c9f11c?t=1729847862207)",
        "access_date": "2026-10-27",
        "license": "Publicly accessible official document extract; redistribution rights not assumed; fair dealing for non-commercial academic research",
        "domain": "Banking/Ethics",
        "decision": "INCLUDED_OFFICIAL_EXTRACT",
        "role": "Primary retrieval corpus for Banking Ethics queries"
    },
    "digital_and_transaction_banking_products.txt": {
        "source": "Official State Bank of India Digital & Transaction Banking Booklet (https://sbi.bank.in/documents/26274/26996/03022022_DTB%2BPRODUCTS%2BBOOKLET.pdf/2d562a0a-5641-7fab-4181-44879b8a6070?t=1643871923575)",
        "access_date": "2026-10-27",
        "license": "Publicly accessible official marketing booklet; redistribution rights not assumed; fair dealing for non-commercial academic research",
        "domain": "Corporate Banking",
        "decision": "INCLUDED_OFFICIAL_EXTRACT",
        "role": "Primary retrieval corpus for Digital Banking queries"
    },
    "ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf": {
        "source": "Official State Bank of India Investor Relations / CARE Analytics & Advisory (CAAPL) Impact Report (https://sbi.bank.in/documents/17836/53469043/Impact%2BReporting%2Bof%2BGreen%2BBond%2Bof%2BUSD%2B250%2BMillion.pdf/aab70f17-604e-98e7-0bc1-8d2b80987ab4?t=1751707146983)",
        "access_date": "2026-10-27",
        "license": "Publicly accessible official investor relations report; redistribution rights not assumed; fair dealing for non-commercial academic research",
        "domain": "ESG & Green Finance",
        "decision": "INCLUDED_OFFICIAL_DOCUMENT",
        "role": "Primary retrieval corpus for ESG/Green Bond queries"
    },
    "microfinance_loans_policy.txt": {
        "source": "Official State Bank of India Policy on Microfinance Loans v1.0 (https://sbi.bank.in/documents/14463/22577/20012023_Mircorfinance%20Loan%20Policy%20for%20Publication.pdf)",
        "access_date": "2026-10-26",
        "license": "Publicly accessible official regulatory policy; redistribution rights not assumed; fair dealing for non-commercial academic research",
        "domain": "Microfinance & Credit",
        "decision": "INCLUDED_OFFICIAL_EXTRACT",
        "role": "Primary retrieval corpus for Microfinance queries"
    },
    "telecom_customer_support.csv": {
        "source": "Author-created synthetic academic evaluation data (AI assistant, 2026-09-09)",
        "access_date": "2026-09-09",
        "license": "Author-created synthetic fixture; internal academic project use only",
        "domain": "Telecom Support",
        "decision": "INCLUDED_AS_SYNTHETIC_FIXTURE",
        "role": "Cross-domain test fixture & telecom queries"
    },
    "university_policies.txt": {
        "source": "Author-created synthetic academic test fixture (AI assistant, 2026-09-09)",
        "access_date": "2026-09-09",
        "license": "Author-created synthetic fixture; internal academic project use only",
        "domain": "Academic/Governance",
        "decision": "INCLUDED_AS_SYNTHETIC_FIXTURE",
        "role": "Pilot loader test fixture & domain distractor"
    }
}

def main():
    manifest_rows = [
        ["filename", "sha256", "source_url_or_author_status", "access_date", "license_terms", "domain", "inclusion_decision", "role_in_study"]
    ]

    for fname, meta in sorted(DOC_METADATA.items()):
        src_file = DOCS_DIR / fname
        dst_file = RELEASE_DOCS_DIR / fname
        shutil.copy2(src_file, dst_file)

        with open(src_file, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()

        manifest_rows.append([
            fname, h, meta["source"], meta["access_date"], meta["license"], meta["domain"], meta["decision"], meta["role"]
        ])

    manifest_path = RELEASE_DIR / "manifest.csv"
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(manifest_rows)

    with open(manifest_path, "rb") as f:
        manifest_hash = hashlib.sha256(f.read()).hexdigest()

    with open(RELEASE_DIR / "manifest.sha256", "w", encoding="utf-8") as f:
        f.write(f"{manifest_hash}  manifest.csv\n")

    print(f"Manifest written: {manifest_path}")
    print(f"Manifest SHA256: {manifest_hash}")

    # Copy processed chunks/documents to preserve exact reproducible snapshot
    shutil.copy2(BASE_DIR / "data" / "processed" / "documents.jsonl", PROCESSED_DIR / "documents.jsonl")
    shutil.copy2(BASE_DIR / "data" / "processed" / "chunks.jsonl", PROCESSED_DIR / "chunks.jsonl")
    shutil.copy2(BASE_DIR / "data" / "vector_store" / "index.faiss", VECTOR_DIR / "index.faiss")
    shutil.copy2(BASE_DIR / "data" / "vector_store" / "metadata_map.json", VECTOR_DIR / "metadata_map.json")

    # Verification checks
    with open(PROCESSED_DIR / "chunks.jsonl", "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]

    with open(PROCESSED_DIR / "documents.jsonl", "r", encoding="utf-8") as f:
        docs = [json.loads(line) for line in f if line.strip()]

    with open(VECTOR_DIR / "metadata_map.json", "r", encoding="utf-8") as f:
        meta_map = json.load(f)

    with open(BASE_DIR / "data" / "queries" / "sample_queries.json", "r", encoding="utf-8") as f:
        queries = json.load(f)

    # Check for empty chunks
    empty_chunks = [c for c in chunks if not c.get("chunk_text", "").strip()]
    print(f"Total chunks: {len(chunks)}, Empty chunks: {len(empty_chunks)}")

    # Check for duplicate document IDs
    doc_ids = [d["document_id"] for d in docs]
    unique_doc_ids = set(doc_ids)
    print(f"Total logical documents: {len(docs)}, Unique doc IDs: {len(unique_doc_ids)}")

    # Check metadata map
    print(f"Metadata map entries: {len(meta_map)}")

    # Check query expected document IDs exist
    indexed_doc_ids = set(doc_ids)
    missing_targets = []
    for q in queries:
        for eid in q.get("expected_document_ids", []):
            if eid not in indexed_doc_ids:
                missing_targets.append((q["question_id"], eid))

    print(f"Queries checked: {len(queries)}, Missing target doc IDs: {len(missing_targets)}")
    if missing_targets:
        print(f"WARNING missing targets: {missing_targets}")
    else:
        print("ALL 50 query expected_document_ids exist in the index!")

if __name__ == "__main__":
    main()
