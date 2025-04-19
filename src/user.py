from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta

from utils.database import get_db
from utils.db_models.main import User
from models.schemas import SignupRequest, TokenResponse

from models.schemas import Role
from utils.security import create_access_token, pwd_context
from utils.request_utils import get_current_user

router = APIRouter()


@router.post("/auth/signup", response_model=TokenResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db),
           current_user: User = Depends(lambda: get_current_user(required_permissions=[Role.admin]))):
    if current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Only admin can create users")
    hashed_password = pwd_context.hash(request.password)
    user = db.create_user(db, email=request.username, hashed_password=hashed_password, role=request.role.value)
    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/auth/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.get_user_by_email(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(data={"sub": str(user.id)})
    user.last_login = datetime.utcnow()
    db.commit()
    return TokenResponse(access_token=token, token_type="bearer")


@router.delete("/auth/user/{user_id}")
def delete_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete_user(db, user_id)
    return {"detail": "User deleted successfully"}


