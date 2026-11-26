"""Assessment schemas for triage requests and responses."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class StructuredSymptomSchema(BaseModel):
    canonical_concept: str
    status: str
    match_type: str
    fuzzy_score: Optional[float] = None
    onset: Optional[str] = None
    severity: Optional[str] = None
    duration: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RuleTriggerSchema(BaseModel):
    rule_id: str
    rule_name: str
    rule_level: int
    specialty: str
    review_status: str

    model_config = ConfigDict(from_attributes=True)


class FollowUpQuestionSchema(BaseModel):
    id: str
    type: str
    text: str
    safety_critical: bool
    urgency_impact: int
    could_trigger_level_2: bool
    options: List[str]
    free_numeric: bool
    context_concept: Optional[str] = None


class AssessmentCreateRequest(BaseModel):
    symptoms_text: str = Field(..., min_length=1, description="Raw symptoms description from patient")
    age_years: Optional[float] = Field(default=None, ge=0, le=130)
    age_months: Optional[float] = Field(default=None, ge=0, le=36)
    sex: Optional[str] = Field(default=None, description="male, female, other, prefer_not_to_say")
    opt_in_store_raw_symptoms: Optional[bool] = Field(
        default=None,
        description="Override user privacy setting for this assessment session only",
    )
    max_optional_followups: Optional[int] = Field(default=3, ge=0, le=10)


class AssessmentResponse(BaseModel):
    id: str
    assessment_id: Optional[str] = None
    created_at: datetime
    final_urgency: Optional[int] = None
    is_uncertain: bool
    is_level_1_emergency: bool

    # Component Breakdown
    rule_urgency: Optional[int] = None
    ml_urgency: Optional[int] = None
    llm_urgency: Optional[int] = None
    rule_status: str
    ml_status: str
    llm_status: str

    # Explanation and Safety
    information_incomplete: bool
    explanation_text: str
    explanation_source: str
    llm_faithfulness_passed: Optional[bool] = None
    llm_provider_label: Optional[str] = None

    # Demographics
    age_years: Optional[float] = None
    age_band: Optional[str] = None
    sex: Optional[str] = None

    # Privacy & Retention
    raw_symptom_text: Optional[str] = None
    guest_retention_notice: Optional[str] = None

    # Structured Extractions and Rules
    structured_symptoms: List[StructuredSymptomSchema] = []
    rule_triggers: List[RuleTriggerSchema] = []

    # Follow-up Questions
    followup_questions: List[FollowUpQuestionSchema] = []
    skipped_followup_questions: List[FollowUpQuestionSchema] = []

    model_config = ConfigDict(from_attributes=True)


class AssessmentSummaryResponse(BaseModel):
    id: str
    assessment_id: Optional[str] = None
    created_at: datetime
    final_urgency: Optional[int] = None
    is_uncertain: bool
    is_level_1_emergency: bool
    information_incomplete: bool
    rule_status: str
    ml_status: str
    llm_status: str

    model_config = ConfigDict(from_attributes=True)


class FollowUpAnswerInput(BaseModel):
    question_id: str
    selected_option: Optional[str] = None
    numeric_value: Optional[float] = None


class FollowUpSubmitRequest(BaseModel):
    answers: List[FollowUpAnswerInput]
