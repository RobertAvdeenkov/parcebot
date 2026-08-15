from fastapi import FastAPI
import os
from sqlalchemy import create_engine
from models import Base
import tasks

app=FastAPI()
DATABASE_URL=os.getenv('DATABASE_URL', 'sqlite:///monitor.db')
engine=create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

app.include_router(tasks.router)