from dataclasses import dataclass

from httpx import AsyncClient
from web3 import Web3
from web3.contract import Contract


@dataclass
class BaseHTTPXProxy:
    httpx_client: AsyncClient


@dataclass
class BaseContractProxy:
    web3_provider: Web3
    contract: Contract
