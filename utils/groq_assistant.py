import os
from pyexpat.errors import messages

from utils.exception_handler import handle_request_error
from groq import Groq

class GroqAssistant:
    """
Provides an assistant for generating customer support responses using the Groq API.

Initializes a Groq client with the provided API key and generates responses based on ticket descriptions, message history, and the latest customer message. Handles request errors using the internal exception handler.
"""
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def generate_response(self, ticket_description: str, message_history: list[str], latest_message: str) -> str:
        """
Generates a customer support response using the Groq API based on the ticket description, message history, and the latest customer message.

Args:
    ticket_description (str): Description of the customer's issue.
    message_history (list[str]): List of previous messages in the conversation.
    latest_message (str): Most recent message from the customer.

Returns:
    str: Generated support response.

Raises:
    HTTPException: If an error occurs during the API request.
"""
        messages = []

        messages.append({
            "role": "system",
            "content": "You are a helpful customer support assistant.",
        })

        messages.append({
            "role": "user",
            "content": f"The customer has the following issue: {ticket_description}"
        })

        for msg in message_history:
            messages.append({
                "role": "user",
                "content": msg
            })

        messages.append({
            "role": "user",
            "content": f"Customer's latest message: {latest_message}"
        })

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="llama3-70b-8192",
                stream=False
            )
            return chat_completion.choices[0].message.content
        except Exception as err:
            return handle_request_error(type(err), err)

    def generate_response_from_history(self, message_history: list[str]) -> str:
        # Pseudo-call to Groq
        # Build a prompt or conversation object depending on their API
        prompt = "\n".join(message_history)
        messages = []
        messages.append({
            "role": "user",
            "content": f"Customer's latest message: {prompt}"
        })

        response = self.client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192",
            stream=False
            )  # implement _call_groq() internally
        return response.choices[0].message.content
