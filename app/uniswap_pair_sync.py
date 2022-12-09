import asyncio
import threading
import time

from fastapi import FastAPI

from app.schemas.uniswap_api import PairResponse, TokenResponse
from app.settings import UniswapSettings


class UniswapSyncer(threading.Thread):

    def __init__(
            self,
            *args,
            app: FastAPI,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.app = app
        self.state = app.state
        self._stop_event = threading.Event()

    def handle_pair_data(self, pair_list: list[PairResponse]):
        self.state.token_graph.add_edges_from(
            [
                (pair.token0.id, pair.token1.id) for pair in pair_list
            ]
        )
        print(f"Synced {len(pair_list)} pairs")

    def handle_token_data(self, token_list: list[TokenResponse]):
        self.state.token_graph.add_nodes_from([token.id for token in token_list])  # noqa E501
        print(f"Synced {len(token_list)} tokens")

    async def load_all(self, getter, setter):
        skip = 0
        first = 1000
        while True:
            try:
                print(f"Loaded {first}, processed: {skip}")
                items = await getter(skip=skip, first=first)
            except Exception as e:
                print(e)
                break
            if len(items) == 0:
                break
            setter(items)
            skip += first

    async def load_all_pairs(self):
        await self.load_all(self.state.uniswap_proxy.get_pairs, self.handle_pair_data)

    async def load_all_tokens(self):
        await self.load_all(self.state.uniswap_proxy.get_tokens, self.handle_token_data)

    async def run_async(self):
        uniswap_settings: UniswapSettings = self.state.uniswap_settings
        while self._stop_event.is_set() is False:
            await self.load_all_pairs()
            await self.load_all_tokens()
            time.sleep(uniswap_settings.sync_interval)

    def run(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.run_async())
        loop.close()

    def stop(self):
        self._stop_event.set()
