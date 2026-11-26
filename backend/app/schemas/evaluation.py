"""Evaluation and Research Schemas."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class EvaluationRunCreateRequest(BaseModel):
    run_name: str = Field(..., min_length=1, max_length=128)
    dataset_name: str = Field(default="vignettes", max_length=128)
    dataset_version: str = Field(default="1.0.0", max_length=64)
    split: str = Field(default="test", max_length=32)


class EvaluationRunResponse(BaseModel):
    id: str
    run_name: str
    dataset_name: str
    dataset_version: str
    split: str
    total_cases: int
    status: str
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetStatsResponse(BaseModel):
    dataset_name: str
    dataset_version: str
    total_cases: int
    split_counts: Dict[str, int]
    urgency_distribution: Dict[str, int]
