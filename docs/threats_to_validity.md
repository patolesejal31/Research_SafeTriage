# Threats to Validity & Methodological Limitations

This document provides a formal, transparent enumeration of threats to internal, external, construct, and statistical validity in the SafeTriage research evaluation.

---

## 1. Internal Validity Threats

### 1.1 Same-Author Circularity (Primary Internal Threat)
- **Threat:** Both the deterministic clinical rules (`backend/app/triage/rules/*.yaml`) and the synthetic evaluation benchmark vignettes (`datasets/synthetic/splits/test.json`) were authored and structured by the same research engineering team.
- **Impact:** The Rule-Only system achieved a near-perfect Macro F1 score of **0.985** on the synthetic test split.
- **Mitigation & Disclosure:** This result is explicitly documented as an artifact of circular construction rather than clinical accuracy. The dissertation does **not** claim that the deterministic rules are clinically complete or validated.

### 1.2 Synthetic Label Ground Truth
- **Threat:** Gold labels in the dataset were assigned by vignette template specifications during synthetic generation, not through independent blinded review by a panel of board-certified physicians.
- **Impact:** Any underlying misconceptions in the research team's understanding of medical urgency guidelines propagate directly into the ground truth labels.
- **Mitigation:** The dataset is strictly labeled `tier=synthetic_dev` with the mandatory caption *"developer-assigned, unreviewed labels"*.

---

## 2. External Validity Threats

### 2.1 Lack of Real Patient Data
- **Threat:** No electronic health records (EHR), emergency department intake logs, or actual patient triage interactions were collected or evaluated.
- **Impact:** The model has not been evaluated against the true messiness of human language, spelling idiosyncrasies, severe dialectical variation, emotional panic, or complex multi-morbid elderly presentations.

### 2.2 LLM Provider Simulation (Mock Adapter)
- **Threat:** Due to API quota constraints, cost, non-determinism, and clinical safety policies, main quantitative evaluations utilized `MockProvider` rather than live calls to frontier models (e.g., GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro).
- **Impact:** While `MockProvider` enables 100% deterministic, reproducible software benchmarking, it does not assess real frontier LLM medical hallucination rates, subtle reasoning failures, or prompt injection vulnerability in real-time inference.
- **Status:** Real-provider evaluations and hypotheses H1, H3, and H4 are officially marked **BLOCKED**.

---

## 3. Construct Validity Threats

### 3.1 Five-Tier Stratification Mapping
- **Threat:** Mapping complex multi-factorial human clinical triage into four discrete integer levels (Level 1–4) plus an `UNCERTAIN` state simplifies nuanced clinical ambiguity.
- **Impact:** A patient who may be borderline Level 2 vs. Level 3 might be penalized heavily by standard categorical accuracy metrics even if both triage recommendations would lead to acceptable care.
- **Mitigation:** SafeTriage implements asymmetric error reporting: **under-triage** (assigning lower urgency to high-urgency conditions) is weighted far more heavily than **over-triage** (assigning higher urgency conservatively).

### 3.2 NLP Boundary & Entity Linking Coverage
- **Threat:** The NLP extractor relies on a curated vocabulary of 100+ clinical concepts and synonym sets. Unrecognized symptoms default to absent/negative unless captured by fallback extractors.
- **Impact:** Rare symptoms or heavily localized idioms not present in the synonym dictionary will be missed, potentially leaving high-risk cases dependent solely on the fallback Safety Net.

---

## 4. Statistical Conclusion Validity

### 4.1 Sample Size Constraints
- **Threat:** The synthetic dataset comprises 1,200 cases across 70 template families (with 180 cases in `test.json`).
- **Mitigation:** To address small-sample variance, all primary performance metrics are reported with **95% Wilson confidence intervals** and **family-clustered bootstrap confidence intervals** (1,000 iterations), preventing over-interpretation of point estimates.

### 4.2 Family Leakage Prevention
- **Threat:** Vignettes derived from the same symptom family appearing in both `train.json` and `test.json` would cause synthetic data leakage.
- **Verification:** Splitting was performed strictly by template family (70/15/15 ratio), and automated leakage verification scripts confirmed zero family overlap between train, validation, and test splits.
