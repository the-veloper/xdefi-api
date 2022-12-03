from functools import lru_cache

from pydantic import BaseSettings
from pydantic import PostgresDsn
from pydantic import validator
from pydantic import AnyHttpUrl


class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgresql+asyncpg", }


class Web3Settings(BaseSettings):
    node_url: AnyHttpUrl

    class Config:
        case_sensitive: bool = False
        env_prefix: str = "WEB3_"


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


@lru_cache()
def get_web3_settings() -> Web3Settings:
    return Web3Settings()
