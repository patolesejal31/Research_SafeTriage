"""API Dependencies: Database, Authentication, Role Verification, and Rate Limiting."""

import time
from typing import Dict, List, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_db

# Bearer security scheme. auto_error=False allows optional auth for guest assessments.
security_scheme = HTTPBearer(auto_error=False)

# In-memory sliding-window rate limiter for login attempts: {identifier: [timestamp, ...]}
_login_attempts: Dict[str, List[float]] = {}


def check_login_rate_limit(request: Request, email: Optional[str] = None) -> None:
    """Enforce login rate limiting (max attempts per minute).

    Raises:
        HTTPException(429): If rate limit is exceeded.
    """
    now = time.time()
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{email.lower()}" if email else client_ip

    window = settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS
    max_attempts = settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS

    # Clean old timestamps
    attempts = [t for t in _login_attempts.get(key, []) if now - t < window]
    if len(attempts) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again after 60 seconds.",
        )
    attempts.append(now)
    _login_attempts[key] = attempts


def reset_login_rate_limit(request: Request, email: Optional[str] = None) -> None:
    """Reset rate limit counter on successful login."""
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{email.lower()}" if email else client_ip
    _login_attempts.pop(key, None)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate Bearer JWT token and return the authenticated User.

    Raises:
        HTTPException(401): If token is missing, invalid, expired, or user not found.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Bearer token missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Return authenticated User if valid Bearer token provided, None if no header.

    Raises:
        HTTPException(401): If an Authorization header is provided but invalid/expired/tampered.
    """
    if not credentials or not credentials.credentials:
        return None

    try:
        payload = decode_access_token(credentials.credentials)
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(required_role: str):
    """Factory dependency enforcing a specific role ('researcher', 'user').

    Raises:
        HTTPException(403): If the user does not possess the required role.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: '{required_role}' privileges required.",
            )
        return current_user

    return role_checker
