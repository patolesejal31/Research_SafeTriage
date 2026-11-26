"""Authentication Pydantic schemas.

STRICT CLINICAL / SECURITY INVARIANT:
- Password hashes and raw passwords must NEVER be included in outgoing schemas.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Must meet password complexity requirements")
    role: str = Field(default="user", description="'user' or 'researcher'")
    opt_in_store_raw_symptoms: bool = Field(
        default=False,
        description="Explicit opt-in to store raw symptom text. Defaults to False (privacy first).",
    )


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    opt_in_store_raw_symptoms: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserResponse
