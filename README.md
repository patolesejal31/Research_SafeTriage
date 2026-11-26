# SafeTriage

**A Safety-Constrained Hybrid NLP and Deterministic Triage Stratification Engine for Non-Diagnostic Emergency Routing**

> **ACADEMIC RESEARCH PROTOTYPE DISCLAIMER**
>
> SafeTriage is an MCA dissertation research software prototype designed to evaluate the safety, latency, and triage behavior of hybrid architectures (Deterministic Rules + Statistical ML + Mock/Bounded LLMs).
>
> **NON-DIAGNOSTIC & NON-PRESCRIPTIVE:**
> - SafeTriage is **NOT** a medical diagnostic tool and **CANNOT** prescribe medications, dosages, or definitive clinical treatments.
> - The clinical rules encoded herein are derived from open public literature (e.g., NICE, IAP, AHA) and are strictly marked **`UNVERIFIED`** (`verified=false`). They have **NOT** been evaluated, approved, or validated by a licensed physician or clinical board.
> - In any actual medical emergency, users must immediately contact emergency dispatch (**112** or **108** in India, or local emergency services).

---

## 1. System Architecture & Two-Stage Safety Pipeline

SafeTriage operates on a **two-stage pipeline** designed around a core safety invariant: **Triage urgency may only escalate, never downgrade.**

```
User Input (Text + Age + Modifiers)
             │
             ▼
    ┌─────────────────┐
    │  Sanitization   │  (Prompt injection screening, length constraints)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  NLP Extraction │  (Negation detection, exact/fuzzy/variant entity linking)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │   Safety Net    │  (Universal red-flag override: unresponsiveness, anaphylaxis)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Stage A: Rule   │  (Deterministic rules 1–31 across 10 specialties)
    │ Engine Check    │
    └────────┬────────┘
             │
      Is Level 1? ─────────► [IMMEDIATE EMERGENCY ALERT (Level 1)]
             │               (Dispatched immediately; bypasses all follow-ups)
             ▼ No
    ┌───────────────────────────────────────────────┐
    │ Stage B: Asynchronous Escalation              │
    │  ├─ Safety-Critical Follow-ups (Age, Red Flags)│
    │  ├─ Optional Follow-ups (Capped at 3)         │
    │  ├─ Statistical ML Stratifier (TF-IDF + LR)   │
    │  ├─ Bounded LLM Reasoning (MOCK / Schema)     │
    │  └─ Explainer & Faithfulness Check            │
    └───────────────────────┬───────────────────────┘
                            │
                            ▼
      Final Urgency Stratification (Levels 1–4 or UNCERTAIN)
      [URGENCY INVARIANT ENFORCED: min(Stage_A, Stage_B)]
```

### Urgency Levels
- **Level 1 (Emergency):** Immediate resuscitation / emergency dispatch (`tel:112`, `tel:108`).
- **Level 2 (Urgent):** In-person emergency or urgent clinical assessment required within hours.
- **Level 3 (Routine):** Standard outpatient consultation or scheduled primary care.
- **Level 4 (Self-Care):** Mild, self-limiting condition suitable for standard supportive home care.
- **UNCERTAIN:** Fallback safety state when deterministic rules cannot rule out emergent risk or if pipeline components produce contradictory confidence. **Never styled or handled as routine self-care.**

---

## 2. Component Implementation & Validation Status

| Subsystem / Feature | Implementation Status | Clinical / Verification Status | Notes |
|---|---|---|---|
| **Deterministic Rule Engine (31 rules)** | **Implemented** | `UNVERIFIED` (`verified=false`) | Synthesized from clinical guidelines (NICE, IAP, AHA) by engineering staff; awaiting formal clinician panel review. |
| **Two-Stage Urgency Invariant** | **Implemented & Formally Tested** | Software Verified | Mathematical guarantee: `Final = min(Rule, SafetyNet, ML, LLM)`. Never downgrades. |
| **NLP Entity Extractor** | **Implemented** | Heuristic / Lexicon Based | Handles negation, colloquialisms, Hinglish transliterations, and severity modifiers. |
| **Statistical ML Stratifier** | **Implemented** | Synthetic-Dev Trained | TF-IDF + Logistic Regression trained strictly on `train.json` (`tier=synthetic_dev`). |
| **LLM Reasoning Adapter** | **Implemented (`MockProvider`)** | `MOCK (not a real LLM)` | Deterministic mock adapter for reproducible academic testing. Strict JSON schema; cannot downgrade. |
| **Real Provider Adapters (OpenAI/Gemini)** | **Implemented (Code only)** | **BLOCKED** | Live API integration is disabled in CI/evaluation tests to prevent unverified clinical risk & non-determinism. |
| **Hypothesis H1 (Hybrid > Rules)** | **Evaluated on Synthetic Split** | **BLOCKED for Clinical Claim** | Rule-only achieved 0.985 F1 due to same-author circularity. |
| **Hypothesis H3 (LLM Escalation Utility)** | **Simulated / Mocked** | **BLOCKED** | Real LLM evaluation blocked pending production keys & clinical governance. |
| **Hypothesis H4 (Clinician Agreement)** | **Protocol Defined** | **BLOCKED** | Clinician review form and dataset sampling ready; clinician review panel not yet convened. |
| **Anonymous Assessment Retention** | **Implemented** | Operational | Automatic 24-hour TTL purge background task (`GUEST_RETENTION_HOURS=24`). |
| **Next.js 14 Web Frontend** | **Implemented** | WCAG 2.1 AA Screened | Top banner 112/108 on every page, immediate Level 1 modal, privacy opt-in, researcher dashboard. |

---

## 3. Honest Limitations & Academic Disclosures

1. **Same-Author Circularity:** The synthetic vignettes (`tier=synthetic_dev`) and deterministic rules were created by the same research group. High performance on `test.json` (e.g., Rule-Only Macro F1 = 0.985) is an artifact of evaluation design, **not clinical efficacy**.
2. **Synthetic Data Only:** No real patient health records or electronic health records (EHR) were used in evaluation.
3. **No Direct Clinician Validation:** Neither the rule set nor the model outputs have been certified by practicing physicians.
4. **Mock LLM:** The LLM evaluation was executed using `MockProvider`. Real-world prompt drift, latency jitter, and hallucinations in frontier models were simulated via adversarial test fixtures only.

---

## 4. Getting Started & Reproduction

### Prerequisites
- Python 3.11+
- Node.js 18+ (tested on Node v20/v22) and npm
- Git

### Linux / macOS Setup

```bash
# 1. Clone repository
git clone https://github.com/example/safetriage.git
cd safetriage

# 2. Python environment & dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Frontend environment
cd frontend
npm ci
cd ..

# 4. Verify test split integrity
python3 -c "import hashlib; h = hashlib.sha256(open('datasets/synthetic/splits/test.json','rb').read()).hexdigest(); assert h == '5c95af7961422cb37e44525f4ec9401401eb00fff7a7db0a71278c98acd79475', f'Mismatch: {h}'"

# 5. Run backend test suite (unit, safety invariants, API, metrics)
pytest --cov=backend/app --cov-report=term-missing

# 6. Run frontend tests (WCAG axe-core & component safety checks)
cd frontend
npm test
npm run build
cd ..

# 7. Start development servers
# Terminal 1 (Backend):
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
# Terminal 2 (Frontend):
cd frontend && npm run dev
```

### Windows (PowerShell) Setup

```powershell
# 1. Clone repository & enter folder
git clone https://github.com/example/safetriage.git
cd safetriage

# 2. Virtual environment & dependencies
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Frontend environment
cd frontend
npm ci
cd ..

# 4. Verify test split checksum
python -c "import hashlib; h = hashlib.sha256(open('datasets/synthetic/splits/test.json','rb').read()).hexdigest(); assert h == '5c95af7961422cb37e44525f4ec9401401eb00fff7a7db0a71278c98acd79475', f'Checksum error: {h}'; print('Checksum verified!')"

# 5. Run test suites
pytest
cd frontend
npm test
npm run build
cd ..
```

---

## 5. Security & Privacy Defaults

- **Raw Symptom Text:** Never stored unless user explicitly toggles the opt-in checkbox (default: `False`).
- **Guest Retention:** Guest assessments are deleted automatically after 24 hours.
- **Passwords:** Hashed with Argon2id; passwords and JWT tokens are rejected from application logs.
- **Local Storage:** No symptom text or assessment outcomes are persisted in browser `localStorage`.
- **JWT Production Guard:** System halts on startup if `JWT_SECRET` is left as default when `ENVIRONMENT=production`.

---

## 6. License & Citation

This project is licensed for academic research purposes under the MIT License. See [LICENSE](LICENSE) for details.
