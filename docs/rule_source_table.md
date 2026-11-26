# Rule Source & Clinical Verification Table

> **CRITICAL COMPLIANCE NOTICE:**
> All 31 deterministic triage rules encoded in the SafeTriage engine are listed below with their public source guidelines.
> In accordance with dissertation ethics requirements, every rule has its review status strictly set to **`verified=false`** (`review_status="UNVERIFIED"`).
> **No clinical claim is made that these rules are safe for actual medical diagnosis or live triage without formal review by a licensed medical board.**

| Rule ID | Specialty | Rule Name | Urgency Level | Clinical Guideline Source | Rule Logic Summary | Verified Status |
|---|---|---|---|---|---|---|
| `CV-001` | Cardiology | Crushing Chest Pain with Diaphoresis | Level 1 | AHA/ACC 2021 Chest Pain Guidelines | Chest pain + sweating/cold clamminess or radiation to jaw/arm | `verified=false` (`UNVERIFIED`) |
| `CV-002` | Cardiology | Syncope with Exertion or Palpitations | Level 2 | ESC 2018 Guidelines for Syncope | Sudden transient loss of consciousness during or after physical exertion | `verified=false` (`UNVERIFIED`) |
| `CV-003` | Cardiology | Atypical Cardiac Presentation (Elderly/Diabetic) | Level 2 | AHA/ACC 2021 Chest Pain Guidelines | Dyspnea + nausea/fatigue in patients >= 65 or diabetic without classic pain | `verified=false` (`UNVERIFIED`) |
| `RESP-001`| Respiratory | Stridor or Acute Airway Obstruction | Level 1 | BTS/SIGN British Guideline on Asthma Management | Audible stridor or severe breathing difficulty with retractions | `verified=false` (`UNVERIFIED`) |
| `RESP-002`| Respiratory | Acute Severe Asthma Exacerbation | Level 1 | GINA 2023 Global Strategy for Asthma | Inability to complete sentences in one breath, tachypnea, severe wheeze | `verified=false` (`UNVERIFIED`) |
| `RESP-003`| Respiratory | Pleuritic Pain with Hemoptysis | Level 2 | BTS Suspected Pulmonary Embolism Guidelines | Coughing up blood accompanied by sharp unilateral chest pain | `verified=false` (`UNVERIFIED`) |
| `NEURO-001`| Neurology | Acute Focal Neurological Deficit (FAST) | Level 1 | ASA/AHA 2019 Acute Stroke Guidelines | Sudden facial droop, unilateral arm drift, or acute speech impediment | `verified=false` (`UNVERIFIED`) |
| `NEURO-002`| Neurology | Thunderclap Headache | Level 1 | AAN Practice Parameter on Headache | Sudden explosive headache reaching maximal intensity in < 1 minute | `verified=false` (`UNVERIFIED`) |
| `NEURO-003`| Neurology | Meningism (Fever + Stiff Neck + Photophobia) | Level 1 | IDSA Guidelines on Bacterial Meningitis | Fever accompanied by neck stiffness, photophobia, or non-blanching rash | `verified=false` (`UNVERIFIED`) |
| `PED-001` | Pediatrics | Neonatal / Young Infant High Fever | Level 1 | NICE NG143 Fever in Under 5s | Fever in infant under 3 months (< 90 days) | `verified=false` (`UNVERIFIED`) |
| `PED-002` | Pediatrics | Pediatric Lethargy with Poor Feeding | Level 1 | IAP Pediatric Triage Guidelines 2020 | Inability to feed, weak cry, decreased consciousness in child < 5 | `verified=false` (`UNVERIFIED`) |
| `PED-003` | Pediatrics | Barking Cough with Resting Stridor (Croup) | Level 2 | NICE CKS Croup Clinical Knowledge Summary | Harsh seal-like barking cough with inspiratory stridor at rest | `verified=false` (`UNVERIFIED`) |
| `GI-001`  | Gastroenterology | Acute Peritonism / Rigid Abdomen | Level 1 | WSES Guidelines on Peritonitis | Severe acute abdominal pain with guarding, rigidity, and rebound | `verified=false` (`UNVERIFIED`) |
| `GI-002`  | Gastroenterology | Upper GI Bleed (Hematemesis / Melena) | Level 1 | ACG Clinical Guideline: Upper GI Bleeding | Vomiting fresh or ground coffee blood, or passage of black tarry stools | `verified=false` (`UNVERIFIED`) |
| `GI-003`  | Gastroenterology | Acute Right Lower Quadrant Pain | Level 2 | WSES Jerusalem Guidelines on Appendicitis | Migratory periumbilical to right iliac fossa pain with anorexia/fever | `verified=false` (`UNVERIFIED`) |
| `ID-001`  | Infectious | Septic Presentation / Sepsis Red Flag | Level 1 | Surviving Sepsis Campaign 2021 / NICE NG51 | Fever + hypothermia + mottled skin, confusion, or oliguria | `verified=false` (`UNVERIFIED`) |
| `ID-002`  | Infectious | Hemorrhagic Dengue Presentation | Level 1 | WHO Guidelines on Dengue Clinical Management | Severe fever with spontaneous bleeding (petechiae, epistaxis, gums) | `verified=false` (`UNVERIFIED`) |
| `ID-003`  | Infectious | Persistent High Fever (> 7 Days) | Level 2 | IAP Approach to Fever of Unknown Origin | Continuous high temperature unresponsive to antipyretics for > 7 days | `verified=false` (`UNVERIFIED`) |
| `TRAUMA-001`| Trauma/Orthopedics| Compound Fracture / Neurovascular Deficit | Level 1 | BOA/BAPRAS Standards on Open Fractures | Open bone exposure or loss of distal pulse/sensation post-injury | `verified=false` (`UNVERIFIED`) |
| `TRAUMA-002`| Trauma/Orthopedics| Head Trauma with Loss of Consciousness | Level 1 | NICE NG232 / Canadian Head CT Rules | Head strike with retrograde amnesia, GCS drop, or recurrent vomiting | `verified=false` (`UNVERIFIED`) |
| `TRAUMA-003`| Trauma/Orthopedics| Inability to Bear Weight post Twist/Fall | Level 3 | Ottawa Ankle/Knee Decision Rules | Isolated joint swelling without neurovascular compromise | `verified=false` (`UNVERIFIED`) |
| `OBGYN-001`| Obstetrics/Gynecology| Severe Vaginal Bleeding with Syncope | Level 1 | RCOG Green-top Guideline on Ectopic Pregnancy | Acute severe pelvic pain + vaginal bleeding with dizziness or fainting | `verified=false` (`UNVERIFIED`) |
| `OBGYN-002`| Obstetrics/Gynecology| Preeclampsia Red Flags (Third Trimester) | Level 1 | ACOG Practice Bulletin: Gestational Hypertension | Third trimester severe frontal headache, visual blurring, right upper pain | `verified=false` (`UNVERIFIED`) |
| `OBGYN-003`| Obstetrics/Gynecology| Decreased Fetal Movement | Level 2 | RCOG Green-top Guideline on Reduced Fetal Movement | Significant reduction in normal daily fetal movement pattern | `verified=false` (`UNVERIFIED`) |
| `PSYCH-001`| Psychiatry | Active Suicidal Ideation with Intent/Plan | Level 1 | APA Practice Guideline for Suicide Assessment | Direct expression of suicide intent, self-harm, or auditory command | `verified=false` (`UNVERIFIED`) |
| `PSYCH-002`| Psychiatry | Severe Agitation with Acute Psychosis | Level 1 | NICE CG178 Psychosis and Schizophrenia | Extreme agitation, acute persecutory delusions threatening harm | `verified=false` (`UNVERIFIED`) |
| `PSYCH-003`| Psychiatry | Moderate Depressive Mood without Self-Harm| Level 3 | NICE NG222 Depression in Adults | Low mood and insomnia for 3 weeks without suicidal ideation | `verified=false` (`UNVERIFIED`) |
| `DERM-001` | Dermatology | Anaphylaxis with Urticaria & Angioedema | Level 1 | World Allergy Organization (WAO) Anaphylaxis | Rapidly spreading hives with lip/tongue swelling and wheezing | `verified=false` (`UNVERIFIED`) |
| `DERM-002` | Dermatology | Suspected Stevens-Johnson Syndrome | Level 1 | British Association of Dermatologists SJS Guide | Painful mucosal ulceration (mouth/eyes) with blistering skin detachment | `verified=false` (`UNVERIFIED`) |
| `DERM-003` | Dermatology | Spreading Cellulitis with Lymphangitis | Level 2 | IDSA Practice Guidelines on Skin Infection | Rapidly advancing hot erythema with red streaks and systemic chills | `verified=false` (`UNVERIFIED`) |
| `ROUTINE-001`| General Primary Care| Mild Upper Respiratory Symptoms | Level 4 | CDC Common Cold Management | Clear runny nose, mild sneezing, afebrile, duration < 4 days | `verified=false` (`UNVERIFIED`) |
