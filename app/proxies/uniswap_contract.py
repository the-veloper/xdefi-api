import json
from dataclasses import dataclass

from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract import Contract

from app.constants import POOL_ABI, UNISCAP_TOKEN_ABI
from app.proxies.base import BaseContractProxy
from app.schemas.uniswap_api import ContractData, TokenResponse, PairResponse
from app.settings import UniswapSettings


@dataclass
class UniswapFactoryProxy(BaseContractProxy):
    uniswap_settings: UniswapSettings

    def get_pair_length(self) -> int:
        return self.contract.functions.allPairsLength().call()

    def get_pair_address(self, index: int) -> ChecksumAddress:
        return Web3.toChecksumAddress(self.contract.functions.allPairs(index).call())  # noqa: E501

    def get_contract(self, address, abi) -> Contract:
        return self.web3_provider.eth.contract(address=address, abi=abi)

    def get_pair_contract(self, index: int) -> Contract:
        pool_address = self.get_pair_address(index)
        pool_abi = json.loads(POOL_ABI)

        return self.get_contract(pool_address, pool_abi)

    def get_pair_contract_data(self, index: int) -> ContractData:
        contract = self.get_pair_contract(index)
        reserves = contract.functions.getReserves().call()
        return ContractData(
            id=contract.address,
            token0=contract.functions.token0().call(),
            token1=contract.functions.token1().call(),
            reserve0=reserves[0],
            reserve1=reserves[1],
        )

    def get_token_contract(self, address) -> Contract:
        return self.get_contract(address, UNISCAP_TOKEN_ABI)

    def get_token(self, address) -> TokenResponse:
        contract = self.get_token_contract(address)
        symbol = contract.functions.symbol().call()
        name = contract.functions.name().call()
        decimals = contract.functions.decimals().call()

        return TokenResponse(
            id=address,
            symbol=symbol,
            name=name,
            decimals=decimals,
        )

    def get_pair(self, index: int) -> PairResponse:
        contract_data = self.get_pair_contract_data(index)
        token0 = self.get_token(contract_data.token0)
        token1 = self.get_token(contract_data.token1)
        token0Price = contract_data.reserve1 / contract_data.reserve0
        token1Price = contract_data.reserve0 / contract_data.reserve1

        return PairResponse(
            id=contract_data.id,
            token0=token0,
            token1=token1,
            token0Price=token0Price,
            token1Price=token1Price,
        )
