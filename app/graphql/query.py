from typing import List

import networkx as nx
import strawberry
from strawberry.types import Info

from app.graphql.schemas.route import RouteInput, Route
from app.graphql.schemas.token import Token


def _weight(l_node, r_node, attributes):
    return 1


@strawberry.type
class Query:
    @strawberry.field
    def tokens(self, info: Info) -> List[Token]:
        app = info.context["app"]
        ETH_AMOUNT = app.state.web3.toWei('1', 'Ether')
        price = app.state.uniswap.functions.getEthToTokenInputPrice(ETH_AMOUNT).call()
        return [Token(id="gega", name="gega", symbol="gega", price=price)]

    @strawberry.field
    def best_route(self, route_input: RouteInput, info: Info) -> Route:
        app = info.context["app"]

        shortest_path = nx.shortest_path(
            app.state.token_graph,
            route_input.fromToken,
            route_input.toToken,
            weight=_weight,
        )

        return Route(id="gega", path=shortest_path)
