import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, NoResultFound
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta

from utils.db_models.main import User, Ticket, Message, Token, Base
from utils.exception_handler import handle_db_error
from utils.security import pwd_context, create_access_token


class DB:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(self.db_url, pool_size=10, max_overflow=20)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def create_user(self, db: Session, email: str, password: str, role: str = "user") -> User:
        hashed_password = pwd_context.hash(password)
        new_user = User(email=email, hashed_password=hashed_password, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def get_user_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_user_by_email_and_password(self, db: Session, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(db, email)
        if user and pwd_context.verify(password, user.hashed_password):
            user.last_login = datetime.utcnow()
            db.commit()
            db.refresh(user)
            return user
        return None

    def delete_user(self, db: Session, user_id: UUID):
        user = self.get_user_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()

    def create_ticket(self, db: Session, user_id: UUID, title: str, description: str, status: str = "open") -> Ticket:
        new_ticket = Ticket(user_id=user_id, title=title, description=description, status=status)
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        return new_ticket

    def get_tickets_by_user(self, db: Session, user_id: UUID) -> List[Ticket]:
        return db.query(Ticket).filter(Ticket.user_id == user_id).all()

    def get_all_tickets(self, db: Session) -> List[Ticket]:
        return db.query(Ticket).all()

    def create_message(self, db: Session, ticket_id: UUID, content: str, is_ai: bool = False) -> Message:
        new_message = Message(ticket_id=ticket_id, content=content, is_ai=is_ai)
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return new_message

    def get_messages_by_ticket(self, db: Session, ticket_id: UUID) -> List[Message]:
        return db.query(Message).filter(Message.ticket_id == ticket_id).all()

    def create_token_for_user(self, db: Session, user_id: UUID, expires_delta: timedelta = timedelta(hours=1)) -> Token:
        access_token = create_access_token(data={"sub": str(user_id)}, expires_delta=expires_delta)
        expires_at = datetime.utcnow() + expires_delta
        new_token = Token(user_id=user_id, token=access_token, expires_at=expires_at)
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        return new_token

    def get_tokens_by_user(self, db: Session, user_id: UUID) -> List[Token]:
        return db.query(Token).filter(Token.user_id == user_id).all()

    def revoke_token(self, db: Session, token_id: UUID):
        token = db.query(Token).filter(Token.id == token_id).first()
        if token:
            token.revoked_at = datetime.utcnow()
            db.commit()
            db.refresh(token)

    def __enter__(self):
        self.db_session = self.get_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db_session.rollback()
            return handle_db_error(exc_type, exc_val)
        else:
            self.db_session.commit()
        self.db_session.close()


def create_db_url() -> str:
    return f"{os.getenv('DB_DIALECT')}://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

def get_db() -> Session:
    """Dependency to get the database session."""
    db_session = DB(db_url=create_db_url()).get_session()
    try:
        yield db_session
    finally:
        db_session.close()