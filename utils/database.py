import os
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from utils.db_models.main import User, Ticket, Message, Token
from utils.exception_handler import handle_db_error
from utils.security import pwd_context, create_access_token


class DB:
    """
Database access layer for user, ticket, message, and token management.

Provides methods for creating, retrieving, updating, and deleting users, tickets, messages, and tokens,
as well as session management and error handling using SQLAlchemy and internal utilities.
Supports context management for safe transaction handling.
"""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(self.db_url, pool_size=10, max_overflow=20)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def create_user(self, db: Session, email: str, password: str, role: str = "user") -> User:
        """
Create a new user with the given email, password, and role.

Args:
    db (Session): SQLAlchemy database session.
    email (str): User's email address.
    password (str): Plaintext password to be hashed.
    role (str, optional): User role. Defaults to "user".

Returns:
    User: The created User object.
"""
        hashed_password = pwd_context.hash(password)
        new_user = User(email=email, hashed_password=hashed_password, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def get_user_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        """
Retrieve a user by their unique ID.

Args:
    db (Session): SQLAlchemy database session.
    user_id (UUID): Unique identifier of the user.

Returns:
    Optional[User]: The User object if found, otherwise None.
"""
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
Retrieve a user by their email address.

Args:
    db (Session): SQLAlchemy database session.
    email (str): User's email address.

Returns:
    Optional[User]: The User object if found, otherwise None.
"""
        return db.query(User).filter(User.email == email).first()

    def get_user_by_email_and_password(self, db: Session, email: str, password: str) -> Optional[User]:
        """
Authenticate a user by email and password.

Args:
    db (Session): SQLAlchemy session.
    email (str): User's email address.
    password (str): Plaintext password.

Returns:
    Optional[User]: The authenticated User object if credentials are valid, otherwise None.
    Updates the user's last_login timestamp on successful authentication.
"""
        user = self.get_user_by_email(db, email)
        if user and pwd_context.verify(password, user.hashed_password):
            user.last_login = datetime.utcnow()
            db.commit()
            db.refresh(user)
            return user
        return None

    def delete_user(self, db: Session, user_id: UUID):
        """
Delete a user from the database by user ID.

Args:
    db (Session): SQLAlchemy session.
    user_id (UUID): Unique identifier of the user to delete.
"""
        user = self.get_user_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()

    def create_ticket(self, db: Session, user_id: UUID, title: str, description: str, status: str = "open") -> Ticket:
        """
Create a new ticket for a user with the specified title, description, and status.

Args:
    db (Session): SQLAlchemy database session.
    user_id (UUID): Unique identifier of the user creating the ticket.
    title (str): Title of the ticket.
    description (str): Description of the ticket.
    status (str, optional): Status of the ticket. Defaults to "open".

Returns:
    Ticket: The created Ticket object.
"""
        new_ticket = Ticket(user_id=user_id, title=title, description=description, status=status)
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        return new_ticket

    def get_tickets_by_user(self, db: Session, user_id: UUID, page: int = 1, page_size: int = 10) -> List[Ticket]:
        """
Retrieve a paginated list of tickets for a specific user.

Args:
    db (Session): SQLAlchemy database session.
    user_id (UUID): Unique identifier of the user.
    page (int, optional): Page number for pagination. Defaults to 1.
    page_size (int, optional): Number of tickets per page. Defaults to 10.

Returns:
    List[Ticket]: A list of Ticket objects associated with the user.
"""
        offset = (page - 1) * page_size
        return db.query(Ticket).filter(Ticket.user_id == user_id).offset(offset).limit(page_size).all()

    def get_all_tickets(self, db: Session, page: int = 1, page_size: int = 10) -> List[Ticket]:
        """
Retrieve a paginated list of all tickets.

Args:
    db (Session): SQLAlchemy database session.
    page (int, optional): Page number for pagination. Defaults to 1.
    page_size (int, optional): Number of tickets per page. Defaults to 10.

Returns:
    List[Ticket]: A list of Ticket objects for the specified page.
"""
        offset = (page - 1) * page_size
        return db.query(Ticket).offset(offset).limit(page_size).all()

    def create_message(self, db: Session, ticket_id: UUID, content: str, is_ai: bool = False) -> Message:
        """
Create a new message for a specified ticket.

Args:
    db (Session): SQLAlchemy database session.
    ticket_id (UUID): Unique identifier of the ticket.
    content (str): Content of the message.
    is_ai (bool, optional): Indicates if the message is generated by AI. Defaults to False.

Returns:
    Message: The created Message object.
"""
        new_message = Message(ticket_id=ticket_id, content=content, is_ai=is_ai)
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return new_message

    def get_messages_by_ticket(self, db: Session, ticket_id: UUID, page: int = 1, page_size: int = 10) -> List[Message]:
        """
Retrieve a paginated list of messages for a specific ticket.

Args:
    db (Session): SQLAlchemy database session.
    ticket_id (UUID): Unique identifier of the ticket.
    page (int, optional): Page number for pagination. Defaults to 1.
    page_size (int, optional): Number of messages per page. Defaults to 10.

Returns:
    List[Message]: A list of Message objects associated with the ticket.
"""
        offset = (page - 1) * page_size
        return db.query(Message).filter(Message.ticket_id == ticket_id).offset(offset).limit(page_size).all()

    def create_token_for_user(self, db: Session, user_id: UUID, expires_delta: timedelta = timedelta(hours=1)) -> Token:
        """
Create and store a new access token for a user.

Args:
    db (Session): SQLAlchemy database session.
    user_id (UUID): Unique identifier of the user.
    expires_delta (timedelta, optional): Token validity duration. Defaults to 1 hour.

Returns:
    Token: The created Token object associated with the user.
"""
        access_token = create_access_token(data={"sub": str(user_id)}, expires_delta=expires_delta)
        expires_at = datetime.utcnow() + expires_delta
        new_token = Token(user_id=user_id, token=access_token, expires_at=expires_at)
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        return new_token

    def get_tokens_by_user(self, db: Session, user_id: UUID, page: int = 1, page_size: int = 10) -> List[Token]:

        """
Retrieve a list of tokens associated with a user, paginated by page and page_size.

Args:
    db (Session): SQLAlchemy database session.
    user_id (UUID): Unique identifier of the user.
    page (int, optional): Page number of the results. Defaults to 1.
    page_size (int, optional): Number of results per page. Defaults to 10.

Returns:
    List[Token]: A list of Token objects associated with the user.
"""
        offset = (page - 1) * page_size
        return db.query(Token).filter(Token.user_id == user_id).offset(offset).limit(page_size).all()

    def revoke_token(self, db: Session, token_id: UUID):
        """
Revoke a token by setting its revoked_at timestamp to the current UTC time.

Args:
    db (Session): SQLAlchemy database session.
    token_id (UUID): Unique identifier of the token to revoke.
"""
        token = db.query(Token).filter(Token.id == token_id).first()
        if token:
            token.revoked_at = datetime.utcnow()
            db.commit()
            db.refresh(token)

    def get_ticket_with_messages(self, db: Session, ticket_id: UUID, page: int = 1, page_size: int = 10) -> Optional[
        Ticket]:
        """
Retrieve a ticket by its ID and attach a paginated list of its messages.

Args:
    db (Session): SQLAlchemy database session.
    ticket_id (UUID): Unique identifier of the ticket.
    page (int, optional): Page number for message pagination. Defaults to 1.
    page_size (int, optional): Number of messages per page. Defaults to 10.

Returns:
    Optional[Ticket]: The Ticket object with its messages if found, otherwise None.
"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.messages = self.get_messages_by_ticket(db, ticket_id, page, page_size)
        return ticket

    def get_ticket(self, db: Session, ticket_id: UUID) -> Optional[Ticket]:
        """
Retrieve a ticket by its unique ID.

Args:
    db (Session): SQLAlchemy database session.
    ticket_id (UUID): Unique identifier of the ticket.

Returns:
    Optional[Ticket]: The Ticket object if found, otherwise None.
"""
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def get_groq_chats_by_ticket_id(
            self,
            db: Session,
            ticket_id: UUID,
            page: int = 1,
            page_size: int = 10
    ) -> List[Message]:
        offset = (page - 1) * page_size
        return (
            db.query(Message)
            .filter(Message.ticket_id == ticket_id)
            .filter(Message.is_ai == True)
            .offset(offset)
            .limit(page_size)
            .all()
        )



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
    """
Constructs and returns a database URL string using environment variables for dialect, user, password, host, port, and database name.
"""
    return f"{os.getenv('DB_DIALECT')}://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"


def get_db() -> Session:
    """Dependency to get the database session."""
    db_session = DB(db_url=create_db_url()).get_session()
    try:
        yield db_session
    finally:
        db_session.close()
