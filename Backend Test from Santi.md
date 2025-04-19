# Customer Support Assistant Backend Assessment

## Overview

Thank you for participating in our backend engineering assessment! This take-home exercise is designed to evaluate your skills with FastAPI, asynchronous programming, OOP principles, and integrating with external services - all skills relevant to our day-to-day work.

**Time Expectation**: 3-4 hours

**Scenario**: You're building a backend for a customer support assistant that can handle customer inquiries and use AI to generate helpful responses. This simplified version focuses on core functionality while demonstrating your engineering skills.

## Project Specifications

### Core Requirements

1. **FastAPI Application**
   - Create a FastAPI application with the following endpoints:
     - User authentication (signup/login)
     - Support ticket creation and retrieval
     - Real-time AI response streaming using SSE

2. **Object-Oriented Design**
   - Implement a service-oriented architecture using OOP principles
   - Create appropriate class hierarchies for your services
   - Use dependency injection for better testability
   - Apply at least one design pattern and document your choice

3. **Database Integration**
   - Use SQLAlchemy or TypeORM with PostgreSQL
   - Create models for users and support tickets
   - Implement proper relationships between models
   - Include database migrations

4. **Authentication & Authorization**
   - Implement JWT-based authentication
   - Add basic role-based permissions (admin/user)

5. **AI Integration**
   - Integrate with Groq API (https://console.groq.com/docs/quickstart)
   - Implement streaming responses for real-time feedback
   - Create a simple prompt template system

6. **Containerization**
   - Provide a Dockerfile and docker-compose.yml
   - Include PostgreSQL in your compose setup
   - Document environment variables needed

## Important Notes

- **Focus on architecture over features**: We're evaluating your code organization and OOP principles more than feature completeness
- **Simple is better than complex**: Keep your solution focused on the requirements
- **This is NOT free work**: This is a simplified assessment version that wouldn't be used in production

## Getting Started

1. Initialize your project with Poetry:
   ```bash
   poetry init
   poetry add fastapi uvicorn sqlalchemy pydantic python-jose passlib python-multipart aiohttp
   poetry add --dev pytest pytest-asyncio black isort mypy
   ```

2. Create a `.env.example` file with required environment variables (don't include actual secrets)

3. Implement the core components following OOP best practices

## Example Data Models

```python
# These are just examples to guide you:

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    
    tickets = relationship("Ticket", back_populates="user")

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String)
    description = Column(String)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(UUID, ForeignKey("users.id"))
    user = relationship("User", back_populates="tickets")
    messages = relationship("Message", back_populates="ticket")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    content = Column(String)
    is_ai = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ticket_id = Column(UUID, ForeignKey("tickets.id"))
    ticket = relationship("Ticket", back_populates="messages")
```

## API Endpoints

Implement at least these endpoints:

- `POST /auth/signup` - Create a new user
- `POST /auth/login` - Login and receive JWT
- `GET /tickets` - List user's tickets
- `POST /tickets` - Create a new support ticket
- `GET /tickets/{ticket_id}` - Get a specific ticket with messages
- `POST /tickets/{ticket_id}/messages` - Add a message to a ticket
- `GET /tickets/{ticket_id}/ai-response` - Stream an AI response (SSE endpoint)

## Groq AI Integration

Use Groq's API to generate responses to customer inquiries. Their free tier is sufficient for this assessment.

Example prompt template:
```
You are a helpful customer support assistant. 
The customer has the following issue: {ticket_description}

Previous messages:
{message_history}

Customer's latest message: {latest_message}

Provide a helpful response that addresses their concern:
```

## Submission Requirements

1. A GitHub repository with your code
2. A comprehensive README.md including:
   - Setup instructions
   - Architectural decisions and OOP principles applied
   - Design patterns used and why
   - Any challenges faced and how you solved them
   - What you would improve with more time
3. Make sure your code has appropriate comments and documentation

## Evaluation Criteria

1. **Code Quality & OOP**
   - Clean, readable code following Python best practices
   - Proper use of classes, inheritance, and encapsulation
   - Appropriate separation of concerns

2. **Architecture**
   - Well-structured project organization
   - Proper service/repository pattern implementation
   - Thoughtful API design

3. **Technical Requirements**
   - Functioning authentication
   - Working database integration
   - Successful AI integration with streaming
   - Docker setup that works as expected

4. **Documentation**
   - Clear setup instructions
   - Well-documented code and API endpoints
   - Explanation of design decisions

Good luck with your assessment! Remember that we're more interested in seeing your engineering approach than perfect feature completion. Feel free to make reasonable assumptions where specifications aren't clear.