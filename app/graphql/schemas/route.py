import strawberry

from app.graphql.schemas.token import Token


@strawberry.input(description="Input for the best route query")
class RouteInput:
    fromToken: str
    toToken: str


@strawberry.type
class Route:
    id: str
    path: list[Token]
