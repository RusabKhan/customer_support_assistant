# Customer Support Assistant

An AI-powered customer support system designed to streamline ticket management and enhance user interactions through intelligent automation.

## 🚀 Features

- **User Management**: Secure registration, authentication, and role-based access control.
- **Ticketing System**: Create, view, and manage support tickets efficiently.
- **Messaging**: Facilitate communication between users and support agents within tickets.
- **AI Integration**: Leverage Groq's LLaMA 3 model to generate context-aware responses.
- **Token Management**: Issue and revoke access tokens with expiration handling.
- **Pagination**: Efficient data retrieval with paginated endpoints for scalability.
- **Feedback Loop**: Reply to AI-generated messages with human responses and feed them back to the model.

## 🧰 Technologies Used

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL, SQLAlchemy
- **ORM**: SQLAlchemy with scoped sessions
- **AI Model**: Groq's LLaMA 3
- **Authentication**: JWT Tokens
- **Environment Management**: Poetry

## 📦 Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/RusabKhan/customer_support_assistant.git
   cd customer_support_assistant
   ```

2. **Install Poetry** (if not already installed):

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**:

   ```bash
   poetry install
   ```

4. **Activate the virtual environment**:

   ```bash
   poetry shell
   ```

5. **Configure environment variables**:

   Create a `.env` file in the root directory:

   ```env
   DB_DIALECT=postgresql
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_db_name
   GROQ_API_KEY=your_groq_api_key
   SECRET_KEY=your_secret_key
   ```

6. **Run the application**:

   ```bash
   uvicorn main:app --reload
   ```

> ✅ **Note**: Alembic migrations are triggered automatically when you start the FastAPI app, so you don’t need to run them manually.

## 🗃️ Database Management

Database sessions are managed using a custom `DB` utility class found in `src/utils/db.py`. This class uses the `with` statement to ensure proper session management:

- Commits transactions on success.
- Rolls back transactions on exception.
- Automatically flushes and disposes the session on exit.

This ensures **atomicity** and **clean handling** of transactions without leaking sessions or failing silently.

## 🧪 API Endpoints

- **User Endpoints**:
  - `POST /users/` – Register a new user.
  - `POST /login/` – Authenticate and receive a JWT token.

- **Ticket Endpoints**:
  - `POST /tickets/` – Create a new support ticket.
  - `GET /tickets/` – Retrieve a list of tickets with pagination.
  - `GET /tickets/{ticket_id}/` – Retrieve a specific ticket.

- **Message Endpoints**:
  - `POST /tickets/{ticket_id}/messages/` – Add a message to a ticket.
  - `GET /tickets/{ticket_id}/messages/` – Retrieve messages for a ticket.

- **AI Integration**:
  - `GET /tickets/{ticket_id}/ai-response/` – Generate an AI response for a ticket.
  - `POST /tickets/{ticket_id}/ai-feedback/` – Submit feedback or a follow-up to the AI-generated response.

## 🐳 Docker Support

To run the project in Docker:

```bash
docker-compose up --build
```

Then go to [http://localhost:8000](http://localhost:8000)

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## 🪪 License

This project is licensed under the MIT License.
