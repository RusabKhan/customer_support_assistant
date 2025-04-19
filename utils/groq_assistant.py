import requests

from utils.exception_handler import handle_request_error


class GroqAssistant:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/v1/ask"  # Update with Groq's correct endpoint

    def generate_response(self, ticket_description: str, message_history: list, latest_message: str) -> str:
        # Construct the prompt template
        prompt = f"""
        You are a helpful customer support assistant. 
        The customer has the following issue: {ticket_description}

        Previous messages:
        {message_history}

        Customer's latest message: {latest_message}

        Provide a helpful response that addresses their concern:
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt,
            "max_tokens": 150  # Control the response length
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "No response generated.")
        except Exception as err:
            return handle_request_error(type(err), err)
