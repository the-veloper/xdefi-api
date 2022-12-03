from functools import lru_cache

from pydantic import BaseSettings
from pydantic import PostgresDsn
from pydantic import validator


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgresql+asyncpg", }


class DatabaseSettings(BaseSettings):
    uri: AsyncPostgresDsn

    @validator("uri")
    @classmethod
    def database_must_be_specified_in_the_uri(cls, uri):
        assert uri.path and len(uri.path) > 1, 'database must be provided'
        return uri

    class Config:
        case_sensitive: bool = False
        env_prefix: str = "DATABASE_"


@lru_cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()
