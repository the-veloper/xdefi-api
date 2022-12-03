from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession  # noqa: E501
from sqlalchemy.orm import sessionmaker


def create_async_database(uri: str) -> Tuple[AsyncEngine, sessionmaker]:
    engine: AsyncEngine = create_async_engine(uri)
    session_maker: sessionmaker = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
    )
    return engine, session_maker
