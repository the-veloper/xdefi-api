import strawberry

from app.graphql.schemas.token import Token


@strawberry.input(description="Input for the best route query")
class RouteInput:
    fromToken: str
    toToken: str


def _get_data(root) -> int:
    return hash(root)


@strawberry.type
class Route:
    path: tuple[Token]
    data: int = strawberry.field(resolver=_get_data)

    def __hash__(self):
        return hash(self.path)
