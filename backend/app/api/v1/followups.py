"""Follow-up questions submission and triage re-assessment endpoint."""

from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional
from app.api.v1.assessments import _to_followup_schema
from app.core.urgency import Urgency
from app.db.models import Assessment, User
from app.db.session import get_db
from app.schemas.assessment import (
    AssessmentResponse,
    FollowUpSubmitRequest,
    RuleTriggerSchema,
    StructuredSymptomSchema,
)
from app.triage.followups import FollowUpAnswer
from app.triage.pipeline import TriagePipeline

router = APIRouter(prefix="/followups", tags=["Follow-ups"])


@router.post(
    "",
    response_model=AssessmentResponse,
    summary="Submit answers to follow-up questions and re-assess triage urgency",
)
@router.post(
    "/{assessment_id}",
    response_model=AssessmentResponse,
    summary="Submit answers to follow-up questions by assessment ID",
)
def submit_followups(
    req: FollowUpSubmitRequest,
    assessment_id: Optional[str] = None,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Process structured follow-up answers. Re-evaluates rules and models.

    Invariant: Follow-up answers may ESCALATE urgency, but never downgrade.
    """
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

    # Convert answers to typed domain dataclasses
    domain_answers = [
        FollowUpAnswer(
            question_id=ans.question_id,
            selected_option=ans.selected_option,
            numeric_value=ans.numeric_value,
        )
        for ans in req.answers
    ]

    pipeline = TriagePipeline()

    # If raw symptom text was stored, re-run assess with answers
    # Otherwise run extraction reconstruction from structured symptoms
    text = assessment.raw_symptom_text or " ".join(
        [s.canonical_concept for s in assessment.structured_symptoms if s.status == "POSITIVE"]
    )

    stage_a = pipeline.run_stage_a(
        text=text,
        age_years=assessment.age_years,
        assessment_id=assessment.id,
    )

    reassessed = pipeline.reassess_with_followup_answers(
        original_text=text,
        answers=domain_answers,
        assessment_id=assessment.id,
    )

    # Invariant: final urgency cannot downgrade below initial assessment level
    old_urg = assessment.final_urgency
    new_urg = int(reassessed.final_urgency) if isinstance(reassessed.final_urgency, Urgency) else None

    # Update assessment record in DB
    if new_urg is not None and old_urg is not None:
        assessment.final_urgency = min(old_urg, new_urg)
    elif new_urg is not None:
        assessment.final_urgency = new_urg

    assessment.is_uncertain = reassessed.is_uncertain
    assessment.explanation_text = reassessed.explanation.text if reassessed.explanation else assessment.explanation_text
    assessment.information_incomplete = reassessed.information_incomplete
    assessment.rule_status = reassessed.rule_status.value
    assessment.ml_status = reassessed.ml_status.value
    assessment.llm_status = reassessed.llm_status.value

    db.commit()
    db.refresh(assessment)

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
        followup_questions=[_to_followup_schema(q) for q in reassessed.followup_questions],
        skipped_followup_questions=[_to_followup_schema(q) for q in reassessed.skipped_followup_questions],
    )
