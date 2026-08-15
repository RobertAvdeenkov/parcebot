from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
import os

url="postgresql+asyncpg://neondb_owner:npg_LEVInm0Za6Jf@ep-muddy-meadow-axsen04k-pooler.c-4.us-east-2.aws.neon.tech/neondb"
engine=create_async_engine(url,connect_args={'ssl':True, 'ssl_require':True})
SessionLocal=sessionmaker(bind=engine,class_=AsyncSession, expire_on_commit=False) #type:ignore

async def get_db():
    async with SessionLocal() as db: #type:ignore
        try:
            yield db
        finally:
            await db.close()