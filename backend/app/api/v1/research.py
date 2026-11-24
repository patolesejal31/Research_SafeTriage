"""Research API endpoints: Dataset statistics and research queries."""

import json
from pathlib import Path
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.models import User
from app.db.session import get_db
from app.schemas.evaluation import DatasetStatsResponse

router = APIRouter(prefix="/research", tags=["Research"])


@router.get(
    "/dataset-stats",
    response_model=DatasetStatsResponse,
    summary="Get research dataset statistics (Researcher role only)",
)
def get_dataset_stats(
    current_user: User = Depends(require_role("researcher")),
    db: Session = Depends(get_db),
):
    """Return dataset distribution and summary statistics for research.

    Protected: Only accounts with role='researcher' may access this endpoint.
    Regular 'user' accounts receive HTTP 403 Forbidden.
    """
    fixture_path = Path(__file__).parent.parent.parent.parent.parent / "datasets" / "test_fixture" / "fixture.json"

    total = 0
    urgency_dist = {"1": 0, "2": 0, "3": 0, "4": 0, "UNCERTAIN": 0}
    split_counts = {"test_fixture": 0, "validation": 0, "test": 0}

    if fixture_path.exists():
        try:
            with open(fixture_path, "r", encoding="utf-8") as f:
                cases = json.load(f)
            total = len(cases)
            split_counts["test_fixture"] = total
            for c in cases:
                gt = str(c.get("ground_truth_urgency", "UNCERTAIN"))
                urgency_dist[gt] = urgency_dist.get(gt, 0) + 1
        except Exception:
            pass

    return DatasetStatsResponse(
        dataset_name="SafeTriage Research Dataset",
        dataset_version="1.0.0",
        total_cases=total,
        split_counts=split_counts,
        urgency_distribution=urgency_dist,
    )
