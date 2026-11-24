"""Guest Assessment Retention and TTL Cleanup Service.

Safety & Governance Invariants:
- Unauthenticated guest assessments (where user_id is NULL) expire after GUEST_RETENTION_HOURS (default 24h).
- Registered users' assessments are NEVER auto-deleted.
- Cascades deletion to all child rows (structured_symptoms, rule_triggers, override_logs) ensuring no orphans.
- Fully idempotent: multiple runs with the same cutoff produce consistent results.
- Injectable clock parameter (now: Optional[datetime]) enables deterministic unit testing.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Assessment

logger = logging.getLogger("safetriage.services.retention")


def cleanup_guest_assessments(
    db: Session,
    retention_hours: Optional[int] = None,
    now: Optional[datetime] = None,
) -> int:
    """Delete expired guest assessments and associated child records.

    Args:
        db: SQLAlchemy database session.
        retention_hours: Number of hours to retain guest assessments (default settings.GUEST_RETENTION_HOURS).
        now: Current timestamp (injectable for testing). Defaults to timezone.utc now.

    Returns:
        Number of deleted guest assessments.
    """
    hours = retention_hours if retention_hours is not None else settings.GUEST_RETENTION_HOURS
    current_time = now or datetime.now(timezone.utc)
    cutoff = current_time - timedelta(hours=hours)

    # Query expired guest assessments (user_id is None)
    expired = (
        db.query(Assessment)
        .filter(Assessment.user_id.is_(None))
        .filter(Assessment.created_at < cutoff)
        .all()
    )

    count = len(expired)
    if count == 0:
        return 0

    for assessment in expired:
        db.delete(assessment)

    db.commit()
    logger.info("Guest assessment TTL cleanup: deleted %d expired guest records (cutoff: %s)", count, cutoff)
    return count
