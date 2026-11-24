# SafeTriage Clinical Review Protocol & Evaluation Form

**Document Status**: PENDING CLINICIAN REVIEW (BLOCKED until formal clinical sign-off)

**Protocol Version**: 1.0.0

**System Description**: SafeTriage Research Prototype (Preliminary Medical Urgency Stratification)

**Clinical Safety Boundary**: Non-diagnostic, non-prescriptive preliminary symptom triage.
Emergency triage numbers: **112 / 108**.

---

## Instructions for Clinical Reviewers

1. **Section 1 (Rules Review)**: Review each of the 31 deterministic clinical triage rules. Verify if the assigned urgency level (1=Emergency, 2=Urgent, 3=Routine, 4=Self-care) conforms to standard clinical practice (NICE, IAP, AHA/ACC guidelines).
2. **Section 2 (100-Case Stratified Sample Review)**: Evaluate the 100 synthetic vignettes sampled with fixed seed 42 (25 cases per urgency level). Assess whether the developer-assigned gold level is clinically sound, and flag any risks of under-triage or severe over-triage.
3. **Section 3 (Sign-Off & Inter-Rater Reliability)**: Sign off and compute agreement (Cohen's Kappa).

---

## Section 1: Clinical Rules Review Checklist (31 Rules)

### Rule 1: `ALLG-001` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'anaphylaxis', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 2: `CARD-001` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'chest_pain', 'status': 'POSITIVE'}]`, Any of: `[{'modifier': 'crushing'}, {'modifier': 'radiating'}, {'severity': 'severe'}, {'matched_term': 'dil ka daura'}]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 3: `GAST-001` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'abdominal_pain', 'status': 'POSITIVE'}]`, Any of: `[{'severity': 'severe'}, {'onset': 'sudden'}, {'concept': 'severe_bleeding', 'status': 'POSITIVE'}]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 4: `INFN-001` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'fever', 'status': 'POSITIVE'}]`, Any of: `[{'concept': 'altered_mental_status', 'status': 'POSITIVE'}, {'severity': 'severe'}]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 5: `NEUR-001` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'stroke_symptoms', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 6: `NEUR-002` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'headache', 'status': 'POSITIVE'}]`, Any of: `[{'modifier': 'worst_ever'}, {'onset': 'sudden'}]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 7: `NEUR-003` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'seizure', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 8: `PED-001` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'age_band': {'any_of': ['neonate', 'young_infant', 'older_infant', 'toddler', 'preschool_child', 'school_age_child']}}]`, Any of: `[{'concept': 'altered_mental_status', 'status': 'POSITIVE'}, {'concept': 'seizure', 'status': 'POSITIVE'}, {'modifier': 'breathless'}]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 9: `PED-002` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'fever', 'status': 'POSITIVE'}, {'age_band': {'any_of': ['neonate', 'young_infant']}}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 10: `RESP-001` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'breathlessness', 'status': 'POSITIVE'}]`, Any of: `[{'severity': 'severe'}, {'modifier': 'breathless'}, {'matched_term': "can't breathe"}, {'matched_term': 'cannot breathe'}, {'matched_term': 'gasping'}, {'matched_term': 'stridor'}]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 11: `TRAU-001` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'snakebite', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 12: `TRAU-002` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'severe_bleeding', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 13: `TRAU-003` (Developer Level 1)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'fever', 'status': 'POSITIVE'}, {'concept': 'altered_mental_status', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 14: `ALLG-002` (Developer Level 2)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'rash', 'status': 'POSITIVE'}, {'onset': 'sudden'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 15: `CARD-002` (Developer Level 2)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'chest_pain', 'status': 'POSITIVE'}, {'age_band': 'older_adult'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 16: `GAST-002` (Developer Level 2)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'diarrhea', 'status': 'POSITIVE'}, {'concept': 'vomiting', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 17: `GENU-001` (Developer Level 2)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'dvt_symptoms', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 18: `INFN-002` (Developer Level 2)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'fever', 'status': 'POSITIVE'}, {'concept': 'abdominal_pain', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 19: `NEUR-004` (Developer Level 2)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'altered_mental_status', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 20: `PED-003` (Developer Level 2)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'fever', 'status': 'POSITIVE'}, {'age_band': 'older_infant'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 21: `PED-004` (Developer Level 2)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'diarrhea', 'status': 'POSITIVE'}, {'age_band': {'any_of': ['young_infant', 'older_infant', 'toddler', 'preschool_child']}}]`, Any of: `[{'concept': 'vomiting', 'status': 'POSITIVE'}, {'severity': 'moderate'}]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 22: `RESP-002` (Developer Level 2)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'breathlessness', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 23: `CARD-003` (Developer Level 3)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'chest_pain', 'status': 'POSITIVE'}, {'severity': 'mild'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 24: `GAST-003` (Developer Level 3)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'diarrhea', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 25: `GENU-002` (Developer Level 3)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'dysuria', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 26: `INFN-003` (Developer Level 3)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'fever', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 27: `NEUR-005` (Developer Level 3)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'headache', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 28: `RESP-003` (Developer Level 3)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'cough', 'status': 'POSITIVE'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 29: `SELF-001` (Developer Level 4)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'cough', 'status': 'POSITIVE'}, {'severity': 'mild'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 30: `SELF-002` (Developer Level 4)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'rash', 'status': 'POSITIVE'}, {'severity': 'mild'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

### Rule 31: `SELF-003` (Developer Level 4)
- **Specialty**: N/A
- **Description**: N/A
- **Citation**: N/A (Verified: False)
- **Conditions**: Required: `[{'concept': 'headache', 'status': 'POSITIVE'}, {'severity': 'mild'}]`, Any of: `[]`, Age bands: `Any`
- **Clinician Evaluation**:
  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`
  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`
  - Safety Concern / Notes: ____________________________________________________
  - Reviewer Initials: ________  Date: ____________

---

## Section 2: Stratified 100-Case Vignette Sample

*Sample generated deterministically using Seed 42 from `datasets/synthetic_dev/full_dataset.json` (25 cases each for Levels 1, 2, 3, 4).*

### Vignette 001 (ID: `SYN_0013`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_01` | **Style**: marathi
- **Demographics**: 62.0 y/o, female
- **Patient Presentation**: "Patient notes: Diabetic patient thandagar ghaam aala ahe aani be-shuddha ahet uthat nahiye."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 002 (ID: `SYN_0014`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_01` | **Style**: typos
- **Demographics**: 62.0 y/o, female
- **Patient Presentation**: "Patient notes: Diabetic insuline unconsious cold swet sugar 32 cant wake."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 003 (ID: `SYN_0016`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_01` | **Style**: historical
- **Demographics**: 62.0 y/o, female
- **Patient Presentation**: "Patient notes: Type 1 diabetes for 15 years with hypoglycemia unawareness."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 004 (ID: `SYN_0017`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_01` | **Style**: third_party
- **Demographics**: 62.0 y/o, female
- **Patient Presentation**: "Patient notes: My father with diabetes is slumped over the table drenched in sweat and not responding."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 005 (ID: `SYN_0045`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_01` | **Style**: formal
- **Demographics**: 56.0 y/o, male
- **Patient Presentation**: "Patient notes: Acute severe generalized abdominal pain with involuntary abdominal wall rigidity, guarding, and vomiting dark coffee-ground blood."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 006 (ID: `SYN_0048`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_01` | **Style**: marathi
- **Demographics**: 56.0 y/o, male
- **Patient Presentation**: "Patient notes: Pota madhe achanak khup jorat dukhat ahe pot tathan zale ahe aani kalyashar raktachi ulti zali."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 007 (ID: `SYN_0053`)
- **Specialty**: pediatric | **Family ID**: `FAM_PED_01` | **Style**: formal
- **Demographics**: Unknown age, female
- **Patient Presentation**: "Neonate 18 days old presenting with rectal temperature of 38.3C, poor feeding and lethargy."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 008 (ID: `SYN_0058`)
- **Specialty**: pediatric | **Family ID**: `FAM_PED_01` | **Style**: negation
- **Demographics**: Unknown age, female
- **Patient Presentation**: "No cough, but neonate under 28 days with core temperature >=38.0C requires immediate neonatal sepsis workup."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 009 (ID: `SYN_0072`)
- **Specialty**: respiratory | **Family ID**: `FAM_RESP_02` | **Style**: hinglish
- **Demographics**: 52.0 y/o, male
- **Patient Presentation**: "Gale mein khana phas gaya hai saans atak gayi hai awaz nahi nikal rahi."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 010 (ID: `SYN_0102`)
- **Specialty**: infectious_fever | **Family ID**: `FAM_INFN_02` | **Style**: historical
- **Demographics**: 21.0 y/o, male
- **Patient Presentation**: "Patient notes: College student living in dormitory, presented with rapid febrile meningeal syndrome."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 011 (ID: `SYN_0112`)
- **Specialty**: environmental_trauma | **Family ID**: `FAM_TRAU_03` | **Style**: minimized
- **Demographics**: 39.0 y/o, male
- **Patient Presentation**: "He overheated terribly in the sun and is out cold with boiling hot skin."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 012 (ID: `SYN_0113`)
- **Specialty**: environmental_trauma | **Family ID**: `FAM_TRAU_03` | **Style**: formal
- **Demographics**: 39.0 y/o, male
- **Patient Presentation**: "Patient notes: Collapse following prolonged physical exertion in 43C ambient heat, core temperature 41C, anhidrosis, coma."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 013 (ID: `SYN_0115`)
- **Specialty**: environmental_trauma | **Family ID**: `FAM_TRAU_03` | **Style**: hinglish
- **Demographics**: 39.0 y/o, male
- **Patient Presentation**: "Patient notes: Bohot dhoop mein kaam karte waqt gir pada sharir aag jaisa garam hai aur koi aawaz nahi sun raha."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 014 (ID: `SYN_0120`)
- **Specialty**: environmental_trauma | **Family ID**: `FAM_TRAU_03` | **Style**: third_party
- **Demographics**: 39.0 y/o, male
- **Patient Presentation**: "Patient notes: A marathon runner collapsed near the finish line in blistering heat, completely unresponsive."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 015 (ID: `SYN_0126`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_02` | **Style**: negation
- **Demographics**: 69.0 y/o, female
- **Patient Presentation**: "No minor hemorrhoidal spotting on paper, large volumes of pure red blood filling the toilet bowl."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 016 (ID: `SYN_0141`)
- **Specialty**: infectious_fever | **Family ID**: `FAM_INFN_01` | **Style**: marathi
- **Demographics**: 78.0 y/o, male
- **Patient Presentation**: "Khup jorat taap ahe shuddhi var nahiye bhabdlya sarkha boltoy shwas jorat chaltoy."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 017 (ID: `SYN_0215`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_02` | **Style**: minimized
- **Demographics**: 38.0 y/o, male
- **Patient Presentation**: "Stung by something in the yard, now covered in spots and feeling like passing out."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 018 (ID: `SYN_0217`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_02` | **Style**: colloquial
- **Demographics**: 38.0 y/o, male
- **Patient Presentation**: "Patient notes: I got stung by a wasp 5 minutes ago and now I have hives everywhere, can't breathe and feeling faint."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 019 (ID: `SYN_0823`)
- **Specialty**: pediatric | **Family ID**: `FAM_PED_02` | **Style**: formal
- **Demographics**: 1.5 y/o, male
- **Patient Presentation**: "Toddler 18 months old with fever 39.5C experiencing generalized tonic-clonic seizure persisting past 10 minutes."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 020 (ID: `SYN_0844`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_01` | **Style**: typos
- **Demographics**: 16.0 y/o, male
- **Patient Presentation**: "Sudden agnizing pain in left testicel swolen up 1 hr ago."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 021 (ID: `SYN_0852`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_01` | **Style**: marathi
- **Demographics**: 16.0 y/o, male
- **Patient Presentation**: "Patient notes: Achanak andashayat khup tivra vedna suru zalya aani sujan aali ahe ulti watte."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 022 (ID: `SYN_0867`)
- **Specialty**: cardiac | **Family ID**: `FAM_CARD_02` | **Style**: colloquial
- **Demographics**: 64.0 y/o, male
- **Patient Presentation**: "Patient notes: I feel like I am having a heart attack right now my chest is squeezing tight."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 023 (ID: `SYN_0873`)
- **Specialty**: cardiac | **Family ID**: `FAM_CARD_02` | **Style**: third_party
- **Demographics**: 64.0 y/o, male
- **Patient Presentation**: "Patient notes: My husband collapsed onto the chair saying he feels like he is having a heart attack."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 024 (ID: `SYN_1029`)
- **Specialty**: neuro | **Family ID**: `FAM_NEUR_02` | **Style**: minimized
- **Demographics**: 44.0 y/o, male
- **Patient Presentation**: "Patient notes: I usually do not complain about headaches, but this sudden explosive headache is terrifyingly severe."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 025 (ID: `SYN_1034`)
- **Specialty**: environmental_trauma | **Family ID**: `FAM_TRAU_01` | **Style**: typos
- **Demographics**: 36.0 y/o, male
- **Patient Presentation**: "Snak bite on fot 2 fang marks sweling spreding fast eyelids droping."
- **Developer Gold Urgency Level**: **Level 1** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 026 (ID: `SYN_0227`)
- **Specialty**: pediatric | **Family ID**: `FAM_PED_04` | **Style**: marathi
- **Demographics**: 1.6 y/o, male
- **Patient Presentation**: "Veess mahinyacha baal ahe ulti julaab mule aath taasat lagnicha diaper bharla nahiye dolye khali gele ahet."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 027 (ID: `SYN_0246`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_03` | **Style**: negation
- **Demographics**: 30.0 y/o, male
- **Patient Presentation**: "No throat swelling, no wheezing, no difficulty swallowing, but rash is extremely pruritic and spreading rapidly."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 028 (ID: `SYN_0264`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_04` | **Style**: historical
- **Demographics**: 55.0 y/o, female
- **Patient Presentation**: "Started new antihypertensive medication 10 days ago, now developed isolated angioedema."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 029 (ID: `SYN_0271`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_04` | **Style**: typos
- **Demographics**: 55.0 y/o, female
- **Patient Presentation**: "Patient notes: Eyelids and lip swolen puffy this morning no brething issue."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 030 (ID: `SYN_0273`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_04` | **Style**: historical
- **Demographics**: 55.0 y/o, female
- **Patient Presentation**: "Patient notes: Started new antihypertensive medication 10 days ago, now developed isolated angioedema."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 031 (ID: `SYN_0276`)
- **Specialty**: infectious_fever | **Family ID**: `FAM_INFN_04` | **Style**: colloquial
- **Demographics**: 51.0 y/o, female
- **Patient Presentation**: "I am on chemo treatment and developed a fever of 101.4 today with shaking chills."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 032 (ID: `SYN_0287`)
- **Specialty**: infectious_fever | **Family ID**: `FAM_INFN_04` | **Style**: marathi
- **Demographics**: 51.0 y/o, female
- **Patient Presentation**: "Patient notes: Cancer chemotherapy chalu ahe aani achanak taap bharla thandi wajun aali."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 033 (ID: `SYN_0303`)
- **Specialty**: cardiac | **Family ID**: `FAM_CARD_03` | **Style**: hinglish
- **Demographics**: 72.0 y/o, female
- **Patient Presentation**: "Patient notes: Do din se chhaati ke beech mein dheema dheema dard bana hua hai thakan lag rahi hai."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 034 (ID: `SYN_0305`)
- **Specialty**: cardiac | **Family ID**: `FAM_CARD_03` | **Style**: typos
- **Demographics**: 72.0 y/o, female
- **Patient Presentation**: "Patient notes: Dul chesd pane for two days feling tierd and week."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 035 (ID: `SYN_0334`)
- **Specialty**: respiratory | **Family ID**: `FAM_RESP_04` | **Style**: third_party
- **Demographics**: 54.0 y/o, male
- **Patient Presentation**: "My uncle coughed into a napkin and there were clear streaks and spoonfuls of blood."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 036 (ID: `SYN_0359`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_04` | **Style**: historical
- **Demographics**: 41.0 y/o, female
- **Patient Presentation**: "Patient notes: Developed acute gastroenteritis after banquet meal, progressing to clinical volume depletion."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 037 (ID: `SYN_0366`)
- **Specialty**: infectious_fever | **Family ID**: `FAM_INFN_03` | **Style**: negation
- **Demographics**: 35.0 y/o, female
- **Patient Presentation**: "No cough or sore throat, persistent high continuous fever beyond 5 days with break-bone body aches."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 038 (ID: `SYN_0396`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_03` | **Style**: colloquial
- **Demographics**: 19.0 y/o, male
- **Patient Presentation**: "Stomach ache started around my belly button yesterday and has moved down into my right hip and hurts when I cough."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 039 (ID: `SYN_0398`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_03` | **Style**: marathi
- **Demographics**: 19.0 y/o, male
- **Patient Presentation**: "Aadhi bembi javal dukhata hota ata ujvya baajula khali potat khup vedna hot ahet."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 040 (ID: `SYN_0400`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_03` | **Style**: negation
- **Demographics**: 19.0 y/o, male
- **Patient Presentation**: "No diarrhea, pain migrated from mid-abdomen to right iliac fossa with localized rebound tenderness."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 041 (ID: `SYN_0407`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_03` | **Style**: marathi
- **Demographics**: 19.0 y/o, male
- **Patient Presentation**: "Patient notes: Aadhi bembi javal dukhata hota ata ujvya baajula khali potat khup vedna hot ahet."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 042 (ID: `SYN_0417`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_03` | **Style**: negation
- **Demographics**: 66.0 y/o, male
- **Patient Presentation**: "No syncope when lying down, symptoms occur exclusively upon assuming upright posture."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 043 (ID: `SYN_0418`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_03` | **Style**: historical
- **Demographics**: 66.0 y/o, male
- **Patient Presentation**: "Recently doubled dosage of blood pressure medication 4 days ago."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 044 (ID: `SYN_0440`)
- **Specialty**: neuro | **Family ID**: `FAM_NEUR_05` | **Style**: hinglish
- **Demographics**: 69.0 y/o, male
- **Patient Presentation**: "Patient notes: Chakkar aa rahe hain sab ghoom raha hai aur chalne par ladkhada raha hoon girne lagta hoon."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 045 (ID: `SYN_0453`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_03` | **Style**: third_party
- **Demographics**: 71.0 y/o, male
- **Patient Presentation**: "My elderly father has been groaning on the toilet unable to pass a single drop of urine for 12 hours."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 046 (ID: `SYN_0459`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_03` | **Style**: typos
- **Demographics**: 71.0 y/o, male
- **Patient Presentation**: "Patient notes: Cant pe at all for 14 hrs blader bursting pain."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 047 (ID: `SYN_0910`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_02` | **Style**: colloquial
- **Demographics**: 73.0 y/o, female
- **Patient Presentation**: "I suddenly blacked out and fainted while sitting in my armchair, woke up on the floor 30 seconds later."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 048 (ID: `SYN_0918`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_02` | **Style**: formal
- **Demographics**: 73.0 y/o, female
- **Patient Presentation**: "Patient notes: Sudden unheralded syncopal episode while seated 1 hour ago, complete loss of consciousness for 30 seconds with spontaneous recovery."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 049 (ID: `SYN_1058`)
- **Specialty**: cardiac | **Family ID**: `FAM_CARD_04` | **Style**: hinglish
- **Demographics**: 61.0 y/o, female
- **Patient Presentation**: "Patient notes: Jab bhi seedhiyan chadhta hoon chhaati bhari ho jaati hai aur rukne par theek hoti hai."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 050 (ID: `SYN_1066`)
- **Specialty**: environmental_trauma | **Family ID**: `FAM_TRAU_05` | **Style**: colloquial
- **Demographics**: 22.0 y/o, male
- **Patient Presentation**: "Hit my head playing soccer, was knocked out for a few seconds and now threw up and can't remember the score."
- **Developer Gold Urgency Level**: **Level 2** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 051 (ID: `SYN_0486`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_05` | **Style**: historical
- **Demographics**: 31.0 y/o, female
- **Patient Presentation**: "Occasional stress-induced sleep initiation insomnia."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 052 (ID: `SYN_0498`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_06` | **Style**: colloquial
- **Demographics**: 43.0 y/o, male
- **Patient Presentation**: "I get a burning feeling in the upper middle stomach and acid taste in my throat after eating fried food."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 053 (ID: `SYN_0499`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_06` | **Style**: hinglish
- **Demographics**: 43.0 y/o, male
- **Patient Presentation**: "Khane ke baad chhaati ke neeche pet mein jalan hoti hai aur khatte dakaar aate hain."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 054 (ID: `SYN_0503`)
- **Specialty**: gastro_abdominal | **Family ID**: `FAM_GAST_06` | **Style**: historical
- **Demographics**: 43.0 y/o, male
- **Patient Presentation**: "Longstanding history of mild gastroesophageal reflux disease when diet is poor."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 055 (ID: `SYN_0514`)
- **Specialty**: neuro | **Family ID**: `FAM_NEUR_06` | **Style**: formal
- **Demographics**: 28.0 y/o, female
- **Patient Presentation**: "Bilateral band-like dull headache of moderate intensity without nausea or photophobia for 2 days."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 056 (ID: `SYN_0546`)
- **Specialty**: pediatric | **Family ID**: `FAM_PED_05` | **Style**: historical
- **Demographics**: 7.0 y/o, female
- **Patient Presentation**: "Patient notes: Standard viral cold caught from classmates at primary school."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 057 (ID: `SYN_0550`)
- **Specialty**: infectious_fever | **Family ID**: `FAM_INFN_05` | **Style**: hinglish
- **Demographics**: 29.0 y/o, male
- **Patient Presentation**: "Do din se halka bukhar 100 degree hai badan mein thoda thoda dard hai aalas lag raha hai."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 058 (ID: `SYN_0561`)
- **Specialty**: infectious_fever | **Family ID**: `FAM_INFN_05` | **Style**: typos
- **Demographics**: 29.0 y/o, male
- **Patient Presentation**: "Patient notes: Mild fevar 100 for 2 days body akes tierdness."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 059 (ID: `SYN_0570`)
- **Specialty**: respiratory | **Family ID**: `FAM_RESP_05` | **Style**: negation
- **Demographics**: 31.0 y/o, female
- **Patient Presentation**: "No fever, no phlegm, no shortness of breath, just a constant annoying tickle in the throat."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 060 (ID: `SYN_0579`)
- **Specialty**: respiratory | **Family ID**: `FAM_RESP_05` | **Style**: negation
- **Demographics**: 31.0 y/o, female
- **Patient Presentation**: "Patient notes: No fever, no phlegm, no shortness of breath, just a constant annoying tickle in the throat."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 061 (ID: `SYN_0582`)
- **Specialty**: respiratory | **Family ID**: `FAM_RESP_06` | **Style**: formal
- **Demographics**: 36.0 y/o, male
- **Patient Presentation**: "Productive cough with moderate yellow-green expectoration for 5 days, afebrile, respiratory rate normal."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 062 (ID: `SYN_0588`)
- **Specialty**: respiratory | **Family ID**: `FAM_RESP_06` | **Style**: historical
- **Demographics**: 36.0 y/o, male
- **Patient Presentation**: "Develops chesty coughs annually with seasonal weather changes."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 063 (ID: `SYN_0599`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_06` | **Style**: formal
- **Demographics**: 33.0 y/o, male
- **Patient Presentation**: "Bilateral conjunctival injection, clear rhinorrhea, sneezing paroxysms and mild palatal itching during pollen season."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 064 (ID: `SYN_0605`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_06` | **Style**: historical
- **Demographics**: 33.0 y/o, male
- **Patient Presentation**: "Annual springtime allergic rhinosinusitis coinciding with flowering trees."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 065 (ID: `SYN_0611`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_06` | **Style**: marathi
- **Demographics**: 33.0 y/o, male
- **Patient Presentation**: "Patient notes: Dolyatun paani yetay aani shinka yet ahet sardi zali ahe unhalyat."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 066 (ID: `SYN_0613`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_06` | **Style**: negation
- **Demographics**: 33.0 y/o, male
- **Patient Presentation**: "Patient notes: No fever, no purulent discharge, no facial pressure, strictly bilateral allergic symptoms."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 067 (ID: `SYN_0644`)
- **Specialty**: cardiac | **Family ID**: `FAM_CARD_05` | **Style**: hinglish
- **Demographics**: 29.0 y/o, male
- **Patient Presentation**: "Patient notes: Pasliyon par ungli dabane se dard hota hai mudne par zyada lagta hai."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 068 (ID: `SYN_0648`)
- **Specialty**: cardiac | **Family ID**: `FAM_CARD_05` | **Style**: historical
- **Demographics**: 29.0 y/o, male
- **Patient Presentation**: "Patient notes: Started working out with weights 3 days ago, developed sharp localized rib ache."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 069 (ID: `SYN_0649`)
- **Specialty**: cardiac | **Family ID**: `FAM_CARD_05` | **Style**: third_party
- **Demographics**: 29.0 y/o, male
- **Patient Presentation**: "Patient notes: My son says his upper chest rib is tender after his football training session."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 070 (ID: `SYN_0652`)
- **Specialty**: environmental_trauma | **Family ID**: `FAM_TRAU_06` | **Style**: colloquial
- **Demographics**: 34.0 y/o, female
- **Patient Presentation**: "Accidentally spilled hot boiling tea on my thigh, have a red painful blister about the size of a coin."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 071 (ID: `SYN_0657`)
- **Specialty**: environmental_trauma | **Family ID**: `FAM_TRAU_06` | **Style**: historical
- **Demographics**: 34.0 y/o, female
- **Patient Presentation**: "Domestic kitchen spill 30 minutes ago, cooled immediately with running tap water for 15 minutes."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 072 (ID: `SYN_0936`)
- **Specialty**: cardiac | **Family ID**: `FAM_CARD_06` | **Style**: colloquial
- **Demographics**: 25.0 y/o, female
- **Patient Presentation**: "Patient notes: My heart feels like it flutters or skips a beat sometimes after drinking morning coffee."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 073 (ID: `SYN_0940`)
- **Specialty**: cardiac | **Family ID**: `FAM_CARD_06` | **Style**: negation
- **Demographics**: 25.0 y/o, female
- **Patient Presentation**: "Patient notes: No chest tightness, fainting or breathlessness, only brief 5-second fluttering sensations."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 074 (ID: `SYN_1132`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_05` | **Style**: third_party
- **Demographics**: 42.0 y/o, male
- **Patient Presentation**: "Patient notes: My brother is pacing the floor clutching his side saying his kidney stone pain has returned."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 075 (ID: `SYN_1154`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_05` | **Style**: typos
- **Demographics**: 27.0 y/o, female
- **Patient Presentation**: "Itchi red rash under mettle watch on rist."
- **Developer Gold Urgency Level**: **Level 3** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 076 (ID: `SYN_0693`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_06` | **Style**: minimized
- **Demographics**: 24.0 y/o, male
- **Patient Presentation**: "Urine was just a bit dark after jogging without my water bottle."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 077 (ID: `SYN_0699`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_06` | **Style**: negation
- **Demographics**: 24.0 y/o, male
- **Patient Presentation**: "Patient notes: No burning, no frequency, no back pain, color normalized to pale straw after drinking 1 liter of water."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 078 (ID: `SYN_0701`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_06` | **Style**: third_party
- **Demographics**: 24.0 y/o, male
- **Patient Presentation**: "Patient notes: My friend noticed his urine was dark amber after our long afternoon bike ride."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 079 (ID: `SYN_0739`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_07` | **Style**: hinglish
- **Demographics**: 20.0 y/o, male
- **Patient Presentation**: "Raat ko machhar ne kaat liya tha hath par halka sa laal daana aur khujli hai."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 080 (ID: `SYN_0741`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_07` | **Style**: typos
- **Demographics**: 20.0 y/o, male
- **Patient Presentation**: "Moskito bite on arm litel red bumb itches."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 081 (ID: `SYN_0743`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_07` | **Style**: historical
- **Demographics**: 20.0 y/o, male
- **Patient Presentation**: "Usual reaction to mosquito bites during monsoon season."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 082 (ID: `SYN_0753`)
- **Specialty**: allergy_immune | **Family ID**: `FAM_ALLG_07` | **Style**: third_party
- **Demographics**: 20.0 y/o, male
- **Patient Presentation**: "Patient notes: My son has two mosquito bites on his ankle that he is scratching."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 083 (ID: `SYN_0754`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_07` | **Style**: formal
- **Demographics**: 27.0 y/o, female
- **Patient Presentation**: "Transient mild urethral awareness for 1 hour following sexual intercourse, completely resolved, no discharge or frequency."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 084 (ID: `SYN_0765`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_07` | **Style**: hinglish
- **Demographics**: 27.0 y/o, female
- **Patient Presentation**: "Patient notes: Ek baar peshab mein halki chubhan hui thi ab sab normal hai koi takleef nahi hai."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 085 (ID: `SYN_0768`)
- **Specialty**: genitourinary | **Family ID**: `FAM_GENU_07` | **Style**: negation
- **Demographics**: 27.0 y/o, female
- **Patient Presentation**: "Patient notes: No persistent burning, no discharge, no rash, no pelvic pain, isolated fleeting sensation."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 086 (ID: `SYN_0782`)
- **Specialty**: neuro | **Family ID**: `FAM_NEUR_07` | **Style**: hinglish
- **Demographics**: 23.0 y/o, female
- **Patient Presentation**: "Patient notes: Dhoop mein ghoomne se halka sa sir dard ho raha hai paani kam piya tha."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 087 (ID: `SYN_0786`)
- **Specialty**: neuro | **Family ID**: `FAM_NEUR_07` | **Style**: historical
- **Demographics**: 23.0 y/o, female
- **Patient Presentation**: "Patient notes: Regular dehydration twinge that resolves completely after fluids and rest."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 088 (ID: `SYN_0787`)
- **Specialty**: neuro | **Family ID**: `FAM_NEUR_07` | **Style**: third_party
- **Demographics**: 23.0 y/o, female
- **Patient Presentation**: "Patient notes: My friend says she has a slight dehydration headache after our long park walk."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 089 (ID: `SYN_0968`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_07` | **Style**: third_party
- **Demographics**: 29.0 y/o, female
- **Patient Presentation**: "My sister rubbed her eyes saying they feel dry from looking at monitors all day."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 090 (ID: `SYN_0983`)
- **Specialty**: environmental_trauma | **Family ID**: `FAM_TRAU_07` | **Style**: negation
- **Demographics**: 26.0 y/o, male
- **Patient Presentation**: "No deep tissue damage, no foreign body, bleeding completely clotted, epidermis intact."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 091 (ID: `SYN_0986`)
- **Specialty**: environmental_trauma | **Family ID**: `FAM_TRAU_07` | **Style**: minimized
- **Demographics**: 26.0 y/o, male
- **Patient Presentation**: "Just a silly little paper cut that stings when washing hands."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 092 (ID: `SYN_1004`)
- **Specialty**: pediatric | **Family ID**: `FAM_PED_07` | **Style**: formal
- **Demographics**: Unknown age, male
- **Patient Presentation**: "Patient notes: Infant 9 months old with mild erythematous macular erythema confined strictly to diaper contact areas, skin folds spared."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 093 (ID: `SYN_1005`)
- **Specialty**: pediatric | **Family ID**: `FAM_PED_07` | **Style**: colloquial
- **Demographics**: Unknown age, male
- **Patient Presentation**: "Patient notes: My 9 month old baby has mild red irritation on his bottom from his diaper, smiling and playing normally."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 094 (ID: `SYN_1008`)
- **Specialty**: pediatric | **Family ID**: `FAM_PED_07` | **Style**: typos
- **Demographics**: Unknown age, male
- **Patient Presentation**: "Patient notes: 9 mo babi red diaper rash smilin playin normel."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 095 (ID: `SYN_1171`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_06` | **Style**: typos
- **Demographics**: 25.0 y/o, male
- **Patient Presentation**: "Sore thiegh musles after jim yestarday stif on stares."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 096 (ID: `SYN_1172`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_06` | **Style**: negation
- **Demographics**: 25.0 y/o, male
- **Patient Presentation**: "No joint swelling, no dark tea-colored urine, no focal muscle tear, symmetric bilateral post-exercise soreness."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 097 (ID: `SYN_1179`)
- **Specialty**: general_self_care | **Family ID**: `FAM_GENL_06` | **Style**: marathi
- **Demographics**: 25.0 y/o, male
- **Patient Presentation**: "Patient notes: Kal vyayam kelyamule mandya bharun aalya ahet thoda dukhtay halchaal kartana."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 098 (ID: `SYN_1184`)
- **Specialty**: infectious_fever | **Family ID**: `FAM_INFN_07` | **Style**: formal
- **Demographics**: 27.0 y/o, male
- **Patient Presentation**: "Mild transient low-grade fever 37.8C occurring 12 hours after routine tetanus toxoid vaccination with localized injection site soreness."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 099 (ID: `SYN_1188`)
- **Specialty**: infectious_fever | **Family ID**: `FAM_INFN_07` | **Style**: typos
- **Demographics**: 27.0 y/o, male
- **Patient Presentation**: "Tetanus shot yestarday arm sore slight 99 fevar."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

### Vignette 100 (ID: `SYN_1192`)
- **Specialty**: infectious_fever | **Family ID**: `FAM_INFN_07` | **Style**: minimized
- **Demographics**: 27.0 y/o, male
- **Patient Presentation**: "Arm is a little tender from the vaccine and running a tiny 99 temp, feels expected."
- **Developer Gold Urgency Level**: **Level 4** (developer_assigned_unreviewed)
- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*
- **Clinician Assessment**:
  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`
  - Agreement with Developer Level: `[ ] Yes  [ ] No`
  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`
  - Clinician Rationale / Action Plan: __________________________________________
  - Reviewer Initials: ________  Date: ____________

---

## Section 3: Clinician Sign-Off & Cohen's Kappa Computation

| Metric | Developer vs Clinician 1 | Developer vs Clinician 2 | Inter-Clinician (C1 vs C2) |
| :--- | :--- | :--- | :--- |
| Observed Agreement ($P_o$) | _______ % | _______ % | _______ % |
| Expected Agreement ($P_e$) | _______ % | _______ % | _______ % |
| Cohen's Kappa ($\kappa$) | _______ | _______ | _______ |
| Safety Violations Flagged | _______ | _______ | _______ |

### Reviewer Attestation

- Lead Clinician Reviewer: _____________________________ (MD / Specialty: ___________________)
- Signature: _________________________________________ Date: __________________
- Secondary Clinician Reviewer: _______________________ (MD / Specialty: ___________________)
- Signature: _________________________________________ Date: __________________
