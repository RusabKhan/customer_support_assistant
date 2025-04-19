from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from uuid import UUID
from typing import List
from datetime import datetime

from utils.db_models.main import User, Ticket, Message, Token, Base
from utils.exception_handler import handle_db_error


class DB:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(self.db_url, pool_size=10, max_overflow=20)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def create_user(self, db: Session, email: str, hashed_password: str, role: str = "user") -> User:
        new_user = User(email=email, hashed_password=hashed_password, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def get_user(self, db: Session, user_id: UUID) -> User:
        return db.query(User).filter(User.id == user_id).first()

    def update_user(self, db: Session, user_id: UUID, email: str = None, hashed_password: str = None, role: str = None) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if email:
                user.email = email
            if hashed_password:
                user.hashed_password = hashed_password
            if role:
                user.role = role
            db.commit()
            db.refresh(user)
        return user

    def delete_user(self, db: Session, user_id: UUID):
        user = db.query(User).filter(User.id == user_id).first()
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

    def create_message(self, db: Session, ticket_id: UUID, content: str, is_ai: bool = False) -> Message:
        new_message = Message(ticket_id=ticket_id, content=content, is_ai=is_ai)
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return new_message

    def get_messages_by_ticket(self, db: Session, ticket_id: UUID) -> List[Message]:
        return db.query(Message).filter(Message.ticket_id == ticket_id).all()

    def create_token(self, db: Session, user_id: UUID, token: str, expires_at: datetime) -> Token:
        new_token = Token(user_id=user_id, token=token, expires_at=expires_at)
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
        """Enter the context manager, creating a session."""
        self.db_session = self.get_session()
        return self.db_session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager, handling flush and session closing."""
        if exc_type:
            self.db_session.rollback()
            return handle_db_error(exc_type, exc_val)
        else:
            self.db_session.commit()  # Commit the changes if no error
        self.db_session.close()

def create_db_url(db_name: str, db_user: str, db_password: str, db_host: str, db_port: int) -> str:
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"