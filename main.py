from fastapi import FastAPI
import os
from sqlalchemy import create_engine
from models import Base
import tasks

app=FastAPI()
url='postgresql://neondb_owner:npg_LEVInm0Za6Jf@ep-muddy-meadow-axsen04k-pooler.c-4.us-east-2.aws.neon.tech/neondb'
engine=create_engine(url)
Base.metadata.create_all(engine)

app.include_router(tasks.router)