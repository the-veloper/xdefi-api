from asyncio import gather

import strawberry
import networkx as nx
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app import settings
from app.db.session import create_async_database
from app.graphql.query import Query
from app.routers import healthchecks_router
from app.uniswap_pair_sync import UniswapSyncer
from app.web3.session import get_web3_provider, uniswap_factory

NAME = "xdefi-api"
ROOT_PATH = f"/{NAME}"


def create_app() -> FastAPI:
    database_settings: settings.DatabaseSettings = settings.get_database_settings()  # noqa: E501
    web3_settings: settings.Web3Settings = settings.get_web3_settings()  # noqa: E501
    uniswap_settings: settings.UniswapSettings = settings.get_uniswap_settings()  # noqa: E501

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

    app.state.uniswap = uniswap_factory(app.state.web3, uniswap_settings.factory_address)  # noqa: E501
    app.state.uniswap_settings = settings.get_uniswap_settings()

    app.state.token_graph = nx.Graph()

    # Shutdown handler
    @app.on_event("shutdown")
    async def shutdown_event():
        await gather(
            app.state.engine.dispose(),
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

    app.state.uniswap_syncer = UniswapSyncer(app=app)
    app.state.uniswap_syncer.start()

    return app


application = create_app()
