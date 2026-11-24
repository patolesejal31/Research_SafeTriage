"""SafeTriage FastAPI Application Entry Point.

Safety & Governance:
- Refuses to start in production if JWT_SECRET is the default or insecure.
- Strict CORS configuration.
- Argon2id authentication and IDOR protection.
- Sensitive data filter applied to root logger to prevent logging symptom text, tokens, or passwords.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging_filters import SensitiveDataFilter
from app.db.base import Base
from app.db.seed import seed_default_users
from app.db.session import SessionLocal, engine

# Apply sensitive data filter to logging
root_logger = logging.getLogger()
filter_present = any(isinstance(f, SensitiveDataFilter) for f in root_logger.filters)
if not filter_present:
    root_logger.addFilter(SensitiveDataFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan handler."""
    # 1. Enforce production safety invariant: check secret key
    settings.validate_production_safety()

    # 2. Ensure database schema exists (creates tables if not present)
    Base.metadata.create_all(bind=engine)

    # 3. Seed default accounts (user@example.com, researcher@example.com)
    db = SessionLocal()
    try:
        seed_default_users(db)
        # 4. Perform idempotent guest assessment cleanup on startup
        from app.services.retention import cleanup_guest_assessments
        cleanup_guest_assessments(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "SafeTriage Preliminary Medical Symptom Triage Research Prototype. "
        "Strictly non-diagnostic and non-prescriptive."
    ),
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
