"""Triage Assessment API endpoints."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional
from app.core.config import settings
from app.core.urgency import Urgency
from app.db.models import (
    Assessment,
    OverrideLog,
    RuleTrigger,
    StructuredSymptom,
    User,
)
from app.db.session import get_db
from app.schemas.assessment import (
    AssessmentCreateRequest,
    AssessmentResponse,
    AssessmentSummaryResponse,
    FollowUpQuestionSchema,
    RuleTriggerSchema,
    StructuredSymptomSchema,
)
from app.triage.pipeline import TriagePipeline

router = APIRouter(prefix="/assessments", tags=["Assessments"])


def _to_followup_schema(q) -> FollowUpQuestionSchema:
    """Helper to convert FollowUpQuestion dataclass to Pydantic schema."""
    return FollowUpQuestionSchema(
        id=q.id,
        type=q.type.value,
        text=q.text,
        safety_critical=q.safety_critical,
        urgency_impact=q.urgency_impact,
        could_trigger_level_2=q.could_trigger_level_2,
        options=q.options,
        free_numeric=q.free_numeric,
        context_concept=q.context_concept,
    )


@router.post(
    "",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit symptoms for triage assessment",
)
def create_assessment(
    req: AssessmentCreateRequest,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Execute two-stage preliminary triage assessment.

    - Stage A executes synchronously (emergency first).
    - Stage B enriches with explanation, ML, LLM suggestions.
    - Privacy: Raw symptoms stored ONLY if explicitly opted in.
    """
    assessment_id = str(uuid.uuid4())
    session_id = x_session_id or (str(uuid.uuid4()) if not current_user else None)

    # Privacy opt-in determination
    if req.opt_in_store_raw_symptoms is not None:
        opt_in = req.opt_in_store_raw_symptoms
    elif current_user is not None:
        opt_in = current_user.opt_in_store_raw_symptoms
    else:
        opt_in = False

    raw_text_to_store = req.symptoms_text if opt_in else None

    # Run Triage Pipeline
    max_optional = req.max_optional_followups if req.max_optional_followups is not None else 3
    pipeline = TriagePipeline(max_optional_followups=max_optional)

    result = pipeline.assess(
        text=req.symptoms_text,
        age_years=req.age_years,
        age_months=req.age_months,
        assessment_id=assessment_id,
    )

    # Extract final urgency integer or None (for UNCERTAIN)
    final_urg_int = int(result.final_urgency) if isinstance(result.final_urgency, Urgency) else None

    # Determine component urgencies
    rule_urg_int = None
    if (
        result.stage_a.rule_engine_result
        and result.stage_a.rule_engine_result.component_result
        and result.stage_a.rule_engine_result.component_result.level
    ):
        rule_urg_int = int(result.stage_a.rule_engine_result.component_result.level)

    ml_urg_int = None
    if result.ml_prediction and result.ml_prediction.component_result.level:
        ml_urg_int = int(result.ml_prediction.component_result.level)

    llm_urg_int = None
    if result.llm_component_result and result.llm_component_result.level:
        llm_urg_int = int(result.llm_component_result.level)

    explanation_text = result.explanation.text if result.explanation else ""
    explanation_source = result.explanation.source if result.explanation else "template"
    llm_faithfulness = result.explanation.llm_faithfulness_passed if result.explanation else None

    # Age band
    resolved_age_band = (
        result.stage_a.rule_engine_result.resolved_age_band
        if result.stage_a.rule_engine_result
        else None
    )

    # Create Assessment DB Record
    db_assessment = Assessment(
        id=assessment_id,
        user_id=current_user.id if current_user else None,
        anonymous_session_id=session_id if not current_user else None,
        final_urgency=final_urg_int,
        is_uncertain=result.is_uncertain,
        rule_urgency=rule_urg_int,
        ml_urgency=ml_urg_int,
        llm_urgency=llm_urg_int,
        rule_status=result.rule_status.value,
        ml_status=result.ml_status.value,
        llm_status=result.llm_status.value,
        information_incomplete=result.information_incomplete,
        explanation_text=explanation_text,
        explanation_source=explanation_source,
        llm_faithfulness_passed=llm_faithfulness,
        llm_provider_label=result.llm_provider_label,
        age_years=req.age_years,
        age_band=resolved_age_band,
        sex=req.sex,
        opt_in_raw_symptom_storage=opt_in,
        raw_symptom_text=raw_text_to_store,
    )
    db.add(db_assessment)

    # Save Structured Symptoms
    structured_schemas: List[StructuredSymptomSchema] = []
    if result.stage_a.extraction:
        for ent in result.stage_a.extraction.entities:
            sym = StructuredSymptom(
                assessment_id=assessment_id,
                canonical_concept=ent.canonical_concept,
                status=ent.status.value,
                match_type=ent.match_type.value,
                fuzzy_score=ent.fuzzy_score,
                onset=result.stage_a.extraction.attributes.onset,
                severity=result.stage_a.extraction.attributes.severity,
                duration=result.stage_a.extraction.attributes.duration,
            )
            db.add(sym)
            structured_schemas.append(
                StructuredSymptomSchema(
                    canonical_concept=ent.canonical_concept,
                    status=ent.status.value,
                    match_type=ent.match_type.value,
                    fuzzy_score=ent.fuzzy_score,
                    onset=result.stage_a.extraction.attributes.onset,
                    severity=result.stage_a.extraction.attributes.severity,
                    duration=result.stage_a.extraction.attributes.duration,
                )
            )

    # Save Rule Triggers
    rule_schemas: List[RuleTriggerSchema] = []
    if result.stage_a.rule_engine_result:
        for rule in result.stage_a.rule_engine_result.all_matched_rules:
            rt = RuleTrigger(
                assessment_id=assessment_id,
                rule_id=rule.id,
                rule_name=rule.name,
                rule_level=int(rule.level),
                specialty=rule.specialty,
                review_status=rule.review_status,
            )
            db.add(rt)
            rule_schemas.append(
                RuleTriggerSchema(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    rule_level=int(rule.level),
                    specialty=rule.specialty,
                    review_status=rule.review_status,
                )
            )

    # Save Override / Escalation Logs (Audit) - NO raw symptom text!
    if result.invariant_result and result.invariant_result.audit_record:
        audit = result.invariant_result.audit_record
        if audit.escalated and audit.escalated_by:
            comp_name = audit.escalated_by.value if hasattr(audit.escalated_by, "value") else str(audit.escalated_by)
            db.add(
                OverrideLog(
                    assessment_id=assessment_id,
                    component=comp_name,
                    from_level=audit.rule_level,
                    to_level=audit.final_level,
                    reason=f"{comp_name} escalation accepted by invariant",
                )
            )
        if audit.downgrade_attempted:
            comp_name = (
                audit.downgrade_prevented_by.value
                if hasattr(audit.downgrade_prevented_by, "value")
                else "INVARIANT"
            )
            db.add(
                OverrideLog(
                    assessment_id=assessment_id,
                    component=comp_name,
                    from_level=audit.rule_level,
                    to_level=None,
                    reason="Adversarial downgrade attempt blocked by invariant",
                )
            )

    db.commit()
    db.refresh(db_assessment)

    # Format follow-up questions
    fqs = [_to_followup_schema(q) for q in result.followup_questions]
    skipped_fqs = [_to_followup_schema(q) for q in result.skipped_followup_questions]

    retention_notice = (
        f"Guest assessment: automatically purged after {settings.GUEST_RETENTION_HOURS} hours."
        if not current_user
        else None
    )

    return AssessmentResponse(
        id=db_assessment.id,
        assessment_id=db_assessment.id,
        created_at=db_assessment.created_at,
        final_urgency=db_assessment.final_urgency,
        is_uncertain=db_assessment.is_uncertain,
        is_level_1_emergency=result.is_level_1_emergency,
        rule_urgency=db_assessment.rule_urgency,
        ml_urgency=db_assessment.ml_urgency,
        llm_urgency=db_assessment.llm_urgency,
        rule_status=db_assessment.rule_status,
        ml_status=db_assessment.ml_status,
        llm_status=db_assessment.llm_status,
        information_incomplete=db_assessment.information_incomplete,
        explanation_text=db_assessment.explanation_text,
        explanation_source=db_assessment.explanation_source,
        llm_faithfulness_passed=db_assessment.llm_faithfulness_passed,
        llm_provider_label=db_assessment.llm_provider_label,
        age_years=db_assessment.age_years,
        age_band=db_assessment.age_band,
        sex=db_assessment.sex,
        raw_symptom_text=db_assessment.raw_symptom_text,
        guest_retention_notice=retention_notice,
        structured_symptoms=structured_schemas,
        rule_triggers=rule_schemas,
        followup_questions=fqs,
        skipped_followup_questions=skipped_fqs,
    )


@router.get(
    "",
    response_model=List[AssessmentSummaryResponse],
    summary="List assessments for current user or anonymous session",
)
def list_assessments(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Retrieve assessments scoped strictly to the authenticated user or session."""
    if current_user:
        assessments = (
            db.query(Assessment)
            .filter(Assessment.user_id == current_user.id)
            .order_by(Assessment.created_at.desc())
            .all()
        )
    elif x_session_id:
        assessments = (
            db.query(Assessment)
            .filter(Assessment.anonymous_session_id == x_session_id)
            .order_by(Assessment.created_at.desc())
            .all()
        )
    else:
        return []

    return [
        AssessmentSummaryResponse(
            id=a.id,
            assessment_id=a.id,
            created_at=a.created_at,
            final_urgency=a.final_urgency,
            is_uncertain=a.is_uncertain,
            is_level_1_emergency=(a.final_urgency == 1 and not a.is_uncertain),
            information_incomplete=a.information_incomplete,
            rule_status=a.rule_status,
            ml_status=a.ml_status,
            llm_status=a.llm_status,
        )
        for a in assessments
    ]


@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
    summary="Get single assessment details (IDOR-protected)",
)
def get_assessment(
    assessment_id: str,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Retrieve single assessment. IDOR protected: returns 404/403 if unauthorized."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    # IDOR Check
    if current_user:
        if assessment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own this assessment.",
            )
    else:
        if not x_session_id or assessment.anonymous_session_id != x_session_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own this session.",
            )

    structured_schemas = [
        StructuredSymptomSchema.model_validate(s) for s in assessment.structured_symptoms
    ]
    rule_schemas = [
        RuleTriggerSchema.model_validate(r) for r in assessment.rule_triggers
    ]

    return AssessmentResponse(
        id=assessment.id,
        assessment_id=assessment.id,
        created_at=assessment.created_at,
        final_urgency=assessment.final_urgency,
        is_uncertain=assessment.is_uncertain,
        is_level_1_emergency=(assessment.final_urgency == 1 and not assessment.is_uncertain),
        rule_urgency=assessment.rule_urgency,
        ml_urgency=assessment.ml_urgency,
        llm_urgency=assessment.llm_urgency,
        rule_status=assessment.rule_status,
        ml_status=assessment.ml_status,
        llm_status=assessment.llm_status,
        information_incomplete=assessment.information_incomplete,
        explanation_text=assessment.explanation_text,
        explanation_source=assessment.explanation_source,
        llm_faithfulness_passed=assessment.llm_faithfulness_passed,
        llm_provider_label=assessment.llm_provider_label,
        age_years=assessment.age_years,
        age_band=assessment.age_band,
        sex=assessment.sex,
        raw_symptom_text=assessment.raw_symptom_text,
        structured_symptoms=structured_schemas,
        rule_triggers=rule_schemas,
        followup_questions=[],
        skipped_followup_questions=[],
    )


@router.post(
    "/{assessment_id}/followups",
    response_model=AssessmentResponse,
    summary="Submit answers to follow-up questions for this assessment",
)
def submit_assessment_followups(
    assessment_id: str,
    req: dict,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Bridge endpoint for submitting followups under /assessments/{assessment_id}/followups."""
    from app.api.v1.followups import submit_followups
    from app.schemas.assessment import FollowUpSubmitRequest, FollowUpAnswerInput

    # Handle both {answers: [...]} and raw array
    raw_answers = req.get("answers", []) if isinstance(req, dict) else req
    typed_answers = []
    for item in raw_answers:
        if isinstance(item, dict):
            qid = item.get("question_id", "")
            val = item.get("answer_value")
            sel_opt = item.get("selected_option")
            num_val = item.get("numeric_value")

            if sel_opt is None and num_val is None and val is not None:
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    num_val = float(val)
                elif isinstance(val, bool):
                    sel_opt = "Yes" if val else "No"
                else:
                    sel_opt = str(val)

            typed_answers.append(
                FollowUpAnswerInput(
                    question_id=qid,
                    selected_option=sel_opt,
                    numeric_value=num_val,
                )
            )

    submit_req = FollowUpSubmitRequest(answers=typed_answers)
    return submit_followups(
        req=submit_req,
        assessment_id=assessment_id,
        x_session_id=x_session_id,
        current_user=current_user,
        db=db,
    )


@router.delete(
    "/{assessment_id}",
    summary="Delete single assessment (IDOR-protected, cascades)",
)
def delete_assessment(
    assessment_id: str,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Delete a single assessment and its associated children."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    # IDOR Check
    if current_user:
        if assessment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You cannot delete another user's assessment.",
            )
    else:
        if not x_session_id or assessment.anonymous_session_id != x_session_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You cannot delete another session's assessment.",
            )

    db.delete(assessment)
    db.commit()
    return {"deleted": True, "id": assessment_id}


@router.delete(
    "",
    summary="Wipe all assessments for current user or session ONLY",
)
def wipe_all_assessments(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Wipe all assessments belonging strictly to the current user or session."""
    if current_user:
        assessments = db.query(Assessment).filter(Assessment.user_id == current_user.id).all()
    elif x_session_id:
        assessments = db.query(Assessment).filter(Assessment.anonymous_session_id == x_session_id).all()
    else:
        return {"deleted_count": 0}

    count = len(assessments)
    for a in assessments:
        db.delete(a)
    db.commit()

    return {"deleted_count": count}
