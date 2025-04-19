from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID

from utils.database import DB, create_db_url
from utils.db_models.main import User
from models.schemas import SignupRequest, TokenResponse
from utils.request_utils import get_db, get_current_user_with_permissions, get_current_user
from models.user_roles import Role

router = APIRouter()

@router.post("/auth/signup", response_model=TokenResponse)
def signup(
    request: SignupRequest,
    current_user: User = Depends(get_current_user_with_permissions([Role.admin]))
):
    with DB(create_db_url()) as db:
        user = db.create_user(email=request.username, password=request.password, role=request.role)
        token = db.create_token_for_user(user.id)
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/auth/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with DB(create_db_url()) as db:
        user = db.get_user_by_email_and_password(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = db.create_token_for_user(user.id)
    return TokenResponse(access_token=token, token_type="bearer")


@router.delete("/auth/user/{user_id}")
def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user_with_permissions([Role.admin]))
):
    with DB(create_db_url()) as db:
        db.delete_user(user_id)
    return {"detail": "User deleted successfully"}
