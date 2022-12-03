import strawberry
from strawberry.asgi import GraphQL
from fastapi import FastAPI


from app import settings
from app.db.session import create_async_database
from app.graphql.query import Query

NAME = "xdefi-api"
ROOT_PATH = f"/{NAME}"


def create_app() -> FastAPI:
    database_settings: settings.DatabaseSettings = settings.get_database_settings()  # noqa: E501

    app = FastAPI(
        title=NAME,
        docs_url=None,
        openapi_url=None,
        redoc_url=None,
        root_path=ROOT_PATH,
    )

    schema = strawberry.Schema(query=Query)

    graphql_app = GraphQL(schema)

    app.state.engine, app.state.sessionmaker = create_async_database(uri=database_settings.uri)  # noqa: E501
    app.add_route("/graphql", graphql_app)
    app.add_websocket_route("/graphql", graphql_app)

    return app
