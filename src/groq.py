import os
from uuid import UUID

from fastapi import Depends, HTTPException, APIRouter
from starlette.responses import JSONResponse

from src.models.enums import Permission
from utils import DB, create_db_url
from utils.db_models.main import User
from utils.groq_assistant import GroqAssistant
from utils.request_utils import get_current_user_with_permissions

router = APIRouter(prefix="/groq", tags=["Groq", "GROQ_ASSISTANT", "AI"])

@router.get("{ticket_id}/ai-response")
async def ai_response(ticket_id: UUID, current_user: User = Depends(get_current_user_with_permissions([Permission.GROQ_ASSISTANT]))):
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

        return JSONResponse(content={"groq_response": groq_response}, status_code=200)
