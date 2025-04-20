import os
from groq import Groq
from utils.exception_handler import handle_request_error


class GroqAssistant:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def generate_response(self, ticket_description: str, message_history: list[str], latest_message: str) -> str:
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
