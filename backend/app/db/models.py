"""SQLAlchemy 2.0 Database Models for SafeTriage.

8 Core Tables:
1. users: Authentication, role (user/researcher), privacy opt-in for raw text storage
2. assessments: Triage assessment outcomes, multi-component levels and statuses
3. structured_symptoms: Structured entities extracted by NLP (no raw phrases)
4. rule_triggers: Deterministic rules matched during triage
5. override_logs: Audit log of escalations/downgrades (NO raw symptom text)
6. evaluation_runs: Research evaluation job records
7. evaluation_predictions: Per-case predictions from evaluation runs
8. experiment_configs: Research experiment parameters and configurations

Clinical Safety & Privacy Constraints:
- raw_symptom_text is NULLABLE and stored ONLY when opt_in_store_raw_symptoms is True.
- Override logs record typed IDs, components, levels, reasons — NEVER user raw text.
- Cascade deletion ensures complete wiping of child records on assessment or user deletion.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class User(Base):
    """User account model supporting 'user' and 'researcher' roles."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)  # "user" or "researcher"
    opt_in_store_raw_symptoms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    # Relationships
    assessments: Mapped[List["Assessment"]] = relationship(
        "Assessment", back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    evaluation_runs: Mapped[List["EvaluationRun"]] = relationship(
        "EvaluationRun", back_populates="creator", cascade="all, delete-orphan", passive_deletes=True
    )


class Assessment(Base):
    """Triage assessment session and outcome."""
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    anonymous_session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Urgency Outcomes (1=Emergency, 2=Urgent, 3=Routine, 4=Self-care, None=UNCERTAIN)
    final_urgency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_uncertain: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rule_urgency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ml_urgency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    llm_urgency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Component Statuses (OK, UNAVAILABLE, ERROR, INVALID, TIMEOUT)
    rule_status: Mapped[str] = mapped_column(String(32), default="UNAVAILABLE", nullable=False)
    ml_status: Mapped[str] = mapped_column(String(32), default="UNAVAILABLE", nullable=False)
    llm_status: Mapped[str] = mapped_column(String(32), default="UNAVAILABLE", nullable=False)

    # Clinical & Safety Metadata
    information_incomplete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    explanation_text: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_source: Mapped[str] = mapped_column(String(32), default="template", nullable=False)
    llm_faithfulness_passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    llm_provider_label: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Demographics (optional, structured)
    age_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    age_band: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    sex: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    # Privacy: raw symptom text stored ONLY if opt-in is True
    opt_in_raw_symptom_storage: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_symptom_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="assessments")
    structured_symptoms: Mapped[List["StructuredSymptom"]] = relationship(
        "StructuredSymptom", back_populates="assessment", cascade="all, delete-orphan", passive_deletes=True
    )
    rule_triggers: Mapped[List["RuleTrigger"]] = relationship(
        "RuleTrigger", back_populates="assessment", cascade="all, delete-orphan", passive_deletes=True
    )
    override_logs: Mapped[List["OverrideLog"]] = relationship(
        "OverrideLog", back_populates="assessment", cascade="all, delete-orphan", passive_deletes=True
    )


class StructuredSymptom(Base):
    """Structured clinical entity extracted by the NLP pipeline."""
    __tablename__ = "structured_symptoms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    canonical_concept: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # POSITIVE, NEGATED, UNCERTAIN
    match_type: Mapped[str] = mapped_column(String(32), nullable=False)  # exact, variant, fuzzy
    fuzzy_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    onset: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    duration: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="structured_symptoms")


class RuleTrigger(Base):
    """Clinical rule matched during assessment."""
    __tablename__ = "rule_triggers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_id: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_level: Mapped[int] = mapped_column(Integer, nullable=False)
    specialty: Mapped[str] = mapped_column(String(64), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), default="UNVERIFIED", nullable=False)

    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="rule_triggers")


class OverrideLog(Base):
    """Audit log of invariant enforcement decisions (escalations, downgrades blocked).

    STRICT CLINICAL INVARIANT:
    Never logs raw symptom text. Uses typed metadata, component names, and levels only.
    """
    __tablename__ = "override_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    component: Mapped[str] = mapped_column(String(32), nullable=False)
    from_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    to_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="override_logs")


class EvaluationRun(Base):
    """Evaluation experiment execution record."""
    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    run_name: Mapped[str] = mapped_column(String(128), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(128), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(64), nullable=False)
    split: Mapped[str] = mapped_column(String(32), default="test", nullable=False)
    total_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="completed", nullable=False)
    metrics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON-serialized metrics
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Relationships
    creator: Mapped["User"] = relationship("User", back_populates="evaluation_runs")
    predictions: Mapped[List["EvaluationPrediction"]] = relationship(
        "EvaluationPrediction", back_populates="run", cascade="all, delete-orphan", passive_deletes=True
    )


class EvaluationPrediction(Base):
    """Per-case prediction for evaluation runs."""
    __tablename__ = "evaluation_predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(String(64), nullable=False)
    ground_truth: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_rule: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    predicted_ml: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    predicted_llm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    predicted_final: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rule_status: Mapped[str] = mapped_column(String(32), default="OK", nullable=False)
    ml_status: Mapped[str] = mapped_column(String(32), default="OK", nullable=False)
    llm_status: Mapped[str] = mapped_column(String(32), default="OK", nullable=False)

    # Relationships
    run: Mapped["EvaluationRun"] = relationship("EvaluationRun", back_populates="predictions")


class ExperimentConfig(Base):
    """Saved experiment configuration parameters for reproducible research."""
    __tablename__ = "experiment_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    config_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
