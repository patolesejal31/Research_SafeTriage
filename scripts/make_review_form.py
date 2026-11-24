"""Generate docs/clinician_review_form.md with 31 rules and 100-case stratified sample."""
import glob
import json
import os
import random
import yaml

def main():
    with open("datasets/synthetic_dev/full_dataset.json", "r", encoding="utf-8") as f:
        full_dataset = json.load(f)

    # Group by level
    by_level = {1: [], 2: [], 3: [], 4: []}
    for case in full_dataset:
        by_level[case["ground_truth_urgency"]].append(case)

    # Sample 25 per level with seed 42
    rng = random.Random(42)
    sampled_cases = []
    for lvl in [1, 2, 3, 4]:
        candidates = sorted(by_level[lvl], key=lambda x: x["case_id"])
        sampled = rng.sample(candidates, 25)
        sampled.sort(key=lambda x: x["case_id"])
        sampled_cases.extend(sampled)

    # Read 31 rules
    rules = []
    for p in sorted(glob.glob("backend/app/triage/rules/*.yaml")):
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            for r in data.get("rules", []):
                rules.append(r)

    rules.sort(key=lambda r: (r["level"], r["id"]))

    os.makedirs("docs", exist_ok=True)
    with open("docs/clinician_review_form.md", "w", encoding="utf-8", newline="\n") as out:
        out.write("# SafeTriage Clinical Review Protocol & Evaluation Form\n\n")
        out.write("**Document Status**: PENDING CLINICIAN REVIEW (BLOCKED until formal clinical sign-off)\n\n")
        out.write("**Protocol Version**: 1.0.0\n\n")
        out.write("**System Description**: SafeTriage Research Prototype (Preliminary Medical Urgency Stratification)\n\n")
        out.write("**Clinical Safety Boundary**: Non-diagnostic, non-prescriptive preliminary symptom triage.\n")
        out.write("Emergency triage numbers: **112 / 108**.\n\n")
        out.write("---\n\n")
        out.write("## Instructions for Clinical Reviewers\n\n")
        out.write("1. **Section 1 (Rules Review)**: Review each of the 31 deterministic clinical triage rules. Verify if the assigned urgency level (1=Emergency, 2=Urgent, 3=Routine, 4=Self-care) conforms to standard clinical practice (NICE, IAP, AHA/ACC guidelines).\n")
        out.write("2. **Section 2 (100-Case Stratified Sample Review)**: Evaluate the 100 synthetic vignettes sampled with fixed seed 42 (25 cases per urgency level). Assess whether the developer-assigned gold level is clinically sound, and flag any risks of under-triage or severe over-triage.\n")
        out.write("3. **Section 3 (Sign-Off & Inter-Rater Reliability)**: Sign off and compute agreement (Cohen's Kappa).\n\n")
        out.write("---\n\n")
        out.write("## Section 1: Clinical Rules Review Checklist (31 Rules)\n\n")
        
        for idx, r in enumerate(rules, 1):
            out.write(f"### Rule {idx}: `{r['id']}` (Developer Level {r['level']})\n")
            out.write(f"- **Specialty**: {r.get('specialty', 'N/A')}\n")
            out.write(f"- **Description**: {r.get('description', 'N/A')}\n")
            src = r.get("source", {})
            out.write(f"- **Citation**: {src.get('citation', 'N/A')} (Verified: {src.get('verified', False)})\n")
            conds = r.get("conditions", {})
            out.write(f"- **Conditions**: Required: `{conds.get('all_of', [])}`, Any of: `{conds.get('any_of', [])}`, Age bands: `{conds.get('age_bands', 'Any')}`\n")
            out.write("- **Clinician Evaluation**:\n")
            out.write("  - Recommended Level: `[ ] 1  [ ] 2  [ ] 3  [ ] 4`\n")
            out.write("  - Clinically Sound: `[ ] Approved  [ ] Needs Revision  [ ] Rejected`\n")
            out.write("  - Safety Concern / Notes: ____________________________________________________\n")
            out.write("  - Reviewer Initials: ________  Date: ____________\n\n")

        out.write("---\n\n")
        out.write("## Section 2: Stratified 100-Case Vignette Sample\n\n")
        out.write("*Sample generated deterministically using Seed 42 from `datasets/synthetic_dev/full_dataset.json` (25 cases each for Levels 1, 2, 3, 4).*\n\n")

        for idx, c in enumerate(sampled_cases, 1):
            out.write(f"### Vignette {idx:03d} (ID: `{c['case_id']}`)\n")
            out.write(f"- **Specialty**: {c['specialty']} | **Family ID**: `{c['family_id']}` | **Style**: {c['language_style']}\n")
            age_val = c.get('age_years')
            age_str = f"{age_val} y/o" if age_val is not None else "Unknown age"
            gender_str = c.get("sex", "unknown")
            out.write(f"- **Demographics**: {age_str}, {gender_str}\n")
            out.write(f"- **Patient Presentation**: \"{c['symptoms_text']}\"\n")
            out.write(f"- **Developer Gold Urgency Level**: **Level {c['ground_truth_urgency']}** ({c['label_source']})\n")
            if c.get("hinglish_marathi_reviewed") is False:
                out.write("- *Note: Hinglish / Marathi terms present in this case are unreviewed by a native speaker.*\n")
            out.write("- **Clinician Assessment**:\n")
            out.write("  - Clinician Urgency Level: `[ ] L1 (Emergency)  [ ] L2 (Urgent)  [ ] L3 (Routine)  [ ] L4 (Self-care)`\n")
            out.write("  - Agreement with Developer Level: `[ ] Yes  [ ] No`\n")
            out.write("  - Clinical Red Flags / Under-Triage Risk: `[ ] None  [ ] Critical Risk (Explain below)`\n")
            out.write("  - Clinician Rationale / Action Plan: __________________________________________\n")
            out.write("  - Reviewer Initials: ________  Date: ____________\n\n")

        out.write("---\n\n")
        out.write("## Section 3: Clinician Sign-Off & Cohen's Kappa Computation\n\n")
        out.write("| Metric | Developer vs Clinician 1 | Developer vs Clinician 2 | Inter-Clinician (C1 vs C2) |\n")
        out.write("| :--- | :--- | :--- | :--- |\n")
        out.write("| Observed Agreement ($P_o$) | _______ % | _______ % | _______ % |\n")
        out.write("| Expected Agreement ($P_e$) | _______ % | _______ % | _______ % |\n")
        out.write("| Cohen's Kappa ($\\kappa$) | _______ | _______ | _______ |\n")
        out.write("| Safety Violations Flagged | _______ | _______ | _______ |\n\n")
        out.write("### Reviewer Attestation\n\n")
        out.write("- Lead Clinician Reviewer: _____________________________ (MD / Specialty: ___________________)\n")
        out.write("- Signature: _________________________________________ Date: __________________\n")
        out.write("- Secondary Clinician Reviewer: _______________________ (MD / Specialty: ___________________)\n")
        out.write("- Signature: _________________________________________ Date: __________________\n")

    print(f"Wrote docs/clinician_review_form.md with {len(rules)} rules and {len(sampled_cases)} cases.")

if __name__ == "__main__":
    main()
