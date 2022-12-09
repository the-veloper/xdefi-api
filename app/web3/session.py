import json

from eth_typing import ChecksumAddress
from web3 import Web3

from app.constants import UNISWAP_FACTORY_ABI


def get_web3_provider(node_url) -> Web3:
    return Web3(Web3.HTTPProvider(node_url))


def uniswap_factory(provider: Web3, factory_address: ChecksumAddress):
    # uniswap_Factory
    abi = json.loads(UNISWAP_FACTORY_ABI)
    factory_contract = provider.eth.contract(address=factory_address, abi=abi)

    return factory_contract
