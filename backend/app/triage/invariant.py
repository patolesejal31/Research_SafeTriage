"""Safety Invariant Engine for SafeTriage.

Implements the non-negotiable safety invariant:
1. Urgency levels: 1=Emergency, 2=Urgent, 3=Routine, 4=Self-care (lower number = more urgent).
2. UNCERTAIN is a DISTINCT non-integer state. It is never displayed as Level 3, Level 4,
   or 'self-care'.
3. Normal case: final_level = min(rule_level, ml_level, llm_level) where ML and LLM
   may strictly ESCALATE, never downgrade.
4. Failure Handling:
   - Rule-engine failure: result = UNCERTAIN. If ML or LLM produced a Level 1 or 2
     escalation, show it labeled 'model-suggested, rule engine unavailable'. Never drop it
     silently, never present it as a rule-verified result. Model Level 3/4 are ignored.
   - Rules ran OK, no match: result = UNCERTAIN. If ML or LLM produced a Level 1 or 2
     suggestion, show it labeled 'model-suggested, no rule matched'. Model Level 3/4 are ignored.
   - ML unavailable: keep successful rule result; record ml_status=UNAVAILABLE.
   - LLM timeout/invalid/error: keep successful rule result (+ ML if available);
     record llm_status=TIMEOUT|INVALID|ERROR.
5. Components with non-OK status or out-of-range levels are marked INVALID and do NOT contribute.
6. Audit records contain strictly typed fields only, never raw symptom descriptions.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from app.core.urgency import (
    UNCERTAIN,
    Urgency,
    UrgencyOrUncertain,
    validate_urgency,
)

INVARIANT_VERSION = "1.0.0"


class ComponentType(str, Enum):
    """Component sources contributing to triage assessment."""
    RULE = "RULE"
    ML = "ML"
    LLM = "LLM"


class ComponentStatus(str, Enum):
    """Component execution status."""
    OK = "OK"                     # Successful execution with a valid urgency level
    NO_MATCH = "NO_MATCH"         # Engine executed successfully, but no clinical rule matched
    UNAVAILABLE = "UNAVAILABLE"   # Service or model is offline, missing, or unconfigured
    TIMEOUT = "TIMEOUT"           # Call timed out
    INVALID = "INVALID"           # Malformed output, out-of-range level, or schema validation failed
    ERROR = "ERROR"               # Internal unhandled crash or exception


@dataclass(frozen=True)
class ComponentResult:
    """Standardized result returned by a triage component."""
    component: ComponentType
    status: ComponentStatus
    level: Optional[Urgency] = None
    rule_id: Optional[str] = None
    model_name: Optional[str] = None


@dataclass(frozen=True)
class AuditRecord:
    """Strictly typed audit event record.
    
    Contains NO free-text fields or raw symptom descriptions.
    """
    assessment_id: Optional[str]
    rule_status: ComponentStatus
    ml_status: ComponentStatus
    llm_status: ComponentStatus
    rule_level: Optional[int]
    ml_level: Optional[int]
    llm_level: Optional[int]
    final_level: Optional[int]
    is_uncertain: bool
    escalated: bool
    escalated_by: Optional[ComponentType]
    downgrade_attempted: bool
    downgrade_prevented_by: Optional[ComponentType]
    invariant_version: str
    timestamp_utc: datetime


@dataclass(frozen=True)
class InvariantResult:
    """Final output guaranteed by the safety invariant."""
    final_urgency: UrgencyOrUncertain
    is_uncertain: bool
    determining_component: Optional[ComponentType]
    model_suggested_urgency: Optional[Urgency]
    model_suggestion_label: Optional[str]
    component_statuses: Dict[ComponentType, ComponentStatus]
    audit_record: AuditRecord


def enforce_invariant(
    rule_result: Optional[ComponentResult] = None,
    ml_result: Optional[ComponentResult] = None,
    llm_result: Optional[ComponentResult] = None,
    assessment_id: Optional[str] = None,
) -> InvariantResult:
    """Enforce the non-negotiable SafeTriage safety invariant across all components.
    
    Args:
        rule_result: Result from the deterministic rule engine.
        ml_result: Optional result from the ML baseline model.
        llm_result: Optional result from the LLM adapter.
        assessment_id: Optional identifier for logging and traceability.
        
    Returns:
        InvariantResult containing the verified final urgency, component statuses,
        model suggestions (if rules unavailable/no match), and typed audit record.
    """
    # Normalize None inputs to default UNAVAILABLE results
    r_res = rule_result if rule_result is not None else ComponentResult(ComponentType.RULE, ComponentStatus.UNAVAILABLE)
    m_res = ml_result if ml_result is not None else ComponentResult(ComponentType.ML, ComponentStatus.UNAVAILABLE)
    l_res = llm_result if llm_result is not None else ComponentResult(ComponentType.LLM, ComponentStatus.UNAVAILABLE)

    # Validate each component's level and status
    # Out-of-range levels (0, 5, -1, etc.) or None when status is OK are rejected as INVALID
    def _validate_component(comp: ComponentResult) -> tuple[ComponentStatus, Optional[Urgency]]:
        if comp.status == ComponentStatus.OK:
            validated = validate_urgency(comp.level)
            if validated is None:
                # Invalid level provided despite OK status -> mark as INVALID, never clamp
                return ComponentStatus.INVALID, None
            return ComponentStatus.OK, validated
        # Non-OK components do not contribute any level
        return comp.status, None

    r_status, r_level = _validate_component(r_res)
    m_status, m_level = _validate_component(m_res)
    l_status, l_level = _validate_component(l_res)

    statuses: Dict[ComponentType, ComponentStatus] = {
        ComponentType.RULE: r_status,
        ComponentType.ML: m_status,
        ComponentType.LLM: l_status,
    }

    # Helper: extract high-urgency model candidates (Level 1 or Level 2 only)
    def _extract_model_emergency_suggestion() -> Optional[Urgency]:
        candidates: list[Urgency] = []
        if m_status == ComponentStatus.OK and m_level in (Urgency.EMERGENCY, Urgency.URGENT):
            candidates.append(m_level)
        if l_status == ComponentStatus.OK and l_level in (Urgency.EMERGENCY, Urgency.URGENT):
            candidates.append(l_level)
        if candidates:
            return min(candidates)
        return None

    # BRANCH 1: Rule Engine did not succeed with status OK
    if r_status != ComponentStatus.OK:
        final_urgency: UrgencyOrUncertain = UNCERTAIN
        is_uncertain = True
        determining_component = None
        escalated = False
        escalated_by = None
        downgrade_attempted = False
        downgrade_prevented_by = None

        model_suggestion = _extract_model_emergency_suggestion()

        if r_status == ComponentStatus.NO_MATCH:
            # Rules ran successfully, but no clinical rule matched
            if model_suggestion is not None:
                model_suggested_urgency = model_suggestion
                model_suggestion_label = "model-suggested, no rule matched"
            else:
                model_suggested_urgency = None
                model_suggestion_label = None
        else:
            # Rule engine failed (ERROR, UNAVAILABLE, TIMEOUT, or INVALID)
            if model_suggestion is not None:
                model_suggested_urgency = model_suggestion
                model_suggestion_label = "model-suggested, rule engine unavailable"
            else:
                model_suggested_urgency = None
                model_suggestion_label = None

        audit_rec = AuditRecord(
            assessment_id=assessment_id,
            rule_status=r_status,
            ml_status=m_status,
            llm_status=l_status,
            rule_level=None,
            ml_level=int(m_level) if m_level is not None else None,
            llm_level=int(l_level) if l_level is not None else None,
            final_level=None,
            is_uncertain=True,
            escalated=False,
            escalated_by=None,
            downgrade_attempted=False,
            downgrade_prevented_by=None,
            invariant_version=INVARIANT_VERSION,
            timestamp_utc=datetime.now(timezone.utc),
        )

        return InvariantResult(
            final_urgency=final_urgency,
            is_uncertain=is_uncertain,
            determining_component=determining_component,
            model_suggested_urgency=model_suggested_urgency,
            model_suggestion_label=model_suggestion_label,
            component_statuses=statuses,
            audit_record=audit_rec,
        )

    # BRANCH 2: Rule Engine succeeded with status OK
    # r_level is guaranteed to be a valid Urgency instance
    assert r_level is not None

    downgrade_attempted = False
    downgrade_prevented_by = None

    # ML check: can only contribute if OK and not downgrading
    ml_contributes = False
    if m_status == ComponentStatus.OK and m_level is not None:
        if m_level > r_level:
            # Attempted downgrade (higher integer = less urgent)
            downgrade_attempted = True
            downgrade_prevented_by = ComponentType.ML
        else:
            ml_contributes = True

    # LLM check: can only contribute if OK and not downgrading
    llm_contributes = False
    if l_status == ComponentStatus.OK and l_level is not None:
        if l_level > r_level:
            # Attempted downgrade
            downgrade_attempted = True
            if downgrade_prevented_by is None:
                downgrade_prevented_by = ComponentType.LLM
        else:
            llm_contributes = True

    # Only components with status OK contribute to the minimum
    candidates: list[tuple[ComponentType, Urgency]] = [(ComponentType.RULE, r_level)]
    if ml_contributes and m_level is not None:
        candidates.append((ComponentType.ML, m_level))
    if llm_contributes and l_level is not None:
        candidates.append((ComponentType.LLM, l_level))

    min_urgency = min(lvl for _, lvl in candidates)
    final_urgency = min_urgency
    is_uncertain = False
    model_suggested_urgency = None
    model_suggestion_label = None

    # Determine escalation and determining component
    if min_urgency < r_level:
        escalated = True
        # Check which model triggered the escalation
        if ml_contributes and m_level == min_urgency:
            escalated_by = ComponentType.ML
            determining_component = ComponentType.ML
        else:
            escalated_by = ComponentType.LLM
            determining_component = ComponentType.LLM
    else:
        escalated = False
        escalated_by = None
        determining_component = ComponentType.RULE

    audit_rec = AuditRecord(
        assessment_id=assessment_id,
        rule_status=r_status,
        ml_status=m_status,
        llm_status=l_status,
        rule_level=int(r_level),
        ml_level=int(m_level) if m_level is not None else None,
        llm_level=int(l_level) if l_level is not None else None,
        final_level=int(final_urgency),
        is_uncertain=False,
        escalated=escalated,
        escalated_by=escalated_by,
        downgrade_attempted=downgrade_attempted,
        downgrade_prevented_by=downgrade_prevented_by,
        invariant_version=INVARIANT_VERSION,
        timestamp_utc=datetime.now(timezone.utc),
    )

    return InvariantResult(
        final_urgency=final_urgency,
        is_uncertain=False,
        determining_component=determining_component,
        model_suggested_urgency=None,
        model_suggestion_label=None,
        component_statuses=statuses,
        audit_record=audit_rec,
    )
