from decimal import Decimal

from pydantic import BaseModel


class TokenResponse(BaseModel):
    id: str
    name: str
    symbol: str

    def __hash__(self):
        return hash(self.id)


class PairResponse(BaseModel):
    id: str
    token0: TokenResponse
    token1: TokenResponse
    token0Price: Decimal
    token1Price: Decimal


class PairListResponse(BaseModel):
    pairs: list[PairResponse]


class TokenListResponse(BaseModel):
    tokens: list[TokenResponse]


class GraphQLPairsResponse(BaseModel):
    data: PairListResponse


class GraphQLTokensResponse(BaseModel):
    data: TokenListResponse
