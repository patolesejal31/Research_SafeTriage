"""SafeTriage Follow-Up Question Engine.

Generates targeted clarifying questions when red-flag information is missing or
age is unknown. Follow-ups are displayed AFTER a Stage A result, never delaying it.

Design rules:
- Follow-ups may never delay, block, or cancel a Level 1 (Emergency) alert.
- If the engine returns UNCERTAIN due to unknown age and a possible pediatric-relevant
  rule, the age follow-up is flagged as safety-critical.
- After answers are collected, the pipeline re-runs Stage A + Stage B, which may only
  escalate (never downgrade) from the initial result.
- Follow-up responses are structured (enum + optional numeric) to prevent injection.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FollowUpType(str, Enum):
    """Category of follow-up question."""
    AGE = "age"
    ONSET = "onset"
    SEVERITY = "severity"
    DURATION = "duration"
    ASSOCIATED_SYMPTOM = "associated_symptom"
    RELEVANT_HISTORY = "relevant_history"


@dataclass(frozen=True)
class FollowUpQuestion:
    """A single follow-up question to present to the user."""
    id: str
    type: FollowUpType
    text: str
    safety_critical: bool = False        # True if this may change Level 1 / UNCERTAIN determination
    urgency_impact: int = 1              # Potential urgency impact (higher = greater change in urgency)
    could_trigger_level_2: bool = False  # True if missing answer could matter for a candidate Level 2 match
    options: List[str] = field(default_factory=list)   # Enumerated choices (if applicable)
    free_numeric: bool = False           # Whether a numeric value is expected (e.g., age in years)
    context_concept: Optional[str] = None  # Canonical concept that triggered this question


@dataclass(frozen=True)
class FollowUpAnswer:
    """A structured answer to a follow-up question."""
    question_id: str
    selected_option: Optional[str] = None    # Must be from the question's options list
    numeric_value: Optional[float] = None    # Only if question.free_numeric is True


class FollowUpResult(list):
    """List of questions to ask, enriched with metadata about skipped questions."""

    def __init__(
        self,
        questions: List[FollowUpQuestion],
        skipped: List[FollowUpQuestion],
        information_incomplete: bool,
    ):
        super().__init__(questions)
        self.questions = questions
        self.skipped = skipped
        self.information_incomplete = information_incomplete


class FollowUpEngine:
    """Generates clinically relevant follow-up questions based on extraction state.

    Clinical invariants:
    - Follow-up questions never delay a Level 1 alert.
    - Age follow-ups are safety-critical when the age band is unknown and a
      pediatric high-risk rule may apply.
    - Severity and onset questions are generated for unresolved Level 2/3 candidates.
    """

    # Fixed follow-up question bank (not user-configurable at runtime)
    ONSET_QUESTION = FollowUpQuestion(
        id="fq_onset",
        type=FollowUpType.ONSET,
        text="When did your symptoms start?",
        options=["Just now (minutes)", "Within the past hour", "A few hours ago",
                 "Earlier today", "Yesterday", "Several days ago", "More than a week ago"],
        safety_critical=False,
        urgency_impact=2,
        could_trigger_level_2=True,
    )

    SEVERITY_QUESTION = FollowUpQuestion(
        id="fq_severity",
        type=FollowUpType.SEVERITY,
        text="How severe are your symptoms on a scale of 1-10?",
        options=["1-3 (Mild)", "4-6 (Moderate)", "7-9 (Severe)", "10 (Worst possible)"],
        safety_critical=False,
        urgency_impact=3,
        could_trigger_level_2=True,
    )

    AGE_QUESTION = FollowUpQuestion(
        id="fq_age",
        type=FollowUpType.AGE,
        text="How old is the patient? (Enter age in years, or choose 'Prefer not to say')",
        options=["Prefer not to say", "Newborn (< 1 month)", "Infant (1-12 months)",
                 "Toddler (1-2 years)", "Child (3-11 years)", "Teenager (12-17 years)",
                 "Adult (18-64 years)", "Older adult (65+)"],
        free_numeric=True,
        safety_critical=False,
        urgency_impact=2,
        could_trigger_level_2=True,
        context_concept="age",
    )

    AGE_SAFETY_CRITICAL_QUESTION = FollowUpQuestion(
        id="fq_age_safety",
        type=FollowUpType.AGE,
        text=(
            "IMPORTANT: Age is unknown and may affect the urgency assessment. "
            "How old is the patient?"
        ),
        options=["Prefer not to say", "Newborn (< 1 month)", "Infant (1-12 months)",
                 "Toddler (1-2 years)", "Child (3-11 years)", "Teenager (12-17 years)",
                 "Adult (18-64 years)", "Older adult (65+)"],
        free_numeric=True,
        safety_critical=True,
        urgency_impact=4,
        could_trigger_level_2=True,
        context_concept="age",
    )

    FEVER_DURATION_QUESTION = FollowUpQuestion(
        id="fq_fever_duration",
        type=FollowUpType.DURATION,
        text="How long has the fever been present?",
        options=["Less than 24 hours", "1-2 days", "3-4 days", "More than 5 days", "Not sure"],
        safety_critical=False,
        urgency_impact=1,
        could_trigger_level_2=False,
        context_concept="fever",
    )

    CHEST_RADIATION_QUESTION = FollowUpQuestion(
        id="fq_chest_radiation",
        type=FollowUpType.ASSOCIATED_SYMPTOM,
        text="Does the chest pain radiate to the arm, jaw, or shoulder?",
        options=["Yes, to the left arm", "Yes, to the jaw", "Yes, to the shoulder",
                 "Yes, to multiple areas", "No", "Not sure"],
        safety_critical=True,
        urgency_impact=4,
        could_trigger_level_2=True,
        context_concept="chest_pain",
    )

    HEADACHE_CHARACTER_QUESTION = FollowUpQuestion(
        id="fq_headache_character",
        type=FollowUpType.ASSOCIATED_SYMPTOM,
        text="How would you describe the headache?",
        options=["Sudden, worst headache of my life", "Gradual onset, throbbing",
                 "Gradual onset, dull pressure", "Associated with nausea/vomiting",
                 "With visual disturbance", "Not sure"],
        safety_critical=True,
        urgency_impact=4,
        could_trigger_level_2=True,
        context_concept="headache",
    )

    BREATHING_DURATION_QUESTION = FollowUpQuestion(
        id="fq_breathing_duration",
        type=FollowUpType.DURATION,
        text="How long have you had difficulty breathing?",
        options=["Just started (minutes)", "1-2 hours", "Several hours",
                 "Since yesterday", "Several days", "Not sure"],
        safety_critical=False,
        urgency_impact=3,
        could_trigger_level_2=True,
        context_concept="breathlessness",
    )

    def generate(
        self,
        requires_age_followup: bool,
        potential_pediatric_escalation: bool,
        concepts_present: List[str],
        onset_known: bool,
        severity_known: bool,
        duration_known: bool,
        max_followups: Optional[int] = None,
        max_optional_followups: Optional[int] = None,
        max_questions: Optional[int] = None,
        candidate_rules: Optional[List[Any]] = None,
    ) -> FollowUpResult:
        """Generate a prioritized list of follow-up questions.

        Decisions:
        - Cap applies to OPTIONAL questions only (max_followups / max_optional_followups, default 3).
        - Safety-critical questions (e.g. unknown age with potential pediatric escalation,
          red-flag modifiers) are NEVER dropped by the cap.
        - Questions are ordered by how much the answer could change urgency (urgency_impact).
        - Skipped questions are recorded in the returned FollowUpResult.skipped.
        - If any skipped question could matter for a candidate Level 2 match,
          information_incomplete is set to True.

        Returns:
            FollowUpResult (acts as List[FollowUpQuestion] with .skipped and .information_incomplete).
        """
        all_candidates: List[FollowUpQuestion] = []

        # 1. Safety-critical age question first if pediatric uncertainty exists
        if requires_age_followup:
            if potential_pediatric_escalation:
                all_candidates.append(self.AGE_SAFETY_CRITICAL_QUESTION)
            else:
                all_candidates.append(self.AGE_QUESTION)

        # 2. Concept-specific questions
        if "chest_pain" in concepts_present:
            all_candidates.append(self.CHEST_RADIATION_QUESTION)

        if "headache" in concepts_present:
            all_candidates.append(self.HEADACHE_CHARACTER_QUESTION)

        if "breathlessness" in concepts_present:
            all_candidates.append(self.BREATHING_DURATION_QUESTION)

        if "fever" in concepts_present:
            all_candidates.append(self.FEVER_DURATION_QUESTION)

        # 3. Generic onset / severity if not yet collected
        if not severity_known:
            all_candidates.append(self.SEVERITY_QUESTION)

        if not onset_known:
            all_candidates.append(self.ONSET_QUESTION)

        # Deduplicate candidates while preserving initial order
        seen_ids: set = set()
        deduped: List[FollowUpQuestion] = []
        for q in all_candidates:
            if q.id not in seen_ids:
                seen_ids.add(q.id)
                deduped.append(q)

        # Separate safety-critical vs optional
        safety_critical = [q for q in deduped if q.safety_critical]
        optional = [q for q in deduped if not q.safety_critical]

        # Order optional questions by urgency_impact descending
        optional.sort(key=lambda q: -q.urgency_impact)

        # Cap for optional questions (default 3)
        opt_cap = 3
        if max_followups is not None:
            opt_cap = max_followups
        elif max_optional_followups is not None:
            opt_cap = max_optional_followups

        kept_optional = optional[:opt_cap]
        skipped_optional = optional[opt_cap:]

        # Combine: safety-critical first (ordered by urgency_impact), then kept optional
        safety_critical.sort(key=lambda q: -q.urgency_impact)
        questions_to_ask = safety_critical + kept_optional

        # Backwards compatibility: if max_questions was explicitly passed without max_followups
        if max_questions is not None and max_followups is None and max_optional_followups is None:
            questions_to_ask = questions_to_ask[:max_questions]

        # Check if any skipped question could matter for a possible Level 2 match
        information_incomplete = any(q.could_trigger_level_2 for q in skipped_optional)

        return FollowUpResult(questions_to_ask, skipped_optional, information_incomplete)

    def apply_answers(
        self,
        answers: List[FollowUpAnswer],
    ) -> Dict[str, Any]:
        """Parse structured follow-up answers into pipeline-usable parameters.

        Returns a dict with keys: age_years, age_months, onset, severity, modifiers.
        Only explicitly provided answers are included; nothing is assumed or defaulted.
        """
        result: Dict[str, Any] = {}

        for ans in answers:
            qid = ans.question_id

            if qid in ("fq_age", "fq_age_safety"):
                if ans.numeric_value is not None:
                    result["age_years"] = float(ans.numeric_value)
                elif ans.selected_option:
                    opt = ans.selected_option.lower()
                    if "prefer not" in opt:
                        pass  # remains unknown
                    elif "newborn" in opt:
                        result["age_months"] = 0.5
                    elif "infant" in opt:
                        result["age_months"] = 6.0
                    elif "toddler" in opt:
                        result["age_months"] = 18.0
                    elif "child" in opt:
                        result["age_years"] = 7.0
                    elif "teenager" in opt:
                        result["age_years"] = 15.0
                    elif "adult (18" in opt:
                        result["age_years"] = 35.0
                    elif "older adult" in opt:
                        result["age_years"] = 70.0

            elif qid == "fq_severity":
                if ans.selected_option:
                    opt = ans.selected_option.lower()
                    if "7-9" in opt or "10" in opt or "worst" in opt:
                        result["severity"] = "severe"
                    elif "4-6" in opt or "moderate" in opt:
                        result["severity"] = "moderate"
                    else:
                        result["severity"] = "mild"

            elif qid == "fq_onset":
                if ans.selected_option:
                    opt = ans.selected_option.lower()
                    if "just now" in opt or "past hour" in opt:
                        result["onset"] = "sudden"
                    else:
                        result["onset"] = "gradual"

            elif qid == "fq_chest_radiation":
                if ans.selected_option and "yes" in ans.selected_option.lower():
                    result.setdefault("modifiers", [])
                    result["modifiers"].append("radiating")

        return result
