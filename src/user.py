from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from uuid import UUID

from utils.database import DB, create_db_url
from utils.db_models.main import User
from src.models.schemas import SignupRequest, TokenResponse, SignupResponse
from utils.request_utils import get_current_user_with_permissions
from src.models.enums import Role

router = APIRouter()

@router.post("/auth/signup", response_model=SignupResponse)
async def signup(
    request: SignupRequest,
    current_user: User = Depends(get_current_user_with_permissions([Role.admin]))
):
    """
Registers a new user account.
Accessible only to admin users.

Args:
    request (SignupRequest): User signup details.
    current_user (User): The authenticated admin user (injected by dependency).

Returns:
    SignupResponse: Details of the newly created user.
"""
    with DB(create_db_url()) as db:
        user = db.create_user(db.db_session,email=request.email, password=request.password, role=request.role)
        return SignupResponse(
            email=user.email,
            role=user.role,
            created_at=user.created_at)


@router.post("/auth/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
Authenticate a user and issue a bearer token.

Validates user credentials from the login form, and returns an access token with expiration details if authentication succeeds.

Args:
    form_data (OAuth2PasswordRequestForm): Login form data containing username and password.

Returns:
    TokenResponse: Access token and related metadata.

Raises:
    HTTPException: If authentication fails due to incorrect credentials.
"""
    with DB(create_db_url()) as db:
        user = db.get_user_by_email_and_password(db.db_session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = db.create_token_for_user(db.db_session, user.id)

        return TokenResponse(
            id=token.id,
            user_id=token.user_id,
            token=token.token,
            expires_at=token.expires_at,
            created_at=token.created_at,
            revoked_at=token.revoked_at,
            token_type="bearer"
        )


@router.delete("/auth/user/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user_with_permissions([Role.admin]))
):
    """
Delete a user by user ID. Requires admin permissions.

Args:
    user_id (UUID): Unique identifier of the user to delete.
    current_user (User): The currently authenticated admin user.

Returns:
    dict: Confirmation message upon successful deletion.
"""
    with DB(create_db_url()) as db:
        db.delete_user(db.db_session, user_id)
    return {"detail": "User deleted successfully"}


@router.get("/auth/user/{user_id}")
async def get_user(user_id: UUID, current_user: User = Depends(get_current_user_with_permissions([Role.admin]))):
    """
Retrieve a user by their unique ID.

Requires admin permissions.

Args:
    user_id (UUID): Unique identifier of the user.
    current_user (User): The currently authenticated admin user (injected by dependency).

Returns:
    User: The user object corresponding to the given ID.
"""
    with DB(create_db_url()) as db:
        user = db.get_user_by_id(db.db_session, user_id)
    return user


@router.get("/auth/users")
async def get_users(current_user: User = Depends(get_current_user_with_permissions([Role.admin]))):
    """
Retrieve a list of all users. Accessible only to users with the admin role.

Args:
    current_user (User): The currently authenticated admin user (injected by dependency).

Returns:
    List[User]: A list of all user objects.
"""
    with DB(create_db_url()) as db:
        users = db.get_all_users(db.db_session)
    return users

