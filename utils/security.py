import os
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

# Configurable secret and algorithm
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
    """
Generates a JWT access token encoding the provided data with an expiration time.

Args:
    data (dict): The data to include in the token payload.
    expires_delta (timedelta, optional): Token validity duration. Defaults to 1 hour.

Returns:
    str: The encoded JWT access token.
"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
Verifies whether a plain password matches the given hashed password.

Args:
    plain_password (str): The plaintext password to verify.
    hashed_password (str): The hashed password to compare against.

Returns:
    bool: True if the password matches, False otherwise.
"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
Hashes a plaintext password using the configured password hashing context.

Args:
    password (str): The plaintext password to hash.

Returns:
    str: The hashed password.
"""
    return pwd_context.hash(password)


def decode_access_token(token: str) -> dict:
    """
Decodes a JWT access token and returns its payload as a dictionary.

Args:
    token (str): The JWT access token to decode.

Returns:
    dict: The decoded token payload if valid, otherwise an empty dictionary.
"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return {}
