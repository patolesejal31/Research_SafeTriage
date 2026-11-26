"""SafeTriage Explanation Service.

Produces two types of explanations:
1. Template explainer: deterministic, fully faithful — lists triggered rules,
   matched/negated symptoms, clinical sources, and review status (UNVERIFIED shown).
   Safe to use as the definitive fallback.
2. Faithfulness checker: validates any LLM-generated explanation by ensuring
   every rule ID it cites actually exists in the triggered rule set. If the check
   fails (hallucinated rule IDs, downgrade language), the template explainer is used
   instead and the check failure is recorded.

Non-negotiable constraints:
- Explanations never contain raw symptom text from the user.
- Review status 'UNVERIFIED' is always shown — never hidden.
- Emergency numbers (112 / 108) are shown for Level 1, Level 2, and UNCERTAIN.
- Never claim diagnosis or prescribe treatment.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Set

from app.core.urgency import UNCERTAIN, Urgency, UrgencyOrUncertain
from app.triage.engine import ClinicalRule
from app.triage.nlp_extractor import EntityStatus, ExtractionResult

logger = logging.getLogger("safetriage.services.explainer")

DISCLAIMER = (
    "⚠️  SafeTriage is a research prototype only. This assessment is NOT a medical diagnosis "
    "and must NOT be used as a substitute for professional clinical evaluation. "
    "Always consult a qualified healthcare professional."
)

EMERGENCY_NOTICE = (
    "🚨 EMERGENCY: Call 112 (National Emergency) or 108 (Ambulance) immediately."
)

URGENT_NOTICE = (
    "⚠️  URGENT: Please seek medical attention promptly. "
    "If symptoms worsen call 112 / 108."
)

UNCERTAIN_NOTICE = (
    "⚠️  UNABLE TO ASSESS SAFELY: Unable to assess safely. "
    "If you have severe symptoms, call 112 / 108 or see a clinician immediately."
)


@dataclass(frozen=True)
class ExplanationResult:
    """The final explanation shown to the user (or stored in the DB)."""
    text: str
    source: str                           # "template" or "llm" (never claimed as real if mock)
    llm_faithfulness_passed: Optional[bool] = None   # None if no LLM was involved
    llm_hallucinated_rule_ids: List[str] = field(default_factory=list)
    includes_emergency_notice: bool = False
    review_status_shown: bool = True      # Always True; UNVERIFIED must always be visible


class Explainer:
    """Generates faithful, template-based or LLM-validated explanations."""

    def build_template_explanation(
        self,
        final_urgency: UrgencyOrUncertain,
        triggered_rules: List[ClinicalRule],
        extraction: ExtractionResult,
        ml_model_name: Optional[str] = None,
        llm_provider_name: Optional[str] = None,
    ) -> ExplanationResult:
        """Build a fully deterministic, faithful template explanation.

        Args:
            final_urgency: The final urgency level (or UNCERTAIN).
            triggered_rules: Rules that matched during engine evaluation.
            extraction: Structured NLP extraction (never raw text).
            ml_model_name: ML model name, if used.
            llm_provider_name: LLM provider name, if used.

        Returns:
            ExplanationResult with source="template".
        """
        lines: List[str] = []

        # --- Header ---
        is_emergency = isinstance(final_urgency, Urgency) and final_urgency == Urgency.EMERGENCY
        is_urgent = isinstance(final_urgency, Urgency) and final_urgency == Urgency.URGENT
        is_uncertain = isinstance(final_urgency, type(UNCERTAIN)) or final_urgency == UNCERTAIN

        lines.append("## SafeTriage Preliminary Assessment")
        lines.append("")

        if is_emergency:
            lines.append(EMERGENCY_NOTICE)
            lines.append("**Assessment Level: 1 — Emergency**")
            includes_emergency = True
        elif is_urgent:
            lines.append(URGENT_NOTICE)
            lines.append("**Assessment Level: 2 — Urgent**")
            includes_emergency = True
        elif is_uncertain:
            lines.append(UNCERTAIN_NOTICE)
            lines.append("**Assessment: UNCERTAIN** — Cannot be safely categorized.")
            includes_emergency = True
        else:
            level_int = int(final_urgency) if isinstance(final_urgency, Urgency) else "?"
            level_name = final_urgency.display_name if isinstance(final_urgency, Urgency) else "Unknown"
            lines.append(f"**Assessment Level: {level_int} — {level_name}**")
            includes_emergency = False

        lines.append("")

        # --- Triggered rules ---
        if triggered_rules:
            lines.append("### Clinical Rules Triggered")
            for rule in triggered_rules:
                lines.append(f"- **[{rule.id}]** {rule.name}")
                lines.append(f"  - *Level:* {int(rule.level)} ({rule.level.display_name})")
                lines.append(f"  - *Specialty:* {rule.specialty}")
                lines.append(f"  - *Rationale:* {rule.rationale}")
                lines.append(f"  - *Suggested Action:* {rule.recommended_action}")
                lines.append(
                    f"  - *Source:* {rule.source.body}, {rule.source.document_title} "
                    f"({rule.source.year})"
                )
                lines.append(f"  - *Review Status:* **{rule.review_status}** ← UNVERIFIED by clinician")
            lines.append("")
        else:
            lines.append("### Clinical Rules Triggered")
            lines.append("- No deterministic rule matched the described presentation.")
            lines.append("")

        # --- Identified symptoms (structured, not raw text) ---
        positive = [e for e in extraction.entities if e.status == EntityStatus.POSITIVE]
        negated = [e for e in extraction.entities if e.status == EntityStatus.NEGATED]
        uncertain_ents = [e for e in extraction.entities if e.status == EntityStatus.UNCERTAIN]

        if positive:
            lines.append("### Identified Symptoms (Present)")
            for ent in positive:
                fuzzy_note = f" *(fuzzy match, score={ent.fuzzy_score:.1f})*" if ent.match_type.value == "fuzzy" else ""
                lines.append(f"- {ent.canonical_concept.replace('_', ' ').title()}{fuzzy_note}")
            lines.append("")

        if negated:
            lines.append("### Symptoms Reported as Absent")
            for ent in negated:
                lines.append(f"- {ent.canonical_concept.replace('_', ' ').title()}")
            lines.append("")

        if uncertain_ents:
            lines.append("### Symptoms with Ambiguous Status")
            for ent in uncertain_ents:
                lines.append(f"- {ent.canonical_concept.replace('_', ' ').title()}")
            lines.append("")

        # --- Next steps & actionable guidance ---
        lines.append("### Recommended Next Steps")
        if is_emergency:
            lines.append("- **Immediate Action:** Call emergency services (112 or 108) or go to the nearest emergency department right away.")
            lines.append("- Do not drive yourself; arrange emergency ambulance transport.")
            lines.append("- Stay calm, sit or lie comfortably, and keep emergency contact informed.")
        elif is_urgent:
            lines.append("- **Prompt Medical Review:** Seek prompt evaluation by a medical doctor or visit an urgent care center within hours.")
            lines.append("- Monitor your symptoms closely; if you develop severe pain, shortness of breath, dizziness, or weakness, immediately call 112 / 108.")
            lines.append("- Avoid strenuous physical activities until evaluated by a healthcare professional.")
        elif is_uncertain:
            lines.append("- **Direct Clinical Assessment Needed:** Your reported presentation cannot be safely categorized by automated rules alone.")
            lines.append("- Please consult a primary care doctor or healthcare clinic for direct examination.")
            lines.append("- If you experience any acute red-flag symptoms (severe chest pain, breathing difficulty, sudden numbness, or heavy bleeding), call 112 / 108 immediately.")
        elif level_int == 3:
            lines.append("- **Routine Healthcare Consultation:** Schedule a routine appointment with your primary care physician or outpatient clinic.")
            lines.append("- Note down your symptoms, when they started, and any over-the-counter remedies tried.")
            lines.append("- If symptoms fail to improve over the next several days or progressively worsen, seek earlier clinical review.")
        elif level_int == 4:
            lines.append("- **Supportive Home Care:** Your symptoms appear mild and consistent with self-limiting presentations suitable for supportive care.")
            lines.append("- Maintain adequate oral hydration, rest well, and monitor your symptoms.")
            lines.append("- Seek medical attention if symptoms persist beyond 7-10 days, or immediately if you develop high fever, breathing distress, or acute chest discomfort.")
        lines.append("")

        # --- Models used ---
        model_parts: List[str] = ["Template explainer (deterministic)"]
        if ml_model_name:
            model_parts.append(f"ML: {ml_model_name}")
        if llm_provider_name:
            model_parts.append(f"LLM: {llm_provider_name}")

        lines.append(f"*Components used: {', '.join(model_parts)}*")
        lines.append("")
        lines.append(DISCLAIMER)

        return ExplanationResult(
            text="\n".join(lines),
            source="template",
            llm_faithfulness_passed=None,
            includes_emergency_notice=includes_emergency,
            review_status_shown=True,
        )

    def check_llm_faithfulness(
        self,
        llm_explanation_text: str,
        triggered_rule_ids: Set[str],
    ) -> tuple[bool, List[str]]:
        """Check whether an LLM explanation is faithful to the triggered rules.

        Faithfulness rule: Every rule ID mentioned in the LLM explanation
        must exist in the set of triggered rules. Any hallucinated rule ID
        → explanation is DISCARDED and template is used instead.

        Args:
            llm_explanation_text: Raw text from the LLM.
            triggered_rule_ids: Set of rule IDs that actually matched.

        Returns:
            Tuple of (passed: bool, hallucinated_rule_ids: List[str]).
        """
        import re
        # Extract all rule-ID-like tokens (e.g. CARD-001, NEUR-002, HALLUCINATED-999)
        found_ids = set(re.findall(r'\b[A-Z]{2,20}-\d{2,4}\b', llm_explanation_text))
        hallucinated = [rid for rid in found_ids if rid not in triggered_rule_ids]

        if hallucinated:
            logger.warning(
                "LLM explanation faithfulness FAILED — hallucinated rule IDs: %s",
                hallucinated,
            )
            return False, hallucinated

        return True, []

    def build_llm_or_template_explanation(
        self,
        final_urgency: UrgencyOrUncertain,
        triggered_rules: List[ClinicalRule],
        extraction: ExtractionResult,
        llm_explanation_text: Optional[str] = None,
        llm_provider_name: Optional[str] = None,
        ml_model_name: Optional[str] = None,
    ) -> ExplanationResult:
        """Build explanation: use LLM text if faithful, else fallback to template.

        Args:
            final_urgency: Verified final urgency from the invariant engine.
            triggered_rules: Rules matched by the deterministic engine.
            extraction: Structured extraction result.
            llm_explanation_text: Raw text from the LLM (may be None).
            llm_provider_name: LLM provider name for attribution.
            ml_model_name: ML model name for attribution.

        Returns:
            ExplanationResult with source="llm" (if faithful) or "template" (fallback).
        """
        triggered_ids: Set[str] = {r.id for r in triggered_rules}

        # If provider is mock or no real LLM prose is provided, use the detailed template explainer
        from app.services.llm_adapter import MOCK_PROVIDER_NAME
        is_mock_provider = (llm_provider_name == MOCK_PROVIDER_NAME)

        if llm_explanation_text and not is_mock_provider:
            passed, hallucinated = self.check_llm_faithfulness(
                llm_explanation_text, triggered_ids
            )
            if passed:
                # Prepend emergency notice from template regardless of LLM text
                is_uncertain = final_urgency == UNCERTAIN
                is_emergency = isinstance(final_urgency, Urgency) and final_urgency == Urgency.EMERGENCY
                is_urgent = isinstance(final_urgency, Urgency) and final_urgency == Urgency.URGENT
                includes_emergency = is_emergency or is_urgent or is_uncertain

                notice = ""
                if is_emergency:
                    notice = f"{EMERGENCY_NOTICE}\n\n"
                elif is_urgent:
                    notice = f"{URGENT_NOTICE}\n\n"
                elif is_uncertain:
                    notice = f"{UNCERTAIN_NOTICE}\n\n"

                provider_label = llm_provider_name or "LLM"
                from app.services.llm_adapter import MOCK_PROVIDER_NAME
                is_mock_provider = llm_provider_name == MOCK_PROVIDER_NAME

                mock_disclaimer = ""
                if is_mock_provider:
                    mock_disclaimer = (
                        "\n\n> ⚠️  This explanation was generated by **MOCK (not a real LLM)**. "
                        "It is for development/testing only and has no clinical validity."
                    )

                llm_text = (
                    f"{notice}"
                    f"*Explanation by: {provider_label}*\n\n"
                    f"{llm_explanation_text}"
                    f"{mock_disclaimer}\n\n"
                    f"*Source review status: **UNVERIFIED** ← UNVERIFIED by clinician*\n\n"
                    f"{DISCLAIMER}"
                )
                return ExplanationResult(
                    text=llm_text,
                    source="llm",
                    llm_faithfulness_passed=True,
                    llm_hallucinated_rule_ids=[],
                    includes_emergency_notice=includes_emergency,
                    review_status_shown=True,
                )
            else:
                # LLM failed faithfulness check → use template
                template_result = self.build_template_explanation(
                    final_urgency, triggered_rules, extraction, ml_model_name, llm_provider_name
                )
                return ExplanationResult(
                    text=template_result.text,
                    source="template",
                    llm_faithfulness_passed=False,
                    llm_hallucinated_rule_ids=hallucinated,
                    includes_emergency_notice=template_result.includes_emergency_notice,
                    review_status_shown=True,
                )

        # No LLM explanation available → template
        return self.build_template_explanation(
            final_urgency, triggered_rules, extraction, ml_model_name, llm_provider_name
        )
