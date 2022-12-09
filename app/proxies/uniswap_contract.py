import json
from dataclasses import dataclass

from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract import Contract

from app.constants import POOL_ABI
from app.proxies.base import BaseContractProxy
from app.schemas.uniswap_api import ContractData
from app.settings import UniswapSettings


@dataclass
class UniswapFactoryProxy(BaseContractProxy):
    uniswap_settings: UniswapSettings

    def get_pair_length(self) -> int:
        return self.contract.functions.allPairsLength().call()

    def get_pair_address(self, index: int) -> ChecksumAddress:
        return Web3.toChecksumAddress(self.contract.functions.allPairs(index).call())  # noqa: E501

    def get_pair_contract(self, index: int) -> Contract:
        pool_address = self.get_pair_address(index)
        pool_abi = json.loads(POOL_ABI)

        return self.web3_provider.eth.contract(address=pool_address, abi=pool_abi)

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