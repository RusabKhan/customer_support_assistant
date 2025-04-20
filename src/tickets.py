from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import List


from src.models.schemas import TicketWithMessages, TicketResponse, TicketCreate, MessageCreate
from src.models.enums import Permission
from utils import create_db_url, DB
from utils.db_models.main import User
from utils.request_utils import get_current_user_with_permissions

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("/", response_model=List[TicketResponse])
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_OWN_TICKETS, Permission.VIEW_ALL_TICKETS]))
):
    """
    Retrieve paginated list of tickets for the current user or all, based on permissions.
    """
    with DB(create_db_url()) as db:
        if current_user.has_permission(Permission.VIEW_ALL_TICKETS):
            tickets = db.get_all_tickets_paginated(db.db_session, page=page, page_size=page_size)
        else:
            tickets = db.get_tickets_by_user_paginated(db.db_session, current_user.id, page=page, page_size=page_size)

        return [
            TicketResponse(
                id=ticket.id,
                title=ticket.title,
                content=ticket.description,
                status=ticket.status
            ) for ticket in tickets
        ]


@router.post("/", response_model=TicketResponse)
async def create_ticket(request: TicketCreate, current_user: User = Depends(get_current_user_with_permissions([Permission.CREATE_TICKET]))):
    """
Create a new ticket for the authenticated user.

Args:
    request (TicketCreate): Ticket creation data.
    current_user (User): The currently authenticated user with ticket creation permission.

Returns:
    TicketResponse: The created ticket's details.
"""
    with DB(create_db_url()) as db:
        ticket = db.create_ticket(db.db_session, current_user.id, request.title, request.content)
        return TicketResponse(id=ticket.id, title=ticket.title, content=ticket.description, status=ticket.status)


@router.get("/all", response_model=List[TicketWithMessages])
async def get_all_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_ALL_TICKETS]))
):
    """
    Retrieve paginated list of tickets, each with their messages.
    """
    with DB(create_db_url()) as db:
        tickets = db.get_all_tickets_paginated(db.db_session, page=page, page_size=page_size)
        return [
            TicketWithMessages(
                id=ticket.id,
                title=ticket.title,
                content=ticket.description,
                messages=ticket.messages  # optionally also paginate this
            ) for ticket in tickets
        ]


@router.get("/{ticket_id}", response_model=TicketWithMessages)
async def get_ticket(
    ticket_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_ALL_TICKETS]))
):
    """
    Retrieve a ticket by its ID along with paginated messages.
    """
    with DB(create_db_url()) as db:
        ticket = db.get_ticket(db.db_session, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        messages = db.get_ticket_messages_paginated(
            db.db_session, ticket_id, page=page, page_size=page_size
        )

        return TicketWithMessages(
            id=ticket.id,
            title=ticket.title,
            content=ticket.description,
            messages=messages
        )


@router.post("/{ticket_id}/messages", response_model=MessageCreate)
async def add_message(ticket_id: UUID, request: MessageCreate, current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_ALL_TICKETS]))):
    """
Add a new message to a specified ticket.

Args:
    ticket_id (UUID): Unique identifier of the ticket.
    request (MessageCreate): Message content and AI flag.
    current_user (User): The authenticated user with required permissions.

Returns:
    MessageCreate: The created message details.

Raises:
    HTTPException: If the ticket is not found or the user lacks permissions.
"""
    with DB(create_db_url()) as db:
        ticket = db.get_ticket(db.db_session, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        message = db.create_message(db.db_session, ticket_id, request.content)
        return MessageCreate(content=message.content, is_ai=message.is_ai)


