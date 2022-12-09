from dataclasses import dataclass
from typing import ClassVar

import httpx
from pydantic import ValidationError

from app import exceptions
from app.proxies.base import BaseHTTPXProxy
from app.schemas.uniswap_api import PairListResponse, GraphQLPairsResponse
from app.settings import UniswapSettings


@dataclass
class UniswapProxy(BaseHTTPXProxy):
    uniswap_settings: UniswapSettings

    GRAPHQL_PATH: ClassVar[str] = "/graphql"

    async def post(self, json: dict):
        return await self.httpx_client.post(
            url=self.uniswap_settings.graphql_url,
            json=json,
            headers={"Content-Type": "application/json"},
        )

    async def get_pairs(self) -> PairListResponse:
        query = """
        {
          pairs {
            id
            token0 {
                id
                symbol
                name
            }
            token1 {
                id
                symbol
                name
            }
            token0Price
            token1Price
          }
        }
        """
        try:
            response = await self.post(
                    json={"query": query}
            )

            response_parsed = GraphQLPairsResponse.parse_raw(response.text)

            if response.status_code != 200:
                raise exceptions.UniswapAPIError("Query failed")

            return response_parsed.data
        except (httpx.TimeoutException, httpx.ConnectError):
            raise exceptions.UniswapAPIConnectionError()

        except ValidationError:
            raise exceptions.UnexpectedAPIResponseError(
                "Uniswap API response is not valid"
            )
