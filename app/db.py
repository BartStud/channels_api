import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@channels_db/channels_db"
)

engine = create_async_engine(DATABASE_URL, echo=True)


async def get_db():
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore
    async with SessionLocal() as session:  # type: ignore
        yield session
