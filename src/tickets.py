from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from uuid import UUID
from typing import List


from models.schemas import TicketWithMessages, TicketResponse, TicketCreate, MessageCreate
from models.enums import Role, Permission
from utils import create_db_url, get_db, DB
from utils.db_models.main import User
from utils.request_utils import get_current_user_with_permissions

router = APIRouter()


@router.get("/tickets", response_model=List[TicketResponse])
def list_tickets( current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_OWN_TICKETS, Permission.VIEW_ALL_TICKETS]))):
    with DB(create_db_url()) as db:
        tickets = db.get_tickets_by_user(db.db_session, current_user.id)
        return [TicketResponse(id=ticket.id, title=ticket.title, content=ticket.description, status=ticket.status) for ticket in tickets]


@router.post("/tickets", response_model=TicketResponse)
def create_ticket(request: TicketCreate, current_user: User = Depends(get_current_user_with_permissions([Permission.CREATE_TICKET]))):
    with DB(create_db_url()) as db:
        ticket = db.create_ticket(db.db_session, current_user.id, request.title, request.content)
        return TicketResponse(id=ticket.id, title=ticket.title, content=ticket.description, status=ticket.status)


@router.get("/tickets/all", response_model=List[TicketWithMessages])
def get_all_tickets(current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_ALL_TICKETS]))):
    with DB(create_db_url()) as db:
        tickets = db.get_all_tickets(db.db_session)
        return [
            TicketWithMessages(
                id=ticket.id,
                title=ticket.title,
                content=ticket.description,
                messages=ticket.messages
            ) for ticket in tickets
        ]

@router.get("/tickets/{ticket_id}", response_model=TicketWithMessages)
def get_ticket(ticket_id: UUID, current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_ALL_TICKETS]))):
    with DB(create_db_url()) as db:
        ticket = db.get_ticket_with_messages(db.db_session, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return TicketWithMessages(
            id=ticket.id,
            title=ticket.title,
            content=ticket.description,
            messages=ticket.messages
        )

@router.post("/tickets/{ticket_id}/messages", response_model=MessageCreate)
def add_message(ticket_id: UUID, request: MessageCreate, current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_ALL_TICKETS]))):

    with DB(create_db_url()) as db:
        ticket = db.get_ticket(db.db_session, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        message = db.create_message(db.db_session, ticket_id, request.content)
        return MessageCreate(content=message.content, is_ai=message.is_ai)


@router.get("/tickets/{ticket_id}/ai-response")
async def ai_response(ticket_id: UUID, current_user: User = Depends(get_current_user_with_permissions([Permission.GROQ_ASSISTANT]))):

    with DB(create_db_url()) as db:
        ticket = db.get_ticket(db.db_session, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        groq_response = f"AI response for ticket {ticket_id}"
        return JSONResponse(content={"groq_response": groq_response}, status_code=200)

