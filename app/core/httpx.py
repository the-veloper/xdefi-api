from httpx import AsyncClient, AsyncHTTPTransport, Limits, Timeout

from app.settings import HTTPXSettings


def create_httpx_client(settings: HTTPXSettings) -> AsyncClient:
    transport = AsyncHTTPTransport(
        retries=settings.transport_retries,
    )
    limits: Limits = Limits(
        max_connections=settings.limits_max_connections,
        max_keepalive_connections=settings.limits_max_keepalive_connections,
    )
    timeout: Timeout = Timeout(
        connect=settings.timeout_connect,
        read=settings.timeout_read,
        write=settings.timeout_write,
        pool=settings.timeout_pool,
    )
    client: AsyncClient = AsyncClient(
        limits=limits,
        timeout=timeout,
        transport=transport,
        trust_env=False,
    )

    return client
