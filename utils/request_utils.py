from typing import List

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from models.enums import Role, RolePermissions, Permission
from utils import get_db
from utils.db_models.main import User
from utils.security import SECRET_KEY, ALGORITHM


def has_permission(role: Role, action: str):
    """
Checks if the given role has permission to perform the specified action.

Raises:
    HTTPException: If the role does not have the required permission.
"""
    allowed = RolePermissions.get(role, set())
    if action not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{role}' does not have permission to perform '{action}'"
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
        required_permissions: List[Role] = None
) -> User:
    """
Retrieves the current authenticated user from the JWT token, verifies their existence in the database,
and checks if their role matches any required permissions. Raises HTTPException for invalid tokens,
missing users, or insufficient permissions.

Args:
    db (Session): Database session dependency.
    token (str): JWT token from the request.
    required_permissions (List[Role], optional): List of roles allowed to access the endpoint.

Returns:
    User: The authenticated user object.

Raises:
    HTTPException: If authentication or authorization fails.
"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # "sub" is the subject of the JWT token (usually user ID)

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        user = db.query(User).filter(User.id == user_id).first()  # Fetch user from the DB
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        if required_permissions:
            if user.role not in required_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have permission to access this resource"
                )

        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user_with_permissions(required_permissions: list[Permission]):
    """
Returns a dependency that retrieves the current user and checks if they have at least one of the specified permissions.

Args:
    required_permissions (list[Permission]): List of permissions required to access the endpoint.

Returns:
    Callable: A dependency function for FastAPI routes that enforces permission checks.

Raises:
    HTTPException: If the user does not have any of the required permissions.
"""

    def dependency(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
        user = get_current_user(db, token)
        user_permissions = RolePermissions.get(user.role, set())

        if not set(required_permissions).intersection(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource."
            )

        return user

    return dependency
