from dataclasses import dataclass

from httpx import AsyncClient


@dataclass
class BaseHTTPXProxy:
    httpx_client: AsyncClient
