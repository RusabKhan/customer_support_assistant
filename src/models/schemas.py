from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional
import re
import enum

from models.user_roles import Role


class Token(str, enum.Enum):
    access_token = "access_token"
    refresh_token = "refresh_token"
    bearer = "bearer"


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: Role

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        return value

class SignupResponse(BaseModel):
    email: str
    role: Role
    created_at: datetime

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    id: UUID
    user_id: UUID
    token: str
    expires_at: datetime
    created_at: datetime
    revoked_at: Optional[datetime] = None
    token_type: str = "bearer"

    class Config:
        orm_mode = True


class TicketCreate(BaseModel):
    title: str = Field(..., max_length=100)
    content: str


class TicketResponse(BaseModel):
    id: int
    title: str
    content: str


class TicketWithMessages(BaseModel):
    id: int
    title: str
    content: str
    messages: List[str]


class MessageCreate(BaseModel):
    content: str
