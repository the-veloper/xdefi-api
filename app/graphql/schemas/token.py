from decimal import Decimal

import strawberry


@strawberry.type
class Token:
    id: str
    name: str
    symbol: str
    price: Decimal

    def __hash__(self):
        return hash(self.id)
