from decimal import Decimal

from pydantic import BaseModel, validator


class TokenResponse(BaseModel):
    id: str
    name: str
    symbol: str
    decimals: int

    def __hash__(self):
        return hash(self.id)

    @validator('id')
    def validate_id(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Token id must start with 0x')
        return v.lower()

    class Config:
        orm_mode = True


class PairResponse(BaseModel):
    id: str
    token0: TokenResponse
    token1: TokenResponse
    token0Price: Decimal
    token1Price: Decimal

    class Config:
        orm_mode = True


class PairListResponse(BaseModel):
    pairs: list[PairResponse]


class TokenListResponse(BaseModel):
    tokens: list[TokenResponse]


class GraphQLPairsResponse(BaseModel):
    data: PairListResponse


class GraphQLTokensResponse(BaseModel):
    data: TokenListResponse


class ContractData(BaseModel):
    id: str
    token0: str
    token1: str
    reserve0: int
    reserve1: int
