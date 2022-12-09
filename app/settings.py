from functools import lru_cache
from typing import Any

from eth_typing import ChecksumAddress
from pydantic import BaseSettings, Field
from pydantic import PostgresDsn
from pydantic import validator
from pydantic import AnyHttpUrl
from web3 import Web3

from app.constants import DEFAULT_HTTPX_MAX_CONNECTIONS, \
    DEFAULT_HTTPX_MAX_KEEPALIVE_CONNECTIONS, DEFAULT_HTTPX_TIMEOUT, \
    DEFAULT_HTTPX_RETRIES


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


class HTTPXSettings(BaseSettings):
    limits_max_connections: int = DEFAULT_HTTPX_MAX_CONNECTIONS
    limits_max_keepalive_connections: int = DEFAULT_HTTPX_MAX_KEEPALIVE_CONNECTIONS  # noqa: E501
    timeout_connect: float = DEFAULT_HTTPX_TIMEOUT
    timeout_read: float = DEFAULT_HTTPX_TIMEOUT
    timeout_write: float = DEFAULT_HTTPX_TIMEOUT
    timeout_pool: float = DEFAULT_HTTPX_TIMEOUT
    transport_retries: int = DEFAULT_HTTPX_RETRIES

    class Config:
        case_sensitive: bool = False
        env_prefix: str = "HTTPX_"


class UniswapSettings(BaseSettings):
    graphql_url: AnyHttpUrl
    sync_interval: int = 5
    factory_address: ChecksumAddress

    @validator("factory_address", pre=True)
    def parse_factory_address(cls, value):
        return Web3.toChecksumAddress(value)

    class Config:
        case_sensitive: bool = False
        env_prefix: str = "UNISWAP_"


@lru_cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()


@lru_cache()
def get_web3_settings() -> Web3Settings:
    return Web3Settings()


@lru_cache()
def get_httpx() -> HTTPXSettings:
    return HTTPXSettings()


@lru_cache()
def get_uniswap_settings() -> UniswapSettings:
    return UniswapSettings()
