"""Seed data helper for SafeTriage.

Requirements:
- Seed accounts ONLY with example.com addresses.
- Passwords read from environment variables or secure defaults.
- Never hardcode production credentials.
"""

import os
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models import User


def seed_default_users(db: Session) -> None:
    """Create default test/research accounts if they do not exist."""
    user_email = "user@example.com"
    researcher_email = "researcher@example.com"

    user_password = os.getenv("SEED_USER_PASSWORD", "UserPassword123!")
    researcher_password = os.getenv("SEED_RESEARCHER_PASSWORD", "ResearcherPassword123!")

    # Check and create default regular user
    existing_user = db.query(User).filter(User.email == user_email).first()
    if not existing_user:
        user = User(
            email=user_email,
            hashed_password=hash_password(user_password),
            role="user",
            opt_in_store_raw_symptoms=False,
        )
        db.add(user)

    # Check and create default researcher
    existing_researcher = db.query(User).filter(User.email == researcher_email).first()
    if not existing_researcher:
        researcher = User(
            email=researcher_email,
            hashed_password=hash_password(researcher_password),
            role="researcher",
            opt_in_store_raw_symptoms=False,
        )
        db.add(researcher)

    db.commit()
