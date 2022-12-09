import asyncio
import threading
import time

from fastapi import FastAPI

from app.proxies.uniswap import UniswapProxy
from app.schemas.uniswap_api import PairListResponse
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

    def handle_pair_data(self, pair_list: PairListResponse):
        self.state.uniswap_pairs = pair_list

    async def run_async(self, *args, **kwargs):
        while True:
            uniswap_proxy: UniswapProxy = self.state.uniswap_proxy
            uniswap_settings: UniswapSettings = self.state.uniswap_settings

            try:
                pairs = await uniswap_proxy.get_pairs()
                self.handle_pair_data(pairs)
            except Exception as e:
                print(e)

            time.sleep(uniswap_settings.sync_interval)

    def run(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.run_async(args))
        loop.close()
