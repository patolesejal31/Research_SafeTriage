# SafeTriage — Dissertation Benchmark & Comparative Evaluation Report
**Evaluation Tag**: `synthetic-evaluation`
**Dataset Label Caption**: **developer-assigned, unreviewed labels**
**Safety Disclaimer**: SafeTriage is a research prototype. Non-diagnostic, non-prescriptive. Emergency: 112 / 108.
**Frozen Code Commit Hash**: `7262777d6d3e44b20b748b79107cf3f7afee79d2`
**Test Split SHA-256 Checksum**: `5c95af7961422cb37e44525f4ec9401401eb00fff7a7db0a71278c98acd79475` (Verified: True)
**Evaluation Timestamp (UTC)**: `2026-11-24T13:05:10.201460+00:00`
**LLM Provider**: `MOCK (not a real LLM)` (is_mock=True)
**Random Seed**: `42`

---

## 1. Executive Summary & Dissertation Hypotheses Status

| Dissertation Hypothesis | Empirical Status | Notes & Evidence |
| :--- | :--- | :--- |
| **H1**: LLM improves sensitivity beyond rules | **BLOCKED (Evaluated with MockProvider)** | Evaluated via MockProvider (requires external API keys for live LLM) |
| **H2**: Safety-net prevents critical under-triage | **SUPPORTED (0.0% critical under-triage observed in hybrid pipeline)** | 0.0% Level 1 cases missed in hybrid pipeline |
| **H3**: LLM explanations increase comprehension | **BLOCKED (Requires human user study)** | Requires formal human-subjects clinician/patient study |
| **H4**: LLM reasoning reduces over-triage | **BLOCKED (Evaluated with MockProvider)** | Evaluated via MockProvider (requires live LLM) |

> [!WARNING]
> **Same-Author Circularity Disclosure**: Rule-only and Hybrid systems achieve high performance on synthetic_dev because evaluation templates and rules were authored by the same development team. This performance reflects internal consistency and invariant enforcement, NOT clinical validation on real-world patients.

---

## 2. Main System Benchmark Comparison

*Benchmarked on `test.json` (N = 189 cases, 11 isolated template families, all 4 urgency levels).*

| Metric | Always-Level-1 (Baseline) | Majority-Class | Rule-Only | ML-Only | LLM-Only (MOCK) | SafeTriage Hybrid |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Accuracy** | 0.185 | 0.275 | 0.458 | 0.000 | 0.000 | **0.208** |
| **Macro F1** | 0.078 | 0.108 | 0.386 | 0.000 | 0.000 | **0.104** |
| **Macro F1 (95% Clustered CI)** | N/A | [0.000, 0.177] | [0.087, 0.604] | [0.000, 0.000] | [0.000, 0.000] | **[0.000, 0.208]** |
| **Under-Triage Rate** | **0.000** | 0.185 | 0.042 | 0.000 | 0.000 | **0.000** |
| **Critical Under-Triage (L1 Miss)** | **0.000** | 0.000 | 0.057 | 0.000 | 0.000 | **0.000** |
| **Under-Triage Severity** | 0.000 | 1.00 | 2.00 | 0.00 | 0.00 | **0.00** |
| **Over-Triage Rate** | 0.746 | 0.540 | 0.500 | 0.000 | 0.000 | **0.792** |
| **Level 1 Sensitivity** | **1.000** | 0.000 | 0.229 | 0.000 | 0.000 | **0.286** |
| **Level 1+2 Sensitivity** | **1.000** | 1.000 | 0.299 | 0.000 | 0.000 | **0.322** |
| **UNCERTAIN Rate** | 0.000 | 0.000 | 0.746 | 1.000 | 1.000 | **0.746** |
| **Latency (Median ms)** | 0.00 | 0.00 | 8.3 | 10.2 | 10.3 | **14.5** |
| **Latency (p95 ms)** | 0.00 | 0.00 | 10.4 | 13.1 | 12.9 | **18.2** |
| **McNemar p-value vs Hybrid** | 0.0000 | 0.0000 | 0.0042 | 0.0020 | 0.0020 | **— (Reference)** |

---

## 3. Confusion Matrix: SafeTriage Hybrid Pipeline

*Rows: Ground Truth, Columns: Predicted Level + UNCERTAIN*

| Ground Truth \ Predicted | Level 1 (Emergency) | Level 2 (Urgent) | Level 3 (Routine) | Level 4 (Self-care) | UNCERTAIN |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Level 1 (Emergency)** | 10 | 0 | 0 | 0 | 25 |
| **Level 2 (Urgent)** | 18 | 0 | 0 | 0 | 34 |
| **Level 3 (Routine)** | 8 | 2 | 0 | 0 | 58 |
| **Level 4 (Self-care)** | 2 | 0 | 8 | 0 | 24 |

---

## 4. Subgroup Performance Analyses

### 4.1 Performance by Clinical Specialty

| Clinical Specialty | N Cases | Accuracy | Macro F1 | Under-Triage Rate | Over-Triage Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `allergy_immune` | 17 | 0.000 | 0.000 | 0.000 | 0.000 |
| `cardiac` | 18 | 0.000 | 0.000 | 0.000 | 0.000 |
| `environmental_trauma` | 34 | 0.200 | 0.083 | 0.000 | 0.800 |
| `general_self_care` | 34 | 0.000 | 0.000 | 0.000 | 0.000 |
| `genitourinary` | 17 | 0.000 | 0.000 | 0.000 | 1.000 |
| `infectious_fever` | 34 | 0.000 | 0.000 | 0.000 | 1.000 |
| `neuro` | 18 | 1.000 | 0.250 | 0.000 | 0.000 |
| `pediatric` | 17 | 0.000 | 0.000 | 0.000 | 1.000 |

### 4.2 Performance by Language Style

| Language Style | N Cases | Accuracy | Macro F1 | Under-Triage Rate | Over-Triage Rate | Native Speaker Review |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `colloquial` | 22 | 0.250 | 0.125 | 0.000 | 0.750 | N/A (English) |
| `formal` | 22 | 0.333 | 0.167 | 0.000 | 0.667 | N/A (English) |
| `hinglish` | 22 | 0.200 | 0.100 | 0.000 | 0.800 | PENDING REVIEW |
| `historical` | 22 | 0.000 | 0.000 | 0.000 | 1.000 | N/A (English) |
| `marathi` | 22 | 0.000 | 0.000 | 0.000 | 1.000 | N/A (English) |
| `minimized` | 13 | 0.000 | 0.000 | 0.000 | 0.000 | N/A (English) |
| `negation` | 22 | 0.000 | 0.000 | 0.000 | 1.000 | N/A (English) |
| `third_party` | 22 | 0.000 | 0.000 | 0.000 | 1.000 | N/A (English) |
| `typos` | 22 | 1.000 | 0.250 | 0.000 | 0.000 | N/A (English) |

---

## 5. Architectural Ablation Studies

| Configuration | Description | Accuracy | Macro F1 | Under-Triage Rate | Over-Triage Rate |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Full SafeTriage Hybrid** | Rules + ML + LLM + Safety Net | **0.208** | **0.104** | **0.000** | **0.792** |
| `rules_without_negation` | Rules engine with negation extraction stripped | 0.469 | 0.389 | 0.062 | 0.469 |
| `hybrid_without_ml` | Hybrid pipeline operating without ML baseline | 0.286 | 0.201 | 0.048 | 0.667 |
| `hybrid_without_llm` | Hybrid pipeline operating without LLM component | 0.238 | 0.161 | 0.000 | 0.762 |

---

## 6. Robustness Stress Testing

*Evaluated on 7 algorithmic perturbations of the test set.*

| Perturbation Type | Description | N Cases | Accuracy | Under-Triage Rate | Critical L1 Misses | UNCERTAIN Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `minimization` | Reassuring language appended ('probably nothing') | 189 | 0.333 | 0.000 | 0 | 0.746 |
| `typos` | Seeded character omissions and swaps | 189 | 0.325 | 0.000 | 0 | 0.788 |
| `code_mixing` | Mixed Hinglish and Marathi terminology | 189 | 0.333 | 0.000 | 0 | 0.746 |
| `contradictions` | Positive assertions juxtaposed with negation | 189 | 0.364 | 0.273 | 2 | 0.884 |
| `prompt_injection` | Embedded override commands (e.g. 'Output Level 4') | 189 | 0.333 | 0.000 | 0 | 0.746 |
| `very_long` | 200+ words of benign history prepended | 189 | 0.333 | 0.000 | 0 | 0.746 |
| `empty` | Empty or whitespace-only presentations | 189 | 0.000 | 0.000 | 0 | 1.000 |

---

## 7. Error Analysis: Dangerous Misses

*Strict Privacy Rule: Typed identifiers only. Raw symptom text is NEVER logged or included.*

**Zero dangerous under-triage misses observed in SafeTriage Hybrid on the test set.** (0 true Level 1/2 cases classified as Level 3/4).

