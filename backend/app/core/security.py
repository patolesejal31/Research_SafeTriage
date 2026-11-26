"""Security utilities for SafeTriage: Argon2id hashing, Password Policy, and JWT handling.

Clinical Informatics & Security Invariants:
- Passwords hashed using Argon2id (memory-hard, resistant to GPU/ASIC cracking).
- Password policy enforced: >= 8 characters, >= 1 uppercase, >= 1 lowercase, >= 1 digit.
- JWT tokens signed with HS256, have strict expiration, and are NEVER accepted via query parameters.
- Password hashes and raw credentials must NEVER be logged or returned in responses.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from jose import jwt

from app.core.config import settings

# Initialize Argon2id password hasher with recommended RFC 9106 parameters
ph = PasswordHasher(
    time_cost=2,
    memory_cost=19456,  # 19 MiB
    parallelism=1,
    hash_len=32,
)


class PasswordPolicyError(ValueError):
    """Raised when a password does not meet the complexity requirements."""
    pass


def validate_password_complexity(password: str) -> None:
    """Validate that the password satisfies security requirements.

    Requirements:
    - Minimum length: 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 decimal digit
    """
    if len(password) < 8:
        raise PasswordPolicyError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise PasswordPolicyError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise PasswordPolicyError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise PasswordPolicyError("Password must contain at least one digit.")


def hash_password(password: str) -> str:
    """Hash password using Argon2id. Enforces complexity check before hashing."""
    validate_password_complexity(password)
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored Argon2id hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError):
        return False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token with an expiration time."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token.

    Raises:
        JWTError: If token is invalid, expired, or tampered with.
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
