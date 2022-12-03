from decimal import Decimal

import strawberry

from app.schemes.token import Token


@strawberry.type
class Query:
    @strawberry.field
    def token(self) -> Token:
        return Token(id="111", name="test", symbol="test", price=Decimal(1.0))
