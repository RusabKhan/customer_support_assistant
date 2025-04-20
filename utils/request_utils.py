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
    """Dependency to get the current logged-in user from the token and check their permissions."""
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # "sub" is the subject of the JWT token (usually user ID)

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        user = db.query(User).filter(User.id == user_id).first()  # Fetch user from the DB
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        # If required_permissions are passed, check if the user's role is allowed to access the endpoint
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
    def dependency(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
        user = get_current_user(db, token)
        user_permissions = RolePermissions.get(user.role, set())

        if not set(required_permissions).issubset(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource."
            )

        return user

    return dependency