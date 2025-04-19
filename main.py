from fastapi import FastAPI
from src.user import  router as user_router
from utils.db_models.main import Base
from utils.database import create_db_url, DB
import os

app = FastAPI()
app.include_router(router=user_router)


if __name__ == "__main__":
    import uvicorn

    Base.metadata.create_all(bind=DB(create_db_url()).engine)
    uvicorn.run(app, host="0.0.0.0", port=8000)