"""Comprehensive unit and property-based tests for the SafeTriage invariant engine."""

from dataclasses import asdict
from datetime import datetime
from enum import Enum
import io
import logging

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from app.core.logging_filters import SensitiveDataFilter
from app.core.urgency import UNCERTAIN, Urgency
from app.triage.invariant import (
    ComponentResult,
    ComponentStatus,
    ComponentType,
    enforce_invariant,
)


class TestPairwiseDowngradesAndEscalations:
    """Tests ensuring models can only escalate and every downgrade is strictly blocked."""

    @pytest.mark.parametrize("rule_lvl", [Urgency.EMERGENCY, Urgency.URGENT, Urgency.ROUTINE, Urgency.SELF_CARE])
    @pytest.mark.parametrize("ml_lvl", [Urgency.EMERGENCY, Urgency.URGENT, Urgency.ROUTINE, Urgency.SELF_CARE])
    def test_ml_pairwise_interaction_with_rule(self, rule_lvl: Urgency, ml_lvl: Urgency):
        """Verify that ML cannot downgrade rule urgency and correctly escalates when more urgent."""
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.OK, rule_lvl)
        ml_res = ComponentResult(ComponentType.ML, ComponentStatus.OK, ml_lvl)

        result = enforce_invariant(rule_result=rule_res, ml_result=ml_res)

        assert not result.is_uncertain
        assert isinstance(result.final_urgency, Urgency)

        if ml_lvl > rule_lvl:
            # ML attempted downgrade -> MUST be blocked
            assert result.final_urgency == rule_lvl
            assert result.audit_record.downgrade_attempted is True
            assert result.audit_record.downgrade_prevented_by == ComponentType.ML
            assert result.audit_record.escalated is False
            assert result.determining_component == ComponentType.RULE
        elif ml_lvl < rule_lvl:
            # ML escalated -> MUST be accepted
            assert result.final_urgency == ml_lvl
            assert result.audit_record.escalated is True
            assert result.audit_record.escalated_by == ComponentType.ML
            assert result.audit_record.downgrade_attempted is False
            assert result.determining_component == ComponentType.ML
        else:
            # Equal levels
            assert result.final_urgency == rule_lvl
            assert result.audit_record.escalated is False
            assert result.audit_record.downgrade_attempted is False
            assert result.determining_component == ComponentType.RULE

    @pytest.mark.parametrize("rule_lvl", [Urgency.EMERGENCY, Urgency.URGENT, Urgency.ROUTINE, Urgency.SELF_CARE])
    @pytest.mark.parametrize("llm_lvl", [Urgency.EMERGENCY, Urgency.URGENT, Urgency.ROUTINE, Urgency.SELF_CARE])
    def test_llm_pairwise_interaction_with_rule(self, rule_lvl: Urgency, llm_lvl: Urgency):
        """Verify that LLM cannot downgrade rule urgency and correctly escalates when more urgent."""
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.OK, rule_lvl)
        llm_res = ComponentResult(ComponentType.LLM, ComponentStatus.OK, llm_lvl)

        result = enforce_invariant(rule_result=rule_res, llm_result=llm_res)

        assert not result.is_uncertain
        assert isinstance(result.final_urgency, Urgency)

        if llm_lvl > rule_lvl:
            # LLM attempted downgrade -> MUST be blocked
            assert result.final_urgency == rule_lvl
            assert result.audit_record.downgrade_attempted is True
            assert result.audit_record.downgrade_prevented_by == ComponentType.LLM
            assert result.audit_record.escalated is False
        elif llm_lvl < rule_lvl:
            # LLM escalated -> MUST be accepted
            assert result.final_urgency == llm_lvl
            assert result.audit_record.escalated is True
            assert result.audit_record.escalated_by == ComponentType.LLM
            assert result.determining_component == ComponentType.LLM
        else:
            assert result.final_urgency == rule_lvl

    def test_chest_pain_adversarial_downgrade(self):
        """Adversarial test: Rule triggers Level 1 (Emergency), ML says Level 4, LLM says Level 4.
        
        Final urgency MUST remain Level 1 Emergency.
        """
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.OK, Urgency.EMERGENCY, rule_id="ACS_001")
        ml_res = ComponentResult(ComponentType.ML, ComponentStatus.OK, Urgency.SELF_CARE)
        llm_res = ComponentResult(ComponentType.LLM, ComponentStatus.OK, Urgency.SELF_CARE)

        result = enforce_invariant(rule_res, ml_res, llm_res)

        assert result.final_urgency == Urgency.EMERGENCY
        assert result.audit_record.downgrade_attempted is True
        assert result.audit_record.final_level == 1
        assert result.determining_component == ComponentType.RULE


class TestThreeFailureModes:
    """Tests covering the three distinct failure modes defined in the non-negotiable invariants."""

    def test_failure_mode_1_rule_engine_failure_returns_uncertain(self):
        """Failure mode 1: Rule engine fails -> final result is UNCERTAIN."""
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.ERROR)
        result = enforce_invariant(rule_result=rule_res)

        assert result.final_urgency is UNCERTAIN
        assert result.is_uncertain is True
        assert result.audit_record.final_level is None
        assert result.determining_component is None

    def test_failure_mode_1_with_ml_emergency_escalation_labeled(self):
        """Rule engine fails, but ML produced Level 1 escalation:
        Result remains UNCERTAIN, but model suggestion is labeled 'model-suggested, rule engine unavailable'.
        """
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.ERROR)
        ml_res = ComponentResult(ComponentType.ML, ComponentStatus.OK, Urgency.EMERGENCY)
        llm_res = ComponentResult(ComponentType.LLM, ComponentStatus.UNAVAILABLE)

        result = enforce_invariant(rule_res, ml_res, llm_res)

        assert result.final_urgency is UNCERTAIN
        assert result.is_uncertain is True
        assert result.model_suggested_urgency == Urgency.EMERGENCY
        assert result.model_suggestion_label == "model-suggested, rule engine unavailable"

    def test_failure_mode_1_with_llm_urgent_escalation_labeled(self):
        """Rule engine fails, but LLM produced Level 2 escalation:
        Result remains UNCERTAIN, model suggestion is Level 2 labeled 'model-suggested, rule engine unavailable'.
        """
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.UNAVAILABLE)
        llm_res = ComponentResult(ComponentType.LLM, ComponentStatus.OK, Urgency.URGENT)

        result = enforce_invariant(rule_res, llm_result=llm_res)

        assert result.final_urgency is UNCERTAIN
        assert result.model_suggested_urgency == Urgency.URGENT
        assert result.model_suggestion_label == "model-suggested, rule engine unavailable"

    def test_failure_mode_1_ignores_model_level_3_and_4(self):
        """Rule engine fails and ML/LLM suggest Level 3 or 4:
        Model suggestions are IGNORED (cannot suggest routine/self-care when uncertain).
        """
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.ERROR)
        ml_res = ComponentResult(ComponentType.ML, ComponentStatus.OK, Urgency.ROUTINE)
        llm_res = ComponentResult(ComponentType.LLM, ComponentStatus.OK, Urgency.SELF_CARE)

        result = enforce_invariant(rule_res, ml_res, llm_res)

        assert result.final_urgency is UNCERTAIN
        assert result.model_suggested_urgency is None
        assert result.model_suggestion_label is None

    def test_failure_mode_2_ml_unavailable_preserves_rule_result(self):
        """Failure mode 2: ML is unavailable, keep successful rule result and record ml_status=unavailable."""
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.OK, Urgency.URGENT)
        ml_res = ComponentResult(ComponentType.ML, ComponentStatus.UNAVAILABLE)
        llm_res = ComponentResult(ComponentType.LLM, ComponentStatus.OK, Urgency.URGENT)

        result = enforce_invariant(rule_res, ml_res, llm_res)

        assert result.final_urgency == Urgency.URGENT
        assert result.component_statuses[ComponentType.ML] == ComponentStatus.UNAVAILABLE
        assert result.audit_record.ml_status == ComponentStatus.UNAVAILABLE
        assert result.audit_record.ml_level is None

    def test_failure_mode_3_llm_timeout_preserves_rule_and_ml(self):
        """Failure mode 3: LLM timeout, keep successful rule result (+ ML if available)."""
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.OK, Urgency.ROUTINE)
        ml_res = ComponentResult(ComponentType.ML, ComponentStatus.OK, Urgency.URGENT)
        llm_res = ComponentResult(ComponentType.LLM, ComponentStatus.TIMEOUT)

        result = enforce_invariant(rule_res, ml_res, llm_res)

        assert result.final_urgency == Urgency.URGENT  # ML escalation kept
        assert result.component_statuses[ComponentType.LLM] == ComponentStatus.TIMEOUT
        assert result.audit_record.llm_status == ComponentStatus.TIMEOUT
        assert result.audit_record.llm_level is None

    def test_failure_mode_3_llm_invalid_preserves_rule(self):
        """Failure mode 3: LLM returns invalid JSON or out-of-range level, preserve rule."""
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.OK, Urgency.EMERGENCY)
        llm_res = ComponentResult(ComponentType.LLM, ComponentStatus.INVALID)

        result = enforce_invariant(rule_res, llm_result=llm_res)

        assert result.final_urgency == Urgency.EMERGENCY
        assert result.component_statuses[ComponentType.LLM] == ComponentStatus.INVALID
        assert result.audit_record.llm_status == ComponentStatus.INVALID


class TestDistinguishNoMatchFromRulesFailed:
    """Requirement 4: Distinguish 'rules ran OK, no match' from 'rules failed'."""

    def test_rules_ran_ok_no_match(self):
        """Rules ran OK without error, but no rule matched."""
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.NO_MATCH)
        result = enforce_invariant(rule_result=rule_res)

        assert result.final_urgency is UNCERTAIN
        assert result.is_uncertain is True
        assert result.component_statuses[ComponentType.RULE] == ComponentStatus.NO_MATCH
        assert result.audit_record.rule_status == ComponentStatus.NO_MATCH
        assert result.model_suggested_urgency is None
        assert result.model_suggestion_label is None

    def test_rules_no_match_with_model_emergency_suggestion(self):
        """Rules ran OK with no match, but ML produced Level 1:
        Result is UNCERTAIN, model suggestion is labeled 'model-suggested, no rule matched'.
        """
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.NO_MATCH)
        ml_res = ComponentResult(ComponentType.ML, ComponentStatus.OK, Urgency.EMERGENCY)

        result = enforce_invariant(rule_res, ml_result=ml_res)

        assert result.final_urgency is UNCERTAIN
        assert result.component_statuses[ComponentType.RULE] == ComponentStatus.NO_MATCH
        assert result.model_suggested_urgency == Urgency.EMERGENCY
        assert result.model_suggestion_label == "model-suggested, no rule matched"

    def test_rules_failed_distinct_from_no_match(self):
        """Rules failed with ERROR -> distinct from NO_MATCH in status and label."""
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.ERROR)
        ml_res = ComponentResult(ComponentType.ML, ComponentStatus.OK, Urgency.EMERGENCY)

        result = enforce_invariant(rule_res, ml_result=ml_res)

        assert result.final_urgency is UNCERTAIN
        assert result.component_statuses[ComponentType.RULE] == ComponentStatus.ERROR
        assert result.model_suggested_urgency == Urgency.EMERGENCY
        assert result.model_suggestion_label == "model-suggested, rule engine unavailable"


class TestAuditRecordIntegrity:
    """Requirement 5: Audit records use typed fields only, no free-text fields."""

    def test_audit_record_typed_fields_only(self):
        """Verify every field in AuditRecord has a strict type and no free-text fields exist."""
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.OK, Urgency.ROUTINE)
        ml_res = ComponentResult(ComponentType.ML, ComponentStatus.OK, Urgency.URGENT)
        llm_res = ComponentResult(ComponentType.LLM, ComponentStatus.OK, Urgency.EMERGENCY)

        result = enforce_invariant(rule_res, ml_res, llm_res, assessment_id="test-uuid-1234")
        rec = result.audit_record

        assert isinstance(rec.assessment_id, str)
        assert isinstance(rec.rule_status, ComponentStatus)
        assert isinstance(rec.ml_status, ComponentStatus)
        assert isinstance(rec.llm_status, ComponentStatus)
        assert isinstance(rec.rule_level, int)
        assert isinstance(rec.ml_level, int)
        assert isinstance(rec.llm_level, int)
        assert isinstance(rec.final_level, int)
        assert isinstance(rec.is_uncertain, bool)
        assert isinstance(rec.escalated, bool)
        assert isinstance(rec.escalated_by, ComponentType)
        assert isinstance(rec.downgrade_attempted, bool)
        assert rec.downgrade_prevented_by is None or isinstance(rec.downgrade_prevented_by, ComponentType)
        assert isinstance(rec.invariant_version, str)
        assert isinstance(rec.timestamp_utc, datetime)

        # Ensure no symptom strings or free text exist in record
        rec_dict = asdict(rec)
        for key, val in rec_dict.items():
            if isinstance(val, str):
                # Only allowed strings are ID, invariant version, or enum values
                assert key in ("assessment_id", "invariant_version") or isinstance(getattr(rec, key), Enum)


class TestPlantedSecretLogCapture:
    """Requirement 6: Planted secret string SECRET_SYMPTOM_XYZ must NEVER appear in logs."""

    def test_planted_secret_is_redacted_from_logger(self):
        """Planted string SECRET_SYMPTOM_XYZ in logs must be caught and redacted."""
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.addFilter(SensitiveDataFilter())

        test_logger = logging.getLogger("safetriage.test.redaction")
        test_logger.setLevel(logging.INFO)
        test_logger.addHandler(handler)

        planted_secret = "SECRET_SYMPTOM_XYZ_CHEST_PAIN"
        test_logger.info("Processing assessment with %s", planted_secret)
        test_logger.info("Direct log msg: User reported SECRET_SYMPTOM_XYZ and palpitations")

        output = log_stream.getvalue()

        # Planted secret string MUST NOT appear
        assert "SECRET_SYMPTOM_XYZ" not in output
        assert planted_secret not in output
        # Redaction indicator MUST appear
        assert "[REDACTED]" in output

    def test_audit_record_does_not_contain_planted_secret(self):
        """Audit record representation never contains planted secret."""
        rule_res = ComponentResult(ComponentType.RULE, ComponentStatus.OK, Urgency.EMERGENCY)
        result = enforce_invariant(rule_res, assessment_id="valid-id-only")

        rec_repr = str(asdict(result.audit_record))
        assert "SECRET_SYMPTOM_XYZ" not in rec_repr


class TestHypothesisPropertyBased:
    """Requirement 7: Hypothesis tests covering all status combinations and out-of-range levels."""

    @settings(max_examples=200)
    @given(
        r_status=st.sampled_from(ComponentStatus),
        m_status=st.sampled_from(ComponentStatus),
        l_status=st.sampled_from(ComponentStatus),
        r_lvl=st.one_of(st.none(), st.integers(min_value=-5, max_value=10)),
        m_lvl=st.one_of(st.none(), st.integers(min_value=-5, max_value=10)),
        l_lvl=st.one_of(st.none(), st.integers(min_value=-5, max_value=10)),
    )
    def test_all_status_and_level_combinations(
        self,
        r_status: ComponentStatus,
        m_status: ComponentStatus,
        l_status: ComponentStatus,
        r_lvl: int | None,
        m_lvl: int | None,
        l_lvl: int | None,
    ):
        """Property: The system is completely robust across all status and level inputs."""
        rule_res = ComponentResult(ComponentType.RULE, r_status, r_lvl)  # type: ignore
        ml_res = ComponentResult(ComponentType.ML, m_status, m_lvl)      # type: ignore
        llm_res = ComponentResult(ComponentType.LLM, l_status, l_lvl)   # type: ignore

        result = enforce_invariant(rule_res, ml_res, llm_res)

        # Invariant 1: UNCERTAIN is never an int
        if result.is_uncertain:
            assert result.final_urgency is UNCERTAIN
            assert not isinstance(result.final_urgency, int)
            assert result.audit_record.final_level is None
        else:
            assert isinstance(result.final_urgency, Urgency)
            assert result.final_urgency in (1, 2, 3, 4)
            assert result.audit_record.final_level in (1, 2, 3, 4)

        # Invariant 2: Out of range levels are rejected as INVALID, never clamped
        if r_status == ComponentStatus.OK and r_lvl not in (1, 2, 3, 4):
            assert result.component_statuses[ComponentType.RULE] == ComponentStatus.INVALID
            assert result.final_urgency is UNCERTAIN

        # Invariant 3: Safety property - when rules succeed, final urgency is never less urgent than rule
        if r_status == ComponentStatus.OK and r_lvl in (1, 2, 3, 4):
            assert result.component_statuses[ComponentType.RULE] == ComponentStatus.OK
            assert not result.is_uncertain
            assert isinstance(result.final_urgency, Urgency)
            # Must be <= r_lvl (equal or more urgent, never downgraded)
            assert int(result.final_urgency) <= r_lvl

        # Invariant 4: When rules fail (ERROR, UNAVAILABLE), final is always UNCERTAIN
        if r_status in (ComponentStatus.ERROR, ComponentStatus.UNAVAILABLE, ComponentStatus.TIMEOUT):
            assert result.is_uncertain is True
            assert result.final_urgency is UNCERTAIN
