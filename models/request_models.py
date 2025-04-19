from pydantic import BaseModel, Field
from typing import List, Optional


# User Models
class SignupRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Ticket Models
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


# Message Model
class MessageCreate(BaseModel):
    content: str
