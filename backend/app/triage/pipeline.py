"""SafeTriage Two-Stage Triage Pipeline.

Implements the emergency-first two-stage pipeline:

Stage A (synchronous, fast, no model dependence):
  sanitize -> NLP extraction -> raw-keyword safety net -> Level 1 rules
  If Level 1 matches → return emergency alert IMMEDIATELY.
  Stage A NEVER depends on ML or LLM availability.
  Stage A failure → UNCERTAIN (never a silent default level).

Stage B (optional, may run after Stage A):
  follow-up questions, ML baseline, LLM adapter, explainer.
  Stage B may ONLY ESCALATE. A Stage B timeout or failure must never
  delay, block, or cancel a Stage A alert.
  Stage B adds its results to the AssessmentResult; it does not modify Stage A output.

Standalone predictors (for Phase 7 independent baseline evaluation):
  predict_rule_only() – runs Stage A only, no ML/LLM.
  predict_ml_only()   – runs ML on extraction without rules.
  predict_llm_only()  – runs LLM on extraction without rules.

Non-negotiable invariants enforced here:
- Level 1 from Stage A is returned before Stage B begins.
- Stage B timeout/failure never blocks or cancels Stage A result.
- ML and LLM may only escalate; invariant enforces this.
- UNCERTAIN is never displayed as Level 3 or Level 4.
- Emergency numbers 112 / 108 shown for Level 1, Level 2, UNCERTAIN.
- No raw symptom text in audit logs or model inputs.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, List, Optional

from app.core.urgency import UNCERTAIN, Urgency, UrgencyOrUncertain
from app.services.explainer import ExplanationResult, Explainer
from app.services.llm_adapter import LLMProvider, MockProvider
from app.services.ml_baseline import MLBaseline, MLPrediction
from app.triage.engine import RuleEngine, RuleEngineResult
from app.triage.followups import FollowUpAnswer, FollowUpEngine, FollowUpQuestion
from app.triage.invariant import (
    ComponentResult,
    ComponentStatus,
    ComponentType,
    InvariantResult,
    enforce_invariant,
)
from app.triage.nlp_extractor import (
    EntityStatus,
    ExtractionResult,
    ExtractedAttributes,
    NLPExtractor,
)
from app.triage.safety_net import SafetyNet, SafetyNetResult

logger = logging.getLogger("safetriage.triage.pipeline")


@dataclass(frozen=True)
class StageAResult:
    """Immediate output from Stage A (synchronous, emergency-first)."""
    final_urgency: UrgencyOrUncertain
    is_level_1_emergency: bool
    safety_net_triggered: bool
    safety_net_result: Optional[SafetyNetResult]
    rule_engine_result: Optional[RuleEngineResult]
    extraction: Optional[ExtractionResult]
    invariant_result: InvariantResult
    stage_a_complete: bool = True
    # Follow-up questions to show AFTER displaying Stage A result
    followup_questions: List[FollowUpQuestion] = field(default_factory=list)
    skipped_followup_questions: List[FollowUpQuestion] = field(default_factory=list)
    information_incomplete: bool = False


@dataclass(frozen=True)
class AssessmentResult:
    """Complete assessment combining Stage A + Stage B."""
    # Stage A fields (always present)
    final_urgency: UrgencyOrUncertain
    is_level_1_emergency: bool
    is_uncertain: bool
    stage_a: StageAResult

    # Stage B fields (may be absent if Stage B was disabled or failed)
    invariant_result: InvariantResult           # Final invariant (may differ from Stage A if escalated)
    ml_prediction: Optional[MLPrediction]
    llm_component_result: Optional[ComponentResult]
    explanation: Optional[ExplanationResult]
    followup_questions: List[FollowUpQuestion] = field(default_factory=list)
    skipped_followup_questions: List[FollowUpQuestion] = field(default_factory=list)
    information_incomplete: bool = False

    # Status flags (each is a distinct field, as required by spec)
    rule_status: ComponentStatus = ComponentStatus.UNAVAILABLE
    ml_status: ComponentStatus = ComponentStatus.UNAVAILABLE
    llm_status: ComponentStatus = ComponentStatus.UNAVAILABLE

    # Mock label: if MockProvider was used, this is "MOCK (not a real LLM)"
    llm_provider_label: Optional[str] = None


class TriagePipeline:
    """Two-stage triage coordinator (Stage A: emergency-first; Stage B: optional enrichment).

    Usage:
        pipeline = TriagePipeline()
        # For a text input:
        result = pipeline.assess(text, age_years=35)
        # result.stage_a.final_urgency is available immediately
        # result.explanation, result.ml_prediction are from Stage B
    """

    def __init__(
        self,
        nlp_extractor: Optional[NLPExtractor] = None,
        safety_net: Optional[SafetyNet] = None,
        rule_engine: Optional[RuleEngine] = None,
        ml_baseline: Optional[MLBaseline] = None,
        llm_provider: Optional[LLMProvider] = None,
        followup_engine: Optional[FollowUpEngine] = None,
        explainer: Optional[Explainer] = None,
        llm_timeout_seconds: float = 10.0,
        ml_timeout_seconds: float = 5.0,
        enable_ml: bool = True,
        enable_llm: bool = True,
        max_optional_followups: int = 3,
    ):
        self.extractor = nlp_extractor or NLPExtractor()
        self.safety_net = safety_net or SafetyNet()
        self.engine = rule_engine or RuleEngine()
        self.ml = ml_baseline or MLBaseline()
        self.llm = llm_provider or MockProvider()
        self.followup_engine = followup_engine or FollowUpEngine()
        self.explainer_svc = explainer or Explainer()
        self.llm_timeout = llm_timeout_seconds
        self.ml_timeout = ml_timeout_seconds
        self.enable_ml = enable_ml
        self.enable_llm = enable_llm
        self.max_optional_followups = max_optional_followups

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_stage_a(
        self,
        text: str,
        age_years: Optional[float] = None,
        age_months: Optional[float] = None,
        age_days: Optional[float] = None,
        age_text: Optional[str] = None,
        assessment_id: Optional[str] = None,
    ) -> StageAResult:
        """Execute Stage A: sanitize → extract → safety net → Level 1 rules.

        Returns immediately with Level 1 if matched.
        Never depends on ML or LLM availability.
        Exceptions inside Stage A are caught and surfaced as UNCERTAIN.
        """
        try:
            return self._run_stage_a_internal(
                text, age_years=age_years, age_months=age_months,
                age_days=age_days, age_text=age_text,
                assessment_id=assessment_id,
            )
        except Exception:
            logger.exception("Stage A encountered unhandled failure — returning UNCERTAIN")
            uncertain_invariant = enforce_invariant(assessment_id=assessment_id)
            return StageAResult(
                final_urgency=UNCERTAIN,
                is_level_1_emergency=False,
                safety_net_triggered=False,
                safety_net_result=None,
                rule_engine_result=None,
                extraction=None,
                invariant_result=uncertain_invariant,
                followup_questions=[],
            )

    def run_stage_b(
        self,
        stage_a: StageAResult,
        assessment_id: Optional[str] = None,
    ) -> AssessmentResult:
        """Execute Stage B: ML, LLM, explainer.

        Stage B may only escalate. Any Stage B failure keeps the Stage A result.
        Never raises; always returns a complete AssessmentResult.
        """
        try:
            return self._run_stage_b_internal(stage_a, assessment_id=assessment_id)
        except Exception:
            logger.exception("Stage B failed — keeping Stage A result")
            return self._stage_b_fallback(stage_a, assessment_id)

    def assess(
        self,
        text: str,
        age_years: Optional[float] = None,
        age_months: Optional[float] = None,
        age_days: Optional[float] = None,
        age_text: Optional[str] = None,
        assessment_id: Optional[str] = None,
    ) -> AssessmentResult:
        """Full pipeline: Stage A then Stage B.

        Stage A result is determined first (synchronous).
        Stage B enriches it without blocking or cancelling Stage A output.
        """
        stage_a = self.run_stage_a(
            text,
            age_years=age_years,
            age_months=age_months,
            age_days=age_days,
            age_text=age_text,
            assessment_id=assessment_id,
        )
        return self.run_stage_b(stage_a, assessment_id=assessment_id)

    def reassess_with_followup_answers(
        self,
        original_text: str,
        answers: List[FollowUpAnswer],
        assessment_id: Optional[str] = None,
    ) -> AssessmentResult:
        """Re-run the full pipeline after follow-up answers are collected.

        Answers may only escalate from the original result — never downgrade.
        The original text is re-extracted with updated age/severity context from answers.
        """
        extra_params = self.followup_engine.apply_answers(answers)
        return self.assess(
            original_text,
            age_years=extra_params.get("age_years"),
            age_months=extra_params.get("age_months"),
            assessment_id=assessment_id,
        )

    # ------------------------------------------------------------------
    # Standalone predictors for Phase 7 independent baseline evaluation
    # ------------------------------------------------------------------

    def predict_rule_only(
        self,
        text: str,
        age_years: Optional[float] = None,
        age_months: Optional[float] = None,
        age_days: Optional[float] = None,
        age_text: Optional[str] = None,
    ) -> InvariantResult:
        """Stage A only. No ML, no LLM. For independent rule-engine baseline evaluation."""
        try:
            extraction = self.extractor.extract(text)
            rule_result = self.engine.evaluate(
                extraction, age_years=age_years, age_months=age_months,
                age_days=age_days, age_text=age_text,
            )
            return enforce_invariant(rule_result=rule_result.component_result)
        except Exception:
            logger.exception("predict_rule_only failed")
            return enforce_invariant()

    def predict_ml_only(self, text: str) -> InvariantResult:
        """ML baseline only. No rules, no LLM. For independent ML baseline evaluation."""
        try:
            extraction = self.extractor.extract(text)
            ml_pred = self.ml.predict(extraction)
            return enforce_invariant(ml_result=ml_pred.component_result)
        except Exception:
            logger.exception("predict_ml_only failed")
            return enforce_invariant()

    def predict_llm_only(self, text: str) -> InvariantResult:
        """LLM only. No rules, no ML. For independent LLM baseline evaluation."""
        try:
            extraction = self.extractor.extract(text)
            llm_result = self.llm.predict(extraction, timeout_seconds=self.llm_timeout)
            return enforce_invariant(llm_result=llm_result)
        except Exception:
            logger.exception("predict_llm_only failed")
            return enforce_invariant()

    # ------------------------------------------------------------------
    # Internal Stage A
    # ------------------------------------------------------------------

    def _run_stage_a_internal(
        self,
        text: str,
        age_years: Optional[float],
        age_months: Optional[float],
        age_days: Optional[float],
        age_text: Optional[str],
        assessment_id: Optional[str],
    ) -> StageAResult:
        # 1. NLP extraction (sanitization happens inside NLPExtractor)
        extraction = self.extractor.extract(text)

        # 2. Raw-keyword safety net (runs even if NLP fails or mislabels)
        safety_net_result = self.safety_net.evaluate(
            text,
            extracted_entities=extraction.entities if extraction else [],
        )

        # 3. If safety net triggered → immediate Level 1, return NOW
        if safety_net_result.triggered:
            rule_component = ComponentResult(
                component=ComponentType.RULE,
                status=ComponentStatus.OK,
                level=Urgency.EMERGENCY,
            )
            invariant = enforce_invariant(
                rule_result=rule_component,
                assessment_id=assessment_id,
            )
            # Follow-up questions still generated but shown AFTER the alert
            followups = self._generate_followups(
                rule_eng_result=None,
                extraction=extraction,
            )
            skipped_fqs = getattr(followups, "skipped", [])
            info_incomplete = getattr(followups, "information_incomplete", False)
            return StageAResult(
                final_urgency=Urgency.EMERGENCY,
                is_level_1_emergency=True,
                safety_net_triggered=True,
                safety_net_result=safety_net_result,
                rule_engine_result=None,
                extraction=extraction,
                invariant_result=invariant,
                followup_questions=list(followups),
                skipped_followup_questions=skipped_fqs,
                information_incomplete=info_incomplete,
            )

        # 4. Run the deterministic rule engine
        rule_result = self.engine.evaluate(
            extraction,
            age_years=age_years,
            age_months=age_months,
            age_days=age_days,
            age_text=age_text or extraction.attributes.age_group,
        )

        # 5. Stage A invariant (rules only, no ML/LLM yet)
        invariant = enforce_invariant(
            rule_result=rule_result.component_result,
            assessment_id=assessment_id,
        )

        is_l1 = (
            invariant.final_urgency == Urgency.EMERGENCY
            and not invariant.is_uncertain
        )

        followups = self._generate_followups(rule_eng_result=rule_result, extraction=extraction)
        skipped_fqs = getattr(followups, "skipped", [])
        info_incomplete = getattr(followups, "information_incomplete", False)

        final_urg = invariant.final_urgency
        # If a skipped question could matter for a candidate Level 2 match,
        # never settle on a lower level (Level 3 or 4).
        if info_incomplete and final_urg in (Urgency.ROUTINE, Urgency.SELF_CARE):
            final_urg = Urgency.URGENT

        return StageAResult(
            final_urgency=final_urg,
            is_level_1_emergency=is_l1,
            safety_net_triggered=False,
            safety_net_result=safety_net_result,
            rule_engine_result=rule_result,
            extraction=extraction,
            invariant_result=invariant,
            followup_questions=list(followups),
            skipped_followup_questions=skipped_fqs,
            information_incomplete=info_incomplete,
        )

    # ------------------------------------------------------------------
    # Internal Stage B
    # ------------------------------------------------------------------

    def _run_stage_b_internal(
        self,
        stage_a: StageAResult,
        assessment_id: Optional[str],
    ) -> AssessmentResult:
        extraction = stage_a.extraction
        rule_result = stage_a.rule_engine_result

        # --- ML prediction ---
        ml_pred: Optional[MLPrediction] = None
        if self.enable_ml and extraction is not None:
            try:
                ml_pred = self.ml.predict(extraction)
            except Exception:
                logger.exception("ML prediction failed in Stage B")
                ml_pred = None

        ml_component = ml_pred.component_result if ml_pred else ComponentResult(
            component=ComponentType.ML, status=ComponentStatus.UNAVAILABLE
        )

        # --- LLM prediction ---
        llm_component: Optional[ComponentResult] = None
        llm_explanation_text: Optional[str] = None
        if self.enable_llm and extraction is not None:
            try:
                llm_component = self.llm.predict(
                    extraction,
                    timeout_seconds=self.llm_timeout,
                )
                # If LLM succeeded, ask it for a prose explanation too
                if llm_component.status == ComponentStatus.OK:
                    llm_explanation_text = self._get_llm_explanation(extraction)
            except Exception:
                logger.exception("LLM prediction failed in Stage B")
                llm_component = ComponentResult(
                    component=ComponentType.LLM, status=ComponentStatus.ERROR
                )

        if llm_component is None:
            llm_component = ComponentResult(
                component=ComponentType.LLM, status=ComponentStatus.UNAVAILABLE
            )

        # --- Final invariant (Stage A rule result + Stage B ML + LLM) ---
        # Use the rule component from Stage A's invariant result, which captures both
        # the case where the rule engine ran normally AND the case where the safety net
        # generated a Level 1 emergency result directly (rule_engine_result may be None).
        stage_a_rule_status = stage_a.invariant_result.component_statuses.get(
            ComponentType.RULE, ComponentStatus.UNAVAILABLE
        )
        stage_a_rule_level = stage_a.invariant_result.audit_record.rule_level
        if stage_a_rule_level is not None and stage_a_rule_status == ComponentStatus.OK:
            rule_comp = ComponentResult(
                component=ComponentType.RULE,
                status=ComponentStatus.OK,
                level=Urgency(stage_a_rule_level),
            )
        elif rule_result is not None:
            rule_comp = rule_result.component_result
        else:
            rule_comp = ComponentResult(component=ComponentType.RULE, status=ComponentStatus.UNAVAILABLE)
        final_invariant = enforce_invariant(
            rule_result=rule_comp,
            ml_result=ml_component,
            llm_result=llm_component,
            assessment_id=assessment_id,
        )

        # --- Explanation ---
        triggered_rules = rule_result.all_matched_rules if rule_result else []
        explanation = self.explainer_svc.build_llm_or_template_explanation(
            final_urgency=final_invariant.final_urgency,
            triggered_rules=triggered_rules,
            extraction=extraction or ExtractionResult(
                sanitized_text="", entities=[], attributes=ExtractedAttributes()
            ),
            llm_explanation_text=llm_explanation_text,
            llm_provider_name=self.llm.name,
            ml_model_name=ml_pred.component_result.model_name if ml_pred else None,
        )

        final_urg = final_invariant.final_urgency
        if stage_a.information_incomplete and final_urg in (Urgency.ROUTINE, Urgency.SELF_CARE):
            final_urg = Urgency.URGENT

        return AssessmentResult(
            final_urgency=final_urg,
            is_level_1_emergency=(
                final_urg == Urgency.EMERGENCY
                and not final_invariant.is_uncertain
            ),
            is_uncertain=final_invariant.is_uncertain,
            stage_a=stage_a,
            invariant_result=final_invariant,
            ml_prediction=ml_pred,
            llm_component_result=llm_component,
            explanation=explanation,
            followup_questions=stage_a.followup_questions,
            skipped_followup_questions=stage_a.skipped_followup_questions,
            information_incomplete=stage_a.information_incomplete,
            rule_status=final_invariant.component_statuses.get(
                ComponentType.RULE, ComponentStatus.UNAVAILABLE
            ),
            ml_status=final_invariant.component_statuses.get(
                ComponentType.ML, ComponentStatus.UNAVAILABLE
            ),
            llm_status=final_invariant.component_statuses.get(
                ComponentType.LLM, ComponentStatus.UNAVAILABLE
            ),
            llm_provider_label=self.llm.name,
        )

    def _get_llm_explanation(self, extraction: ExtractionResult) -> Optional[str]:
        """Ask the LLM for a prose explanation. Returns None on failure."""
        try:
            from app.services.llm_adapter import build_structured_prompt
            payload = build_structured_prompt(extraction)
            # For prose explanation, we reuse the provider's _call_api with explanation payload
            # In practice, the same response JSON's 'reasoning' field is the explanation
            raw = self.llm._call_api_with_timeout(payload, self.llm_timeout)
            import json
            data = json.loads(raw)
            return data.get("reasoning")
        except Exception:
            return None

    def _stage_b_fallback(
        self,
        stage_a: StageAResult,
        assessment_id: Optional[str],
    ) -> AssessmentResult:
        """Return a minimal AssessmentResult when Stage B completely fails."""
        triggered = stage_a.rule_engine_result.all_matched_rules if stage_a.rule_engine_result else []
        from app.triage.nlp_extractor import ExtractedAttributes, ExtractionResult
        extraction = stage_a.extraction or ExtractionResult(
            sanitized_text="", entities=[], attributes=ExtractedAttributes()
        )
        explanation = self.explainer_svc.build_template_explanation(
            stage_a.final_urgency, triggered, extraction
        )
        return AssessmentResult(
            final_urgency=stage_a.final_urgency,
            is_level_1_emergency=stage_a.is_level_1_emergency,
            is_uncertain=stage_a.invariant_result.is_uncertain,
            stage_a=stage_a,
            invariant_result=stage_a.invariant_result,
            ml_prediction=None,
            llm_component_result=None,
            explanation=explanation,
            followup_questions=stage_a.followup_questions,
            skipped_followup_questions=stage_a.skipped_followup_questions,
            information_incomplete=stage_a.information_incomplete,
            rule_status=stage_a.invariant_result.component_statuses.get(
                ComponentType.RULE, ComponentStatus.UNAVAILABLE
            ),
            ml_status=ComponentStatus.UNAVAILABLE,
            llm_status=ComponentStatus.UNAVAILABLE,
            llm_provider_label=self.llm.name,
        )

    def _generate_followups(
        self,
        rule_eng_result: Optional[RuleEngineResult],
        extraction: Optional[ExtractionResult],
    ) -> Any:
        """Generate follow-up questions from extraction and rule engine output."""
        if extraction is None:
            from app.triage.followups import FollowUpResult
            return FollowUpResult([], [], False)

        concepts_present = [
            e.canonical_concept for e in extraction.entities
            if e.status == EntityStatus.POSITIVE
        ]
        return self.followup_engine.generate(
            requires_age_followup=rule_eng_result.requires_age_followup if rule_eng_result else False,
            potential_pediatric_escalation=(
                rule_eng_result.potential_pediatric_escalation if rule_eng_result else False
            ),
            concepts_present=concepts_present,
            onset_known=extraction.attributes.onset is not None,
            severity_known=extraction.attributes.severity is not None,
            duration_known=extraction.attributes.duration is not None,
            max_optional_followups=self.max_optional_followups,
        )
