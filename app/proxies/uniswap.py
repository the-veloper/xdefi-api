from dataclasses import dataclass

import httpx
from pydantic import ValidationError

from app import exceptions
from app.proxies.base import BaseHTTPXProxy
from app.schemas.uniswap_api import GraphQLPairsResponse
from app.schemas.uniswap_api import GraphQLTokensResponse
from app.schemas.uniswap_api import TokenResponse
from app.schemas.uniswap_api import PairResponse
from app.settings import UniswapSettings


@dataclass
class UniswapProxy(BaseHTTPXProxy):
    uniswap_settings: UniswapSettings

    async def _post(self, json: dict):
        return await self.httpx_client.post(
            url=self.uniswap_settings.graphql_url,
            json=json,
            headers={"Content-Type": "application/json"},
        )

    async def _graphql_request(self, query: str) -> str:
        try:
            response = await self._post(
                json={"query": query}
            )

            if response.status_code != 200:
                raise exceptions.UniswapAPIError("Query failed")

            return response.text

        except (httpx.TimeoutException, httpx.ConnectError):
            raise exceptions.UniswapAPIConnectionError()

    async def get_pairs(
        self,
        skip: int = 0,
        first: int = 500
    ) -> list[PairResponse]:
        query = f"""
        {{
          pairs(skip: {skip}, first: {first}) {{
            id
            token0 {{
                id
                symbol
                name
            }}
            token1 {{
                id
                symbol
                name
            }}
            token0Price
            token1Price
          }}
        }}
        """
        response = await self._graphql_request(
            query=query,
        )

        try:
            return GraphQLPairsResponse.parse_raw(response).data.pairs
        except ValidationError:
            raise exceptions.UnexpectedAPIResponseError(
                "Uniswap API response is not valid"
            )

    async def get_tokens(
        self,
        skip: int = 0,
        first: int = 500
    ) -> list[TokenResponse]:
        query = f"""
        {{
          tokens(skip: {skip}, first: {first}) {{
            id
            symbol
            name
          }}
        }}
        """
        response = await self._graphql_request(
            query=query,
        )

        try:
            return GraphQLTokensResponse.parse_raw(response).data.tokens
        except ValidationError:
            raise exceptions.UnexpectedAPIResponseError(
                "Uniswap API response is not valid"
            )
