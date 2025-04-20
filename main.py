import os
from fastapi import FastAPI

from src.user import router as user_router
from src.tickets import router as ticket_router
from src.groq_assistant import router as groq_router

from utils.db_models.main import Base
from utils.database import create_db_url, DB

app = FastAPI()

app.include_router(router=user_router)
app.include_router(router=ticket_router)
app.include_router(router=groq_router)


@app.on_event("startup")
def on_startup():
    with DB(create_db_url()) as db:
        Base.metadata.create_all(bind=db.engine)

        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if admin_email and admin_password:
            existing_admin = db.get_user_by_email(db.db_session, admin_email)
            if not existing_admin:
                db.create_user(db.db_session, email=admin_email, password=admin_password, role="admin")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
