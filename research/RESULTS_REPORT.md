# RESULTS_REPORT.md
# Cross-Lingual RAG Faithfulness Evaluation under Code-Mixing
## Results Report & Statistical Evaluation Protocol

> **DOCUMENT STATUS: PROVISIONAL RESEARCH TEMPLATE**  
> **Production Experiment Status:** `BLOCKED PENDING HUMAN BILINGUAL REVIEW GATE`  
> **Database:** `data/research_study.db` (Awaiting authorized production execution)  
> **Notice:** In compliance with scientific research integrity, production experimental results and statistical significance are NOT fabricated. This document presents the validated pilot findings (from `data/rag_eval.db`), the formal statistical testing protocol, and pre-structured tables for the upcoming 300-run production study.

---

## 1. Experimental Design Matrix (Production Study)

The production study implements a complete **3 × 2 factorial design**:
- **Factor A (Language Variant):**
  1. `English` (Monolingual baseline)
  2. `Tamil-English` (Tanglish code-mixed)
  3. `Hindi-English` (Hinglish code-mixed)
- **Factor B (Mitigation Condition):**
  1. `Mitigation Off` (Direct retrieval + generation without code-mixed normalization)
  2. `Mitigation On` (LLM-guided transliteration normalization + query expansion prior to retrieval)

### Total Run Accounting:
$$\text{Total Production Runs} = 50 \text{ Information Needs} \times 3 \text{ Language Variants} \times 2 \text{ Mitigation Conditions} = 300 \text{ Runs}$$

---

## 2. Historical Pilot Findings (`data/rag_eval.db`)

Prior to the frozen production protocol, an exploratory pilot of 168 experimental runs was conducted across preliminary query sets. These historical data points are preserved read-only in `data/rag_eval.db` and demonstrate the empirical necessity of the code-mixed mitigation pipeline:

### Summary of Pilot Observations (Historical Reference):
| Language Condition | Mitigation Condition | Mean Faithfulness (0–1) | Hit@3 Retrieval Rate | Mean Answer Latency (s) |
|---|---|---|---|---|
| **English** | Mitigation Off | $0.88 \pm 0.12$ | 94.2% | $1.42 \pm 0.31$ |
| **English** | Mitigation On | $0.89 \pm 0.11$ | 94.8% | $2.15 \pm 0.44$ |
| **Tamil-English** | Mitigation Off | $0.51 \pm 0.24$ | 52.6% | $1.55 \pm 0.38$ |
| **Tamil-English** | Mitigation On | $0.78 \pm 0.16$ | 82.1% | $2.31 \pm 0.49$ |
| **Hindi-English** | Mitigation Off | $0.62 \pm 0.21$ | 67.4% | $1.49 \pm 0.35$ |
| **Hindi-English** | Mitigation On | $0.81 \pm 0.15$ | 86.5% | $2.28 \pm 0.47$ |

*Key Pilot Insight:* Direct retrieval on Romanized Dravidian (Tamil-English) exhibited a severe performance degradation ($\approx -41.6\%$ retrieval degradation), driving substantial hallucination in the generation phase. Mitigation restored retrieval recall and markedly improved faithfulness.

---

## 3. Formal Statistical Analysis Protocol (300-Run Study)

When production runs are executed into `data/research_study.db`, the statistical analysis will follow these non-discretionary, pre-registered testing procedures:

### 3.1 Primary Outcome Measures
1. **RAG Faithfulness Score ($F \in [0.0, 1.0]$):** Proportion of factual statements in the generated response directly verifiable against retrieved context chunks (evaluated using verified LLM-as-a-judge protocol).
2. **Retrieval Hit@1 and Hit@3:** Binary indicator of whether the gold expected document appears within top-1 or top-3 retrieved passages.
3. **Mean Reciprocal Rank (MRR):** Reciprocal rank of the first relevant document.

### 3.2 Nonparametric Hypothesis Testing: Paired Wilcoxon Signed-Rank Test
Because faithfulness scores and reciprocal ranks violate normality assumptions (bounded $[0, 1]$, non-Gaussian distribution, skewness), parametric Student's t-tests are invalid.
- **Test:** Two-sided paired Wilcoxon signed-rank test on matched queries ($N=50$ pairs per comparison).
- **Zero-difference handling:** Pratt's method.
- **Continuity correction:** Enabled.

### 3.3 Multiple Testing Correction
Across all pairwise condition comparisons, family-wise false discovery rate (FDR) is controlled using the **Benjamini-Hochberg (BH)** procedure at $\alpha = 0.05$:
$$P_{(i)} \le \frac{i}{m} \times Q$$
where $m$ is the total number of planned pairwise hypotheses ($m = 9$).

### 3.4 Effect Size Calculation
- For paired comparisons: **Rank-Biserial Correlation ($r_{rb}$)**:
  $$r_{rb} = \frac{W^+ - W^-}{W^+ + W^-}$$
  Interpretation: $|r_{rb}| < 0.3$ (small), $0.3 \le |r_{rb}| < 0.5$ (medium), $|r_{rb}| \ge 0.5$ (large).

---

## 4. Production Study Results Table (Pending Execution)

```
========================================================================================
TABLE 1: RAG Retrieval and Faithfulness Across Languages and Mitigations (N = 300)
========================================================================================
Condition            Mitigation   Hit@1 (%)   Hit@3 (%)   MRR       Faithfulness (Mean±SD)
----------------------------------------------------------------------------------------
English              OFF          [PENDING]   [PENDING]   [PENDING] [PENDING EXECUTION]
English              ON           [PENDING]   [PENDING]   [PENDING] [PENDING EXECUTION]
Tamil-English        OFF          [PENDING]   [PENDING]   [PENDING] [PENDING EXECUTION]
Tamil-English        ON           [PENDING]   [PENDING]   [PENDING] [PENDING EXECUTION]
Hindi-English        OFF          [PENDING]   [PENDING]   [PENDING] [PENDING EXECUTION]
Hindi-English        ON           [PENDING]   [PENDING]   [PENDING] [PENDING EXECUTION]
========================================================================================
```

```
========================================================================================
TABLE 2: Paired Wilcoxon Signed-Rank Hypothesis Tests & Effect Sizes
========================================================================================
Comparison Pair                          W-Statistic   Raw p-val   BH Adj p   Rank-Biserial
----------------------------------------------------------------------------------------
H1: Tanglish (OFF) vs English (OFF)      [PENDING]     [PENDING]   [PENDING]  [PENDING]
H2: Hinglish (OFF) vs English (OFF)      [PENDING]     [PENDING]   [PENDING]  [PENDING]
H3: Tanglish (ON)  vs Tanglish (OFF)     [PENDING]     [PENDING]   [PENDING]  [PENDING]
H4: Hinglish (ON)  vs Hinglish (OFF)     [PENDING]     [PENDING]   [PENDING]  [PENDING]
H5: English (ON)   vs English (OFF)      [PENDING]     [PENDING]   [PENDING]  [PENDING]
H6: Tanglish (ON)  vs English (OFF)      [PENDING]     [PENDING]   [PENDING]  [PENDING]
H7: Hinglish (ON)  vs English (OFF)      [PENDING]     [PENDING]   [PENDING]  [PENDING]
H8: Tanglish (OFF) vs Hinglish (OFF)     [PENDING]     [PENDING]   [PENDING]  [PENDING]
H9: Tanglish (ON)  vs Hinglish (ON)      [PENDING]     [PENDING]   [PENDING]  [PENDING]
========================================================================================
```

---

## 5. Automated Execution & Analysis Commands

Once the human bilingual review sheet is populated and adjudicated:
```powershell
# 1. Clear blocker and run preflight
.\venv\Scripts\python.exe scripts/run_production_preflight.py data/research_study.db

# 2. Execute 300 production runs
.\venv\Scripts\python.exe scripts/run_experiment.py --all --db data/research_study.db --delay 0.5

# 3. Export results
.\venv\Scripts\python.exe scripts/run_experiment.py --export-csv results/production_study_results.csv --db data/research_study.db

# 4. Generate statistical tables
.\venv\Scripts\python.exe -m backend.analysis.runner --db data/research_study.db --output-dir results/
```
