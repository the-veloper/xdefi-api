from asyncio import gather

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app import settings
from app.core.httpx import create_httpx_client
from app.db.session import create_async_database
from app.graphql.query import Query
from app.proxies.uniswap import UniswapProxy
from app.routers import healthchecks_router
from app.schemas.uniswap_api import PairListResponse
from app.uniswap_pair_sync import UniswapSyncer
from app.web3.session import get_web3_provider, uniswap_factory

NAME = "xdefi-api"
ROOT_PATH = f"/{NAME}"


def create_app() -> FastAPI:
    database_settings: settings.DatabaseSettings = settings.get_database_settings()  # noqa: E501
    web3_settings: settings.Web3Settings = settings.get_web3_settings()  # noqa: E501
    httpx_settings: settings.HTTPXSettings = settings.get_httpx()

    uniswap_client_pool = create_httpx_client(settings=httpx_settings)  # noqa: E501

    app = FastAPI(
        title=NAME,
        docs_url=None,
        openapi_url=None,
        redoc_url=None,
        root_path=ROOT_PATH,
    )

    # App State
    app.state.app_name = NAME

    app.state.web3 = get_web3_provider(web3_settings.node_url)
    app.state.engine, app.state.sessionmaker = create_async_database(uri=database_settings.uri)  # noqa: E501

    app.state.uniswap = uniswap_factory(app.state.web3)
    app.state.uniswap_settings = settings.get_uniswap_settings()
    app.state.uniswap_proxy = UniswapProxy(
        httpx_client=uniswap_client_pool,
        uniswap_settings=app.state.uniswap_settings
    )
    app.state.uniswap_pairs = {}
    app.state.uniswap_syncer = UniswapSyncer(app=app)
    app.state.uniswap_syncer.start()

    # Shutdown handler
    @app.on_event("shutdown")
    async def shutdown_event():
        await gather(
            app.state.engine.dispose(),
            uniswap_client_pool.aclose(),
        )
        app.state.uniswap_syncer.stop()
        app.state.uniswap_syncer.join()

    # GraphQL
    schema = strawberry.Schema(query=Query)
    graphql_app = GraphQLRouter(
        schema,
        context_getter=lambda: dict(app=app,),
    )

    # Routers
    app.include_router(graphql_app, prefix="/graphql")

    app.include_router(
        healthchecks_router.router,
        prefix="/healthchecks",
        tags=["Healthchecks"],
    )

    return app
