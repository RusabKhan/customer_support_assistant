from pydantic import BaseModel, Field
from typing import List, Optional
import enum

class Role(str, enum.Enum):
    user = "user"
    admin = "admin"
    support = "support"


class Token(str, enum.Enum):
    access_token = "access_token"
    refresh_token = "refresh_token"
    bearer = "bearer"


class SignupRequest(BaseModel):
    username: str
    password: str
    role: Role


class TokenResponse(BaseModel):
    access_token: str
    token_type: Token.bearer


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
