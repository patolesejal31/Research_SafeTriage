"""Authentication endpoints: Registration and Login."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import check_login_rate_limit, reset_login_rate_limit
from app.core.config import settings
from app.core.security import (
    PasswordPolicyError,
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user or researcher account",
)
def register(
    req: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user account with Argon2id password hashing.

    Enforces password complexity: >=8 chars, uppercase, lowercase, digit.
    Returns user details WITHOUT password or hash.
    """
    # Check duplicate email
    existing_user = db.query(User).filter(User.email == req.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Validate role
    role = req.role.lower()
    if role not in ("user", "researcher"):
        role = "user"

    # Hash password with Argon2id (validates complexity internally)
    try:
        hashed = hash_password(req.password)
    except PasswordPolicyError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    user = User(
        email=req.email.lower(),
        hashed_password=hashed,
        role=role,
        opt_in_store_raw_symptoms=req.opt_in_store_raw_symptoms,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
def login(
    req: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Authenticate with Argon2id and return a JWT access token.

    Enforces rate limiting (max 5 failed attempts per minute).
    """
    # Check rate limit before verifying credentials
    check_login_rate_limit(request, email=req.email)

    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Reset rate limit counter on success
    reset_login_rate_limit(request, email=req.email)

    # Create JWT access token
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=expires_delta,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserResponse.model_validate(user),
    )
