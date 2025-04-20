import os
from uuid import UUID

from fastapi import Depends, HTTPException, APIRouter, Query
from starlette.responses import JSONResponse

from src.models.schemas import GroqResponse, GroqFollowupInput
from src.models.enums import Permission
from utils import DB, create_db_url
from utils.db_models.main import User
from utils.groq_assistant import GroqAssistant
from utils.request_utils import get_current_user_with_permissions

router = APIRouter(prefix="/groq", tags=["Groq"])


@router.get("/{ticket_id}/ai-response")
async def ai_response(ticket_id: UUID,
                      current_user: User = Depends(get_current_user_with_permissions([Permission.GROQ_ASSISTANT]))):
    """
Generates an AI-powered response for a specified ticket using the GroqAssistant, accessible only to users with the GROQ_ASSISTANT permission.

Args:
    ticket_id (UUID): Unique identifier of the ticket.
    current_user (User, optional): The authenticated user with required permissions.

Returns:
    JSONResponse: Contains the generated AI response for the ticket.

Raises:
    HTTPException: If the ticket is not found or the user lacks permissions.
"""
    with DB(create_db_url()) as db:
        ticket = db.get_ticket_with_messages(db.db_session, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        sorted_messages = sorted(ticket.messages, key=lambda msg: msg.created_at)
        history = [msg.content for msg in sorted_messages[:-1]] if len(sorted_messages) > 1 else []
        latest_message = sorted_messages[-1].content if sorted_messages else ""

        groq_assistant = GroqAssistant(api_key=os.environ["GROQ_API_KEY"])
        groq_response = groq_assistant.generate_response(
            ticket_description=ticket.description,
            message_history=history,
            latest_message=latest_message
        )

        if not groq_response:
            raise HTTPException(status_code=500, detail="Something went wrong. Failed to generate Groq AI response")

        with DB(create_db_url()) as db:
            db.create_message(db.db_session, ticket_id, groq_response,is_ai=True)

        return JSONResponse(content={"groq_response": groq_response}, status_code=200)


@router.get("/groq-response/{ticket_id}", response_model=GroqResponse)
async def get_groq_response(
    ticket_id: UUID,
    page: int = Query(1, ge=1),
    current_user: User = Depends(get_current_user_with_permissions([Permission.GROQ_ASSISTANT]))
):
    with DB(create_db_url()) as db:
        records = db.get_groq_chats_by_ticket_id(db.db_session, ticket_id=ticket_id, page=page)
        messages = [r.content for r in records]
        return GroqResponse(responses=messages)

@router.post("/{ticket_id}/ai-followup")
async def follow_up_with_groq(
    ticket_id: UUID,
    payload: GroqFollowupInput,
    current_user: User = Depends(get_current_user_with_permissions([Permission.GROQ_ASSISTANT]))
):
    """
    Sends a user's reply back to Groq to continue the conversation thread.

    Args:
        ticket_id (UUID): ID of the ticket.
        payload (GroqFollowupInput): User's reply to Groq's previous message.

    Returns:
        JSONResponse: Groq's next response in the thread.
    """
    with DB(create_db_url()) as db:
        ticket = db.get_ticket_with_messages(db.db_session, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        sorted_messages = sorted(ticket.messages, key=lambda msg: msg.created_at)
        conversation = [msg.content for msg in sorted_messages]
        conversation.append(payload.user_reply)

        groq_assistant = GroqAssistant(api_key=os.environ["GROQ_API_KEY"])
        next_response = groq_assistant.generate_response_from_history(conversation)

        if not next_response:
            raise HTTPException(status_code=500, detail="Groq follow-up failed")

        db.create_message(db.db_session, ticket_id, payload.user_reply, is_ai=False)
        db.create_message(db.db_session, ticket_id, next_response, is_ai=True)

        return JSONResponse(content={"groq_response": next_response}, status_code=200)