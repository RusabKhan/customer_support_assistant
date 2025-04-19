import requests
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError


def handle_db_error(exc_type, exc_val):
    """
    Handles database errors and maps them to HTTP exceptions with custom messages.

    Args:
    - exc_type: The type of exception raised.
    - exc_val: The actual exception instance.

    Returns:
    - Raises a FastAPI HTTPException with status code and detailed error message.
    """
    if isinstance(exc_val, IntegrityError):
        detail = "Database constraint error."
        if "unique" in str(exc_val.orig):
            detail = f"Duplicate entry detected: {exc_val.orig}"

        raise HTTPException(status_code=409, detail=detail)

    elif isinstance(exc_val, NoResultFound):
        raise HTTPException(status_code=404, detail="Resource not found.")

    elif isinstance(exc_val, SQLAlchemyError):
        raise HTTPException(status_code=500, detail="Internal server error with the database.")

    else:
        raise HTTPException(status_code=500, detail="Unknown database error.")


def handle_request_error(exc_type, exc_val):
    """
    Handles request errors and maps them to HTTP exceptions with custom messages.

    Args:
    - exc_type: The type of exception raised.
    - exc_val: The actual exception instance.

    Raises:
    - FastAPI HTTPException with appropriate status code and detail.
    """
    if isinstance(exc_val, HTTPException):
        raise exc_val

    if isinstance(exc_val, requests.exceptions.HTTPError):
        response = exc_val.response
        code = response.status_code if response else 500

        if code == 400:
            raise HTTPException(status_code=400, detail="Bad request: Check your parameters.")
        elif code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing API key.")
        elif code == 403:
            raise HTTPException(status_code=403, detail="Forbidden: You don’t have access to this resource.")
        elif code == 404:
            raise HTTPException(status_code=404, detail="Not found: Resource does not exist.")
        elif code == 409:
            raise HTTPException(status_code=409, detail="Conflict: Duplicate or conflicting resource.")
        elif code == 429:
            raise HTTPException(status_code=429, detail="Too Many Requests: Rate limit exceeded.")
        elif code == 500:
            raise HTTPException(status_code=500, detail="Internal server error: Remote server issue.")
        elif code == 502:
            raise HTTPException(status_code=502, detail="Bad Gateway: Groq's server is down or unreachable.")
        elif code == 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Remote service is temporarily offline.")
        else:
            raise HTTPException(status_code=code, detail=f"Unexpected error from remote API: {response.text if response else 'No response'}")

    elif isinstance(exc_val, requests.exceptions.ConnectionError):
        raise HTTPException(status_code=503, detail="Connection error: Unable to reach the API.")
    elif isinstance(exc_val, requests.exceptions.Timeout):
        raise HTTPException(status_code=504, detail="Timeout error: API took too long to respond.")
    elif isinstance(exc_val, requests.exceptions.RequestException):
        raise HTTPException(status_code=500, detail="Unexpected request error occurred.")
    else:
        raise HTTPException(status_code=500, detail=f"Unhandled exception: {str(exc_val)}")