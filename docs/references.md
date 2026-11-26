# Clinical Literature References & Guideline Sources

> **DISCLAIMER:** The references listed below provided the conceptual baseline for constructing SafeTriage's deterministic triage rules and red-flag symptom lexicons. However, the software implementation, thresholds, and logic mappings were authored by computer science researchers and **have NOT been formally certified, reviewed, or verified by licensed medical clinicians** (`verified=false`).

---

## 1. Primary Clinical Guidelines

1. **National Institute for Health and Care Excellence (NICE)**
   - *Fever in under 5s: assessment and initial management (NG143)* (2019). Traffic light system for identifying risk of serious illness in infants and children.
   - *Suspected sepsis: recognition, diagnosis and early management (NG51)* (2016, updated 2024). Red-flag criteria for systemic infection, hemodynamic instability, and altered mental status.
   - *Chest pain of recent onset: assessment and diagnosis (CG95)* (2010, updated 2016). Differentiating acute coronary syndromes (ACS) from non-cardiac causes.
   - *Head injury: assessment and early management (NG232)* (2023). Indications for urgent head CT and emergency trauma assessment (Canadian CT Head Rule / PECARN adaptations).

2. **Indian Academy of Pediatrics (IAP)**
   - *Consensus Guidelines on Pediatric Triage and Resuscitation* (2020). Pediatric assessment triangle (Appearance, Work of Breathing, Circulation) adapted for primary healthcare in India.
   - *National Guidelines for Pediatric Sepsis and Shock* (2022). Fluid resuscitation triggers and immediate triage priorities.

3. **American Heart Association / American College of Cardiology (AHA/ACC)**
   - *2021 Guideline for the Evaluation and Diagnosis of Chest Pain*. Emergency department stratification, atypical presentations (diabetic, elderly, female presentations), and red-flag symptom constellations.

4. **American Stroke Association (ASA)**
   - *Guidelines for the Early Management of Patients With Acute Ischemic Stroke* (2019). FAST criteria (Face, Arm, Speech, Time) for hyperacute stroke triage.

5. **Manchester Triage System (MTS) & Emergency Severity Index (ESI)**
   - Mackway-Jones, K., Marsden, J., & Windle, J. (Eds.). *Emergency Triage: Manchester Triage Group* (3rd ed., 2014). Flowchart-based urgency assignment from Level 1 (Immediate) to Level 5 (Non-urgent).
   - Gilboy, N., et al. *Emergency Severity Index (ESI): A Triage Tool for Emergency Department Care, Version 4* (AHRQ Publication No. 12-0014, 2012).

---

## 2. Medical NLP & Negation Literature

6. **Harkema, H., Dowling, J. N., Thornblade, T., & Chapman, W. W. (2009)**
   - *Context: An algorithm for determining negation, experiencer, and temporality in clinical notes.* Journal of Biomedical Informatics, 42(5), 839-851.
   - Basis for SafeTriage's scoped windowed negation detection and historical experiencer exclusion.

7. **Kocaballi, A. B., et al. (2020)**
   - *The safety and usability of consumer-facing medical triage chatbots.* Journal of Medical Internet Research, 22(8), e20386.

8. **Semigran, H. L., Linder, J. A., Gidengil, C., & Mehrotra, A. (2015)**
   - *Evaluation of symptom checkers for self diagnosis and triage: audit study.* BMJ, 351, h3480. Highlighting safety discrepancies and under-triage risks in consumer symptom apps.
