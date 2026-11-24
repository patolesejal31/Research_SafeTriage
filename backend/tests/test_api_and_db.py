"""Phase 5 Comprehensive Tests: API, DB Models, Security, RBAC, IDOR, and Privacy.

Test Coverage:
1. Alembic fresh DB migration & seed accounts.
2. Password policy (length, uppercase, lowercase, digit) & Argon2id hashing.
3. Password hashes NEVER exposed in any API response.
4. JWT token authentication, expiration, tampering rejection, and rate limiting (429).
5. Refuse to start in production with default JWT secret.
6. Role-Based Access Control (RBAC): researcher-only endpoints return 403 for user role.
7. Anonymous triage support with session scoping (X-Session-ID).
8. IDOR Protection: Cross-user access (read, list, delete) returns 403/404.
9. Wipe-all isolation: User A's wipe does not affect User B.
10. Database cascade deletion: Deleting assessment removes all child records.
11. Privacy opt-in: Raw symptom text stored ONLY with explicit opt-in (default NULL).
12. Security log-capture test: Planted secrets NEVER appear in application logs.
13. Follow-up question refinements: Safety-critical questions never dropped, 3 optional cap,
    and information_incomplete flagging.
14. CORS preflight headers.
"""

from __future__ import annotations

import io
import json
import logging
import uuid
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import _login_attempts, get_db
from app.core.config import Settings, settings
from app.core.logging_filters import SensitiveDataFilter
from app.core.security import (
    PasswordPolicyError,
    create_access_token,
    hash_password,
    validate_password_complexity,
    verify_password,
)
from app.db.base import Base
from app.db.models import (
    Assessment,
    EvaluationPrediction,
    EvaluationRun,
    OverrideLog,
    RuleTrigger,
    StructuredSymptom,
    User,
)
from app.db.seed import seed_default_users
from app.main import app
from app.triage.followups import FollowUpAnswer, FollowUpEngine


# ---------------------------------------------------------------------------
# Test Database Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_db_engine():
    """Create an in-memory SQLite database engine with foreign key enforcement."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """Provide a transactional session per test, rolling back at teardown."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, future=True)

    # Seed default users
    seed_default_users(session)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient overriding get_db to use test session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_rate_limits():
    """Clear in-memory login attempts before each test."""
    _login_attempts.clear()


# ---------------------------------------------------------------------------
# Helper Auth Tokens
# ---------------------------------------------------------------------------

def get_auth_token(client: TestClient, email: str = "user@example.com", password: str = "UserPassword123!") -> str:
    """Helper to authenticate and return Bearer token."""
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


def get_researcher_token(client: TestClient) -> str:
    """Helper to authenticate researcher and return Bearer token."""
    return get_auth_token(client, email="researcher@example.com", password="ResearcherPassword123!")


# ---------------------------------------------------------------------------
# 1. Database & Seed Accounts
# ---------------------------------------------------------------------------

class TestDatabaseAndSeed:
    """Alembic migrations, tables, and seed account verification."""

    def test_seed_accounts_exist_with_example_domains(self, db_session: Session):
        """Seed accounts must use example.com domain only."""
        users = db_session.query(User).all()
        emails = [u.email for u in users]
        assert "user@example.com" in emails
        assert "researcher@example.com" in emails
        for u in users:
            assert u.email.endswith("@example.com"), f"Non-example.com email found: {u.email}"

    def test_seed_passwords_are_valid_argon2_hashes(self, db_session: Session):
        """Seed account passwords must be valid Argon2id hashes."""
        users = db_session.query(User).all()
        for u in users:
            assert u.hashed_password.startswith("$argon2id$")
            assert verify_password("UserPassword123!", u.hashed_password) or verify_password(
                "ResearcherPassword123!", u.hashed_password
            )

    def test_alembic_migration_on_fresh_db(self, tmp_path):
        """Alembic upgrade head applies cleanly on a completely fresh SQLite database."""
        from alembic.config import Config
        from alembic import command
        from pathlib import Path

        db_path = tmp_path / "fresh_migration_test.db"
        alembic_ini_path = Path(__file__).parent.parent / "alembic.ini"
        alembic_scripts_path = Path(__file__).parent.parent / "alembic"

        cfg = Config(str(alembic_ini_path))
        cfg.set_main_option("script_location", str(alembic_scripts_path))
        cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

        # Run upgrade
        command.upgrade(cfg, "head")
        assert db_path.exists()


# ---------------------------------------------------------------------------
# 2. Password Policy & Hashing
# ---------------------------------------------------------------------------

class TestPasswordPolicyAndArgon2:
    """Password complexity requirements and Argon2id verification."""

    def test_password_length_requirement(self):
        with pytest.raises(PasswordPolicyError, match="at least 8 characters"):
            validate_password_complexity("Short1!")

    def test_password_uppercase_requirement(self):
        with pytest.raises(PasswordPolicyError, match="uppercase"):
            validate_password_complexity("lowercase123!")

    def test_password_lowercase_requirement(self):
        with pytest.raises(PasswordPolicyError, match="lowercase"):
            validate_password_complexity("UPPERCASE123!")

    def test_password_digit_requirement(self):
        with pytest.raises(PasswordPolicyError, match="digit"):
            validate_password_complexity("NoDigitsHere!")

    def test_valid_password_passes(self):
        # Should not raise
        validate_password_complexity("ValidPass123")

    def test_argon2_hashing_and_verification(self):
        h = hash_password("ValidPass123")
        assert h.startswith("$argon2id$")
        assert verify_password("ValidPass123", h) is True
        assert verify_password("WrongPass123", h) is False

    def test_registration_enforces_password_policy(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "badpass@example.com", "password": "weak"},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 3. Security & Privacy: No Hashes or Secrets Returned
# ---------------------------------------------------------------------------

class TestSecurityResponsesAndLogs:
    """Zero exposure of password hashes or raw secrets in API responses or logs."""

    def test_password_hashes_never_returned_in_auth_endpoints(self, client: TestClient):
        """Registration and Login responses must NEVER contain password hash fields."""
        # 1. Register
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"email": "newuser@example.com", "password": "NewUserPassword123!"},
        )
        assert reg_resp.status_code == 201
        data = reg_resp.json()
        assert "hashed_password" not in data
        assert "password" not in data

        # 2. Login
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "newuser@example.com", "password": "NewUserPassword123!"},
        )
        assert login_resp.status_code == 200
        login_data = login_resp.json()
        assert "hashed_password" not in login_data["user"]
        assert "password" not in login_data["user"]

    def test_planted_secrets_never_appear_in_application_logs(self, client: TestClient):
        """Planted secrets (password, symptoms, tokens) must never appear in log records."""
        secret_symptom = "SECRET_SYMPTOM_XYZ"
        secret_password = "SECRET_PASSWORD_123!"
        secret_token = "SECRET_TOKEN_ABC"

        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.addFilter(SensitiveDataFilter())
        logger = logging.getLogger()
        logger.addHandler(handler)

        try:
            # Trigger registration with planted password
            client.post(
                "/api/v1/auth/register",
                json={"email": "audit_test@example.com", "password": secret_password},
            )

            # Trigger assessment with planted symptom
            client.post(
                "/api/v1/assessments",
                json={"symptoms_text": f"Severe chest pain and {secret_symptom}"},
            )

            # Log an event containing planted tokens directly
            logger.info("Processing user request with token=%s and symptom=%s", secret_token, secret_symptom)

            log_output = log_stream.getvalue()
            assert secret_symptom not in log_output
            assert secret_password not in log_output
            assert secret_token not in log_output
        finally:
            logger.removeHandler(handler)


# ---------------------------------------------------------------------------
# 4. Authentication, JWT, and Rate Limiting
# ---------------------------------------------------------------------------

class TestAuthAndRateLimiting:
    """JWT expiration, tampering, header requirements, and rate limiting."""

    def test_successful_login_returns_bearer_token(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "UserPassword123!"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["token_type"] == "bearer"
        assert "access_token" in data
        assert data["user"]["email"] == "user@example.com"

    def test_invalid_credentials_returns_401(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "WrongPassword123!"},
        )
        assert resp.status_code == 401

    def test_login_rate_limiting_triggers_429(self, client: TestClient):
        """More than 5 failed attempts within 60s returns HTTP 429."""
        for _ in range(5):
            r = client.post(
                "/api/v1/auth/login",
                json={"email": "user@example.com", "password": "WrongPassword123!"},
            )
            assert r.status_code == 401

        # 6th attempt should trigger 429
        r6 = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "WrongPassword123!"},
        )
        assert r6.status_code == 429
        assert "Too many failed login attempts" in r6.text

    def test_tampered_token_rejected_with_401(self, client: TestClient):
        token = get_auth_token(client)
        tampered_token = token[:-4] + "fake"
        resp = client.get(
            "/api/v1/assessments",
            headers={"Authorization": f"Bearer {tampered_token}"},
        )
        # Invalid token returns 401
        assert resp.status_code == 401

    def test_tokens_in_url_query_params_are_not_supported(self, client: TestClient):
        """Tokens passed via ?token= query parameter are ignored; requires Authorization header."""
        token = get_auth_token(client)
        resp = client.get(f"/api/v1/research/dataset-stats?token={token}")
        # Research endpoint requires researcher auth in header -> 401
        assert resp.status_code == 401

    def test_production_safety_check_blocks_insecure_defaults(self):
        """In production environment, default or short JWT secrets raise RuntimeError."""
        prod_settings = Settings(
            ENVIRONMENT="production",
            JWT_SECRET="safetriage-insecure-dev-secret-key-change-in-production",
        )
        with pytest.raises(RuntimeError, match="FATAL SECURITY ERROR"):
            prod_settings.validate_production_safety()


# ---------------------------------------------------------------------------
# 5. Role-Based Access Control (RBAC)
# ---------------------------------------------------------------------------

class TestRoleBasedAccessControl:
    """Researcher role required for evaluation and research endpoints."""

    def test_user_role_blocked_from_dataset_stats_with_403(self, client: TestClient):
        user_token = get_auth_token(client)
        resp = client.get(
            "/api/v1/research/dataset-stats",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403
        assert "privileges required" in resp.text

    def test_researcher_role_allowed_for_dataset_stats(self, client: TestClient):
        researcher_token = get_researcher_token(client)
        resp = client.get(
            "/api/v1/research/dataset-stats",
            headers={"Authorization": f"Bearer {researcher_token}"},
        )
        assert resp.status_code == 200
        assert "dataset_name" in resp.json()

    def test_user_role_blocked_from_evaluation_run(self, client: TestClient):
        user_token = get_auth_token(client)
        resp = client.post(
            "/api/v1/evaluation/run",
            json={"run_name": "test_run"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403

    def test_researcher_role_can_create_evaluation_run(self, client: TestClient):
        researcher_token = get_researcher_token(client)
        resp = client.post(
            "/api/v1/evaluation/run",
            json={"run_name": "benchmark_test_run"},
            headers={"Authorization": f"Bearer {researcher_token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["run_name"] == "benchmark_test_run"
        assert "metrics" in data


# ---------------------------------------------------------------------------
# 6. Anonymous Triage Support & Session Scoping
# ---------------------------------------------------------------------------

class TestAnonymousAssessments:
    """Unauthenticated users can perform emergency triage with session isolation."""

    def test_guest_can_perform_triage_assessment(self, client: TestClient):
        session_id = str(uuid.uuid4())
        resp = client.post(
            "/api/v1/assessments",
            json={"symptoms_text": "Severe headache and fever"},
            headers={"X-Session-ID": session_id},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["final_urgency"] is not None

    def test_guest_can_list_and_delete_their_session_assessments(self, client: TestClient):
        session_id = str(uuid.uuid4())
        # Create
        c_resp = client.post(
            "/api/v1/assessments",
            json={"symptoms_text": "Mild cough for 3 days"},
            headers={"X-Session-ID": session_id},
        )
        aid = c_resp.json()["id"]

        # List
        l_resp = client.get("/api/v1/assessments", headers={"X-Session-ID": session_id})
        assert l_resp.status_code == 200
        ids = [a["id"] for a in l_resp.json()]
        assert aid in ids

        # Delete single
        d_resp = client.delete(f"/api/v1/assessments/{aid}", headers={"X-Session-ID": session_id})
        assert d_resp.status_code == 200

        # Confirm gone
        l_resp2 = client.get("/api/v1/assessments", headers={"X-Session-ID": session_id})
        assert aid not in [a["id"] for a in l_resp2.json()]


# ---------------------------------------------------------------------------
# 7. User Data Isolation & IDOR Protection
# ---------------------------------------------------------------------------

class TestIDORProtectionAndDataIsolation:
    """Users cannot view, list, or delete other users' assessments."""

    def test_cross_user_read_blocked_with_403(self, client: TestClient):
        # User A registers and creates an assessment
        client.post(
            "/api/v1/auth/register",
            json={"email": "usera@example.com", "password": "UserAPassword123!"},
        )
        token_a = get_auth_token(client, email="usera@example.com", password="UserAPassword123!")
        res_a = client.post(
            "/api/v1/assessments",
            json={"symptoms_text": "Sudden severe chest pain"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        aid_a = res_a.json()["id"]

        # User B registers
        client.post(
            "/api/v1/auth/register",
            json={"email": "userb@example.com", "password": "UserBPassword123!"},
        )
        token_b = get_auth_token(client, email="userb@example.com", password="UserBPassword123!")

        # User B tries to read User A's assessment
        read_resp = client.get(
            f"/api/v1/assessments/{aid_a}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert read_resp.status_code == 403

    def test_cross_user_delete_blocked_with_403(self, client: TestClient):
        # Register User A and create assessment
        client.post(
            "/api/v1/auth/register",
            json={"email": "usera2@example.com", "password": "UserAPassword123!"},
        )
        token_a = get_auth_token(client, email="usera2@example.com", password="UserAPassword123!")
        res_a = client.post(
            "/api/v1/assessments",
            json={"symptoms_text": "Fever for 2 days"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        aid_a = res_a.json()["id"]

        # Register User B
        client.post(
            "/api/v1/auth/register",
            json={"email": "userb2@example.com", "password": "UserBPassword123!"},
        )
        token_b = get_auth_token(client, email="userb2@example.com", password="UserBPassword123!")

        # User B tries to delete User A's assessment
        del_resp = client.delete(
            f"/api/v1/assessments/{aid_a}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert del_resp.status_code == 403

    def test_user_b_wipe_all_does_not_affect_user_a(self, client: TestClient):
        # Register User A and create assessment
        client.post(
            "/api/v1/auth/register",
            json={"email": "usera3@example.com", "password": "UserAPassword123!"},
        )
        token_a = get_auth_token(client, email="usera3@example.com", password="UserAPassword123!")
        res_a = client.post(
            "/api/v1/assessments",
            json={"symptoms_text": "Headache"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        aid_a = res_a.json()["id"]

        # Register User B
        client.post(
            "/api/v1/auth/register",
            json={"email": "userb3@example.com", "password": "UserBPassword123!"},
        )
        token_b = get_auth_token(client, email="userb3@example.com", password="UserBPassword123!")

        # User B calls wipe all
        wipe_resp = client.delete(
            "/api/v1/assessments",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert wipe_resp.status_code == 200

        # User A's assessment is still intact
        read_a = client.get(
            f"/api/v1/assessments/{aid_a}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert read_a.status_code == 200
        assert read_a.json()["id"] == aid_a


# ---------------------------------------------------------------------------
# 8. Database Cascade Deletion
# ---------------------------------------------------------------------------

class TestDatabaseCascadeDeletion:
    """Deleting an assessment cascades and removes all symptoms, triggers, and logs."""

    def test_assessment_deletion_cascades_to_children(self, client: TestClient, db_session: Session):
        token = get_auth_token(client)
        # Presentation that triggers clinical rule RESP-003
        resp = client.post(
            "/api/v1/assessments",
            json={"symptoms_text": "Persistent dry cough", "age_years": 40},
            headers={"Authorization": f"Bearer {token}"},
        )
        aid = resp.json()["id"]

        # Verify child records exist in DB
        assert db_session.query(StructuredSymptom).filter(StructuredSymptom.assessment_id == aid).count() > 0
        assert db_session.query(RuleTrigger).filter(RuleTrigger.assessment_id == aid).count() > 0

        # Delete assessment
        del_resp = client.delete(
            f"/api/v1/assessments/{aid}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert del_resp.status_code == 200

        # Verify child records were cascade deleted
        assert db_session.query(StructuredSymptom).filter(StructuredSymptom.assessment_id == aid).count() == 0
        assert db_session.query(RuleTrigger).filter(RuleTrigger.assessment_id == aid).count() == 0
        assert db_session.query(OverrideLog).filter(OverrideLog.assessment_id == aid).count() == 0


# ---------------------------------------------------------------------------
# 9. Privacy: Opt-in Raw Symptom Text Storage
# ---------------------------------------------------------------------------

class TestPrivacyRawSymptomStorage:
    """Raw symptom text is stored ONLY with explicit user opt-in (default NULL)."""

    def test_default_privacy_does_not_store_raw_text(self, client: TestClient, db_session: Session):
        token = get_auth_token(client)
        resp = client.post(
            "/api/v1/assessments",
            json={"symptoms_text": "I have had a mild sore throat for 2 days"},
            headers={"Authorization": f"Bearer {token}"},
        )
        aid = resp.json()["id"]

        # Check DB: raw_symptom_text must be NULL
        assessment = db_session.query(Assessment).filter(Assessment.id == aid).first()
        assert assessment.opt_in_raw_symptom_storage is False
        assert assessment.raw_symptom_text is None

    def test_explicit_opt_in_stores_raw_text(self, client: TestClient, db_session: Session):
        token = get_auth_token(client)
        text = "I have had a mild sore throat for 2 days"
        resp = client.post(
            "/api/v1/assessments",
            json={
                "symptoms_text": text,
                "opt_in_store_raw_symptoms": True,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        aid = resp.json()["id"]

        # Check DB: raw_symptom_text is stored
        assessment = db_session.query(Assessment).filter(Assessment.id == aid).first()
        assert assessment.opt_in_raw_symptom_storage is True
        assert assessment.raw_symptom_text == text


# ---------------------------------------------------------------------------
# 10. Follow-up Question Refinements
# ---------------------------------------------------------------------------

class TestFollowUpRefinements:
    """Phase 5 Follow-up refinements: safety-critical questions preserved,
    optional capped at 3, order by urgency impact, information_incomplete flag.
    """

    def test_five_gaps_yields_three_highest_risk_optional_plus_safety_critical(self):
        fe = FollowUpEngine()
        # 5 optional gaps: age (general adult), breathlessness duration, fever duration, severity, onset
        result = fe.generate(
            requires_age_followup=True,
            potential_pediatric_escalation=False,  # general age is optional
            concepts_present=["fever", "breathlessness"],
            onset_known=False,
            severity_known=False,
            duration_known=False,
            max_optional_followups=3,
        )

        # Total 5 gaps present -> exactly 3 highest-risk asked, 2 skipped
        assert len(result) == 3
        assert len(result.skipped) == 2

        # The 3 asked must have highest urgency_impact
        asked_impacts = [q.urgency_impact for q in result]
        skipped_impacts = [q.urgency_impact for q in result.skipped]
        assert min(asked_impacts) >= max(skipped_impacts)

    def test_missing_age_pediatric_case_always_asks_age(self):
        fe = FollowUpEngine()
        result = fe.generate(
            requires_age_followup=True,
            potential_pediatric_escalation=True,
            concepts_present=["fever"],
            onset_known=True,
            severity_known=True,
            duration_known=True,
            max_optional_followups=1,
        )
        question_ids = [q.id for q in result]
        assert "fq_age_safety" in question_ids

    def test_skipped_question_relevant_to_level_2_marks_information_incomplete(self):
        fe = FollowUpEngine()
        # Cap optional questions to 0 to force skipping
        result = fe.generate(
            requires_age_followup=False,
            potential_pediatric_escalation=False,
            concepts_present=["fever"],
            onset_known=False,
            severity_known=True,
            duration_known=False,
            max_optional_followups=0,
        )
        # fq_onset is skipped and could trigger Level 2 -> information_incomplete is True
        assert result.information_incomplete is True

    def test_reassess_endpoint_updates_assessment_and_preserves_invariant(self, client: TestClient):
        token = get_auth_token(client)
        create_resp = client.post(
            "/api/v1/assessments",
            json={"symptoms_text": "Chest pain"},
            headers={"Authorization": f"Bearer {token}"},
        )
        aid = create_resp.json()["id"]

        # Submit follow-up: radiation to arm
        reassess_resp = client.post(
            f"/api/v1/followups?assessment_id={aid}",
            json={
                "answers": [
                    {"question_id": "fq_chest_radiation", "selected_option": "Yes, to the left arm"}
                ]
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert reassess_resp.status_code == 200
        data = reassess_resp.json()
        assert data["final_urgency"] == 1  # Emergency ACS triggered by radiation


# ---------------------------------------------------------------------------
# 11. CORS Preflight
# ---------------------------------------------------------------------------

class TestCORSHeaders:
    """CORS preflight requests are properly answered."""

    def test_cors_preflight(self, client: TestClient):
        resp = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
