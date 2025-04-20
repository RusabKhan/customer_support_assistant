from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List


from src.models.schemas import TicketWithMessages, TicketResponse, TicketCreate, MessageCreate
from src.models.enums import Permission
from utils import create_db_url, DB
from utils.db_models.main import User
from utils.request_utils import get_current_user_with_permissions

router = APIRouter()


@router.get("/tickets", response_model=List[TicketResponse])
async def list_tickets( current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_OWN_TICKETS, Permission.VIEW_ALL_TICKETS]))):
    """
Retrieve a list of tickets belonging to the current user.

Requires the user to have either VIEW_OWN_TICKETS or VIEW_ALL_TICKETS permission.

Returns:
    List[TicketResponse]: A list of ticket summaries for the authenticated user.
"""
    with DB(create_db_url()) as db:
        tickets = db.get_tickets_by_user(db.db_session, current_user.id)
        return [TicketResponse(id=ticket.id, title=ticket.title, content=ticket.description, status=ticket.status) for ticket in tickets]


@router.post("/tickets", response_model=TicketResponse)
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


@router.get("/tickets/all", response_model=List[TicketWithMessages])
async def get_all_tickets(current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_ALL_TICKETS]))):
    """
Retrieve all tickets with their associated messages.

Requires the current user to have the VIEW_ALL_TICKETS permission.

Args:
    current_user (User): The authenticated user with required permissions.

Returns:
    List[TicketWithMessages]: A list of all tickets, each including its messages.
"""
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
async def get_ticket(ticket_id: UUID, current_user: User = Depends(get_current_user_with_permissions([Permission.VIEW_ALL_TICKETS]))):
    """
Retrieve a ticket by its ID along with all associated messages.

Args:
    ticket_id (UUID): Unique identifier of the ticket.
    current_user (User): The authenticated user with required permissions.

Returns:
    TicketWithMessages: The ticket details and its messages.

Raises:
    HTTPException: If the ticket is not found or the user lacks permissions.
"""
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


