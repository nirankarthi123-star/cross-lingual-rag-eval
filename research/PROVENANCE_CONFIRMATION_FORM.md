**# Research Corpus & Dataset Provenance Confirmation Form**



**\*\*Project:\*\*** Cross-Lingual RAG Faithfulness Evaluation under Code-Mixing  

**\*\*Form updated:\*\*** 2026-10-27  

**\*\*Overall status:\*\*** \`FROZEN — RESEARCHER-DECLARED; OPEN PROVENANCE LIMITATIONS RECORDED\`



\> **\*\*Basis of this form:\*\*** The researcher has declared the corpus frozen as of 2026-10-27. Project details and generation history are based on supplied project materials and researcher statements. The September 9, 2026 generation history for the four pilot fixtures has not been independently corroborated against original Antigravity session logs. SBI local-file matching and reuse-term review remain recorded limitations. This status records the researcher's freeze decision; it does not claim those checks were independently verified.



**## 1. Status definitions**



\- \`VERIFIED OFFICIAL SOURCE\`: an official publisher source has been identified and the document identity checked to the extent stated.

\- \`SYNTHETIC — RESEARCHER-REPORTED HISTORY\`: the researcher reports that the file was generated for development/testing and not copied from an external website.

\- \`PENDING\`: an exact local-file match, source history, reuse condition, or other required check remains.

\- \`NOT PROVIDED\`: information cannot be filled without the researcher's actual details.
\- \`FROZEN — RESEARCHER-DECLARED WITH OPEN LIMITATIONS\`: the researcher has frozen the current corpus snapshot, while unresolved checks remain explicitly documented and must be resolved before production evaluation or public redistribution.

\- A file being publicly accessible does not automatically mean it may be redistributed without restrictions.



**## 2. Synthetic pilot fixtures**



**### 2.1 \`data/documents/banking_faq.json\`**



\- **\*\*Internal ID:\*\*** \`DOC-CORPUS-01\`

\- **\*\*Source type:\*\*** AI-assistant-generated synthetic academic evaluation / ingestion-test data.

\- **\*\*Creation date:\*\*** 2026-09-09.

\- **\*\*Project phase:\*\*** Phase 2 — Domain Dataset and Document Processing.

\- **\*\*Reported generation step:\*\*** Step 133.

\- **\*\*Creation purpose:\*\*** Five synthetic banking Q&A pairs created as a small development sample to test the JSON ingestion loader.

\- **\*\*External source / URL:\*\*** \`N/A — researcher reports it was not downloaded, scraped, or copied from a website\`.

\- **\*\*Original prompt:\*\*** Not available in the supplied history.

\- **\*\*PII / confidentiality:\*\*** Researcher reports no real customer names, phone numbers, account balances, or confidential financial records. A final inspection of the actual file is still required before signing the privacy declaration.

\- **\*\*Factuality warning:\*\*** Realistic examples may include inaccurate or outdated limits, procedures, SMS instructions, or liability timelines. Mark as synthetic/non-authoritative and do not present them as real bank policy without separate verification.

\- **\*\*Reuse terms:\*\*** No third-party source terms are identified based on the reported origin. This is not a blanket legal determination about AI-generated content.

\- **\*\*Status:\*\*** \`SYNTHETIC — RESEARCHER-REPORTED HISTORY; LABEL AND CONTENT REVIEW REQUIRED\`.



**### 2.2 \`data/documents/telecom_customer_support.csv\`**



\- **\*\*Internal ID:\*\*** \`DOC-CORPUS-07\`

\- **\*\*Source type:\*\*** AI-assistant-generated synthetic academic evaluation / ingestion-test data.

\- **\*\*Creation date:\*\*** 2026-09-09.

\- **\*\*Project phase:\*\*** Phase 2 — Domain Dataset and Document Processing.

\- **\*\*Reported generation step:\*\*** Step 135.

\- **\*\*Creation purpose:\*\*** Five synthetic telecom customer-support Q&A rows created as a small development sample to test the CSV ingestion loader.

\- **\*\*External source / URL:\*\*** \`N/A — researcher reports it was not downloaded, scraped, or copied from a website\`.

\- **\*\*Original prompt:\*\*** Not available in the supplied history.

\- **\*\*PII / confidentiality:\*\*** Researcher reports no real subscriber phone numbers, personal identifiers, or confidential subscriber records. A final inspection of the actual file is still required before signing the privacy declaration.

\- **\*\*Factuality warning:\*\*** Examples involving SMS short code \`199\`, plan rules, roaming, eSIM, data rollover, and 5G may be provider-specific or inaccurate. Mark as synthetic/non-authoritative and do not present as an actual operator's policy.

\- **\*\*Reuse terms:\*\*** No third-party source terms are identified based on the reported origin. This is not a blanket legal determination about AI-generated content.

\- **\*\*Status:\*\*** \`SYNTHETIC — RESEARCHER-REPORTED HISTORY; LABEL AND CONTENT REVIEW REQUIRED\`.



**### 2.3 \`data/documents/university_policies.txt\`**



\- **\*\*Internal ID:\*\*** \`DOC-CORPUS-08\`

\- **\*\*Source type:\*\*** AI-assistant-generated synthetic academic evaluation / ingestion-test data.

\- **\*\*Creation date:\*\*** 2026-09-09.

\- **\*\*Project phase:\*\*** Phase 2 — Domain Dataset and Document Processing.

\- **\*\*Reported generation step:\*\*** Step 131 at \`2026-09-09 13:29:46 UTC\`.

\- **\*\*Creation method:\*\*** The assistant reportedly wrote the file directly to \`data/documents/university_policies.txt\` using \`write_to_file\`.

\- **\*\*Creation purpose:\*\*** Sample TXT document to implement and validate the plain-text loader (\`TXTLoader\`).

\- **\*\*Content described in generation history:\*\*** Four fictional sections: admission and enrollment eligibility (including CGPA and IELTS/TOEFL examples); grading and academic standing; scholarship disbursement and renewal; examination conduct and integrity.

\- **\*\*External source / URL:\*\*** \`N/A — researcher reports it was not downloaded from a real university or external website\`.

\- **\*\*Original prompt:\*\*** Not available in the supplied history.

\- **\*\*Institution represented:\*\*** None established; treat policies as fictional, not the rules of a real university.

\- **\*\*PII / confidentiality:\*\*** Researcher reports no personal data or private records; final inspection is still required.

\- **\*\*Reuse terms:\*\*** No third-party source terms are identified based on the reported origin. This is not a blanket legal determination about AI-generated content.

\- **\*\*Status:\*\*** \`SYNTHETIC — RESEARCHER-REPORTED HISTORY; LABEL AND CONTENT REVIEW REQUIRED\`.



**### 2.4 \`data/documents/campus_library_guide.pdf\`**



\- **\*\*Internal ID:\*\*** \`DOC-CORPUS-02\`

\- **\*\*Source type:\*\*** AI-assistant-generated synthetic PDF ingestion-test fixture.

\- **\*\*Creation date:\*\*** 2026-09-09.

\- **\*\*Project phase:\*\*** Phase 2 — Domain Dataset and Document Processing.

\- **\*\*Reported generation steps:\*\*** Steps 137–139, around \`2026-09-09 13:29:59 UTC\`.

\- **\*\*Creation method:\*\*** The assistant reportedly wrote \`scripts/create_sample_pdf.py\`, which programmatically assembled a minimal valid PDF 1.4 stream, then ran the script to generate the 927-byte PDF.

\- **\*\*Creation purpose:\*\*** Controlled sample used to test PDF text extraction through the project's \`pypdf\`-based PDF loader.

\- **\*\*Content described in generation history:\*\*** “Campus Central Library Rules and Borrowing Guidelines”; a five-book borrowing limit, a 14-calendar-day loan period, INR 10 per book per day overdue fine, and restrictions on checking out reference materials, journals, and theses.

\- **\*\*External source / URL:\*\*** \`N/A — researcher reports it was not downloaded from a real university or external website\`.

\- **\*\*Institution represented:\*\*** No real institution established; treat the library and its rules as fictional.

\- **\*\*PII / confidentiality:\*\*** Researcher reports none; final inspection is still required.

\- **\*\*Reuse terms:\*\*** No third-party source terms are identified based on the reported origin. This is not a blanket legal determination about AI-generated content.

\- **\*\*Status:\*\*** \`SYNTHETIC — RESEARCHER-REPORTED HISTORY; LABEL AND CONTENT REVIEW REQUIRED\`.



**## 3. External institutional / banking documents**



**### 3.1 \`data/documents/code_of_ethics.txt\`**



\- **\*\*Document type:\*\*** Abridged text extract; local heading reportedly identifies “Code of Ethics Version 3.0”.

\- **\*\*Official source candidate:\*\*** State Bank of India (SBI), Code of Ethics 3.0 (Abridged), official PDF:  

  https\://sbi.bank.in/documents/17826/20624/251024-ABRIDGED%2BCODE%2BOF%2BETHICS%2BV-2.0.pdf/ab38b9e2-f39a-cd00-4550-569bf5c9f11c?t=1729847862207

\- **\*\*Verification date recorded for this form:\*\*** 2026-10-27 (source candidate identified; not the original download date).

\- **\*\*Original download/access date:\*\*** Unknown unless supported by a contemporaneous record.

\- **\*\*Local extract match:\*\*** Pending line-by-line or documented representative comparison; the local file is not the complete PDF.

\- **\*\*Reuse / redistribution:\*\*** Not established. Review the source site's terms and any applicable permissions before redistributing copied text.

\- **\*\*Status:\*\*** \`OFFICIAL SOURCE CANDIDATE — LOCAL EXTRACT MATCH AND REUSE TERMS PENDING\`.



**### 3.2 \`data/documents/digital_and_transaction_banking_products.txt\`**



\- **\*\*Document type:\*\*** Text extract of a Digital & Transaction Banking Products booklet.

\- **\*\*Official source candidate:\*\*** SBI-hosted PDF:  

  https\://sbi.bank.in/documents/26274/26996/03022022_DTB%2BPRODUCTS%2BBOOKLET.pdf/2d562a0a-5641-7fab-4181-44879b8a6070?t=1643871923575

\- **\*\*Verification date recorded for this form:\*\*** 2026-10-27 (source candidate identified; not the original download date).

\- **\*\*Original download/access date:\*\*** Unknown unless supported by a contemporaneous record.

\- **\*\*Local extract match:\*\*** Pending comparison against the exact official PDF version.

\- **\*\*Reuse / redistribution:\*\*** Not established; public availability alone does not establish permission to redistribute.

\- **\*\*Status:\*\*** \`OFFICIAL SOURCE CANDIDATE — LOCAL MATCH AND REUSE TERMS PENDING\`.



**### 3.3 \`data/documents/ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf\`**



\- **\*\*Document title:\*\*** Impact Reporting of Green Bond of USD 250 Million.

\- **\*\*Official SBI Investor Relations page:\*\***  

  https\://sbi.bank.in/web/investor-relations/impact-analysis-and-post-issuance-assurance-of-green-bond

\- **\*\*Direct official PDF candidate:\*\***  

  https\://sbi.bank.in/documents/17836/53469043/Impact%2BReporting%2Bof%2BGreen%2BBond%2Bof%2BUSD%2B250%2BMillion.pdf/aab70f17-604e-98e7-0bc1-8d2b80987ab4?t=1751707146983

\- **\*\*Verification date recorded for this form:\*\*** 2026-10-27 (official listing/source candidate; not original download date).

\- **\*\*Original download/access date:\*\*** Unknown unless supported by a contemporaneous record.

\- **\*\*Local PDF match:\*\*** Compare the local PDF to the linked official PDF (page count/content and preferably file hash) before freeze.

\- **\*\*Reuse / redistribution:\*\*** Review report notices and applicable source terms; public availability does not automatically grant redistribution rights.

\- **\*\*Status:\*\*** \`OFFICIAL SOURCE CANDIDATE — EXACT LOCAL FILE MATCH AND REUSE TERMS TO CONFIRM\`.



**### 3.4 \`data/documents/microfinance_loans_policy.txt\`**



\- **\*\*Document type:\*\*** Partial text extract of SBI's microfinance loans policy.

\- **\*\*Official source:\*\*** SBI PDF:  

  https\://sbi.bank.in/documents/14463/22577/20012023_Mircorfinance%20Loan%20Policy%20for%20Publication.pdf

\- **\*\*Version described in existing project records:\*\*** Version 1.0; instructions through 18 October 2022 incorporated.

\- **\*\*Existing project record's verification date:\*\*** 2026-10-26. Retain this as a recorded project value, but the researcher should confirm its accuracy.

\- **\*\*Original download/access date:\*\*** Do not infer this from the verification date; unknown unless separately recorded.

\- **\*\*Local extract coverage:\*\*** Existing project documentation describes it as covering Sections 1 through 6.3 and omitting later sections/annexures. Call it a partial extract, not the full policy.

\- **\*\*Reuse / redistribution:\*\*** Not established; review applicable source terms.

\- **\*\*Status:\*\*** \`OFFICIAL SOURCE RECORDED; PARTIAL-EXTRACT LABEL REQUIRED; REUSE TERMS TO REVIEW\`.



**## 4. Query benchmark**



**### \`data/queries/sample_queries.json\`**



\- **\*\*Existing project description:\*\*** 50 base information needs, each represented in English, Tanglish, and Hinglish, for 150 query variants total.

\- **\*\*Expected document mapping:\*\*** Project documentation says \`expected_document_ids\` map queries to corpus evidence; actual IDs and counts must be checked against the current files/index.

\- **\*\*Creation history:\*\*** Original authorship/source history not independently established by this form.

\- **\*\*External URLs:\*\*** Not applicable if all queries are original; if any were adapted from external material, record those sources.

\- **\*\*Privacy:\*\*** Must be inspected before the researcher signs the certification.

\- **\*\*Required checks:\*\*** Confirm actual counts, one-to-one language variants, duplicate/near-duplicate questions, valid document IDs, retrieval/index alignment, and no confidential data.

\- **\*\*Status:\*\*** \`DOCUMENTATION CLAIM RECORDED — CURRENT FILE VALIDATION AND PRIVACY REVIEW PENDING\`.



**## 5. Consolidated corpus status**



\| File | Current provenance status | Remaining action |

\|---|---|---|

\| \`banking_faq.json\` | Synthetic origin reported by researcher | Mark synthetic/non-authoritative; inspect content and privacy |

\| \`campus_library_guide.pdf\` | Synthetic origin reported by researcher | Mark fictional/non-authoritative; preserve generation script/history if available |

\| \`code_of_ethics.txt\` | Official source candidate | Compare local extract to exact source; review reuse terms |

\| \`digital_and_transaction_banking_products.txt\` | Official source candidate | Compare local extract to exact source; review reuse terms |

\| Green Bond PDF | Official source candidate | Compare local PDF to official PDF; review reuse terms |

\| \`microfinance_loans_policy.txt\` | Official source recorded in project | Preserve partial-extract description; review reuse terms |

\| \`telecom_customer_support.csv\` | Synthetic origin reported by researcher | Mark synthetic/non-authoritative; inspect content and privacy |

\| \`university_policies.txt\` | Synthetic origin reported by researcher | Mark fictional/non-authoritative; inspect content and privacy |



**\*\*Release decision:\**** \`FROZEN — RESEARCHER-DECLARED WITH OPEN LIMITATIONS\`. The researcher has chosen to freeze the current corpus snapshot on 2026-10-27. This is an administrative freeze decision, not independent validation of every provenance claim. The generation history does not independently authenticate the historical session. SBI local-file matching and reuse review, benchmark validation, and final corpus/privacy inspection remain recorded as outstanding. Preserve this snapshot unchanged; do not launch the planned 300 production runs or redistribute external-source extracts until the mandatory checks and project preflight pass.



**## 6. Researcher certification and sign-off**



These are personal declarations and must be checked only by the researcher after completing the stated review.



\- [done] **\*\*Researcher to confirm:\*\*** I inspected all files in \`data/documents/\` and \`data/queries/sample_queries.json\` for confidential financial records, personal customer/subscriber data, passwords, employee evaluations, and private communications.

\- [done] **\*\*Researcher to confirm:\*\*** I reviewed the source and version of each external document and checked applicable access, attribution, and reuse terms.

\- [done] **\*\*Researcher to confirm:\*\*** I have resolved or explicitly documented all remaining provenance and content-quality blockers.

\- [done] **\*\*Researcher to confirm:\*\*** I approve freezing the corpus under the project's stated protocol.



\- **\*\*Researcher name:\*\*** \`NIRANJNA KARTHIKEYAN MOUMIN ZAARA ANIRUDH VIJAYAN\`

\- **\*\*Affiliation / institution:\*\*** \`VIT CHENNAI\`

\- **\*\*Date signed (YYYY-MM-DD):\*\*** \`2026-10-27\`

\- **\*\*Corpus freeze approval:\*\*** [x] \`APPROVED TO FREEZE — RESEARCHER-DECLARED; LIMITATIONS ABOVE APPLY\`



**## 7. Final actions before corpus freeze**



1\. Keep the four pilot fixtures clearly labelled as synthetic development/test fixtures, not authoritative real-world policy documents.

2\. Inspect their actual contents for privacy issues and potentially misleading factual claims; retain the supplied generation-history record with the project.

3\. Compare the local SBI extracts/PDF against the exact official versions and document the result.

4\. Review applicable reuse/redistribution conditions for the external SBI documents.

5\. Validate the actual query count, language variants, expected document IDs, and index/ground-truth consistency.

6\. Update the corpus manifest, this form, and the release decision so all statuses agree.

7\. Complete the personal declarations, name, affiliation, and actual signing date only after performing the review.

8\. Run the project's preflight and tests; do not start the production experiment until all mandatory release gates pass.



**\*\*Prepared status:\*\*** This form incorporates the provenance details and researcher sign-off information supplied in the conversation. The freeze approval is recorded as researcher-declared. Open source-matching, reuse, benchmark-validation, and privacy-review limitations remain visible; this document does not represent independent verification of those checks.
