from typing import List

import strawberry
from strawberry.types import Info

from app.graphql.schemas.token import Token


@strawberry.type
class Query:
    @strawberry.field
    def tokens(self, info: Info) -> List[Token]:
        app = info.context["app"]
        ETH_AMOUNT = app.state.web3.toWei('1', 'Ether')
        price = app.state.uniswap.functions.getEthToTokenInputPrice(ETH_AMOUNT).call()
        return [Token(id="gega", name="gega", symbol="gega", price=price)]
