from decimal import Decimal

from pydantic import BaseModel


class TokenResponse(BaseModel):
    id: str
    name: str
    symbol: str


class PairResponse(BaseModel):
    id: str
    token0: TokenResponse
    token1: TokenResponse
    token0Price: Decimal
    token1Price: Decimal


class PairListResponse(BaseModel):
    pairs: list[PairResponse]


class GraphQLPairsResponse(BaseModel):
    data: PairListResponse
