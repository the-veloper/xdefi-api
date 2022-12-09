import asyncio
import multiprocessing
import threading
from asyncio import gather

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import settings
from app.core.httpx import create_httpx_client
from app.exceptions import UserInterrupt
from app.logger import logger
from app.proxies.uniswap_contract import UniswapFactoryProxy
from app.proxies.uniswap_graphql import UniswapGraphQLProxy
from app.repositories.pair_repository import PairRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.uniswap_api import PairResponse, TokenResponse
from app.settings import UniswapSettings
from app.utils import interval


class UniswapSyncer(threading.Thread):

    def __init__(
        self,
        *args,
        app: FastAPI,
        index: int,
        token_repository: TokenRepository,
        pair_repository: PairRepository,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        httpx_settings: settings.HTTPXSettings = settings.get_httpx()

        self.uniswap_client_pool = create_httpx_client(settings=httpx_settings)  # noqa: E501
        self.uniswap_proxy = UniswapGraphQLProxy(
            httpx_client=self.uniswap_client_pool,
            uniswap_settings=app.state.uniswap_settings
        )
        self.uniswap_factory = UniswapFactoryProxy(
            web3_provider=app.state.web3,
            uniswap_settings=app.state.uniswap_settings,
            contract=app.state.uniswap,
        )
        self.app = app
        self.index = index
        self.cores = multiprocessing.cpu_count()
        self.state = app.state
        self.token_repository = token_repository
        self.pair_repository = pair_repository
        self._stop_event = threading.Event()

    async def handle_pair_data(self, pair_list: list[PairResponse]):
        for pair in pair_list:
            # weight = balance_target * input / (balance_source + input)
            # used to calculate the shortest path
            self.state.token_graph.add_edge(pair.token0.id, pair.token1.id, weight=pair.token0Price)  # noqa E501
            await self.handle_token_data([pair.token0, pair.token1])
            self.pair_repository.create_or_update_pair(pair)
        logger.info(f"Synced {len(pair_list)} pairs")

    async def handle_token_data(self, token_list: list[TokenResponse]):
        for token in token_list:
            self.state.token_graph.add_node(token.id, token=token)  # noqa E501
            print("saving token", token)
            self.token_repository.create_or_update_token(token)
        logger.info(f"Synced {len(token_list)} tokens")

    async def load_all(self, getter, setter):
        skip = 0
        first = 1000
        while True:
            if self._stop_event.is_set():
                break
            try:
                items = await getter(skip=skip, first=first)
            except Exception as e:
                logger.error(f"Error while loading data: {e}")
                break
            if len(items) == 0:
                break
            setter(items)
            logger.info(f"Loaded {first}, processed: {skip}")
            skip += first

    async def load_all_pairs(self):
        """
        Load 5000 most traded pairs from Uniswap
        :return:
        """
        await self.load_all(self.uniswap_proxy.get_pairs, self.handle_pair_data)

    async def load_all_tokens(self):
        """
        Load 5000 tokens from Uniswap
        :return:
        """
        await self.load_all(self.uniswap_proxy.get_tokens, self.handle_token_data)

    async def run_async(self):
        uniswap_settings: UniswapSettings = self.state.uniswap_settings

        task_tokens = asyncio.create_task(self.load_all_tokens())
        task_pairs = asyncio.create_task(self.load_all_pairs())

        while True:
            if self._stop_event.is_set():
                break
            await gather(task_tokens, task_pairs, *self.factory_pair_tasks())
            await asyncio.sleep(uniswap_settings.sync_interval)

        await gather(
            self.uniswap_client_pool.aclose(),
        )

    def factory_pair_tasks(self):
        tasks = []
        my_interval = interval([0, self.uniswap_factory.get_pair_length()], self.cores)[self.index]  # noqa: E501
        logger.info(f"Thread {self.index} will process pairs {my_interval}")
        for pair_index in range(my_interval[0], my_interval[1]):
            tasks.append(asyncio.create_task(self.load_contract_pair(pair_index)))
        return tasks

    async def load_contract_pair(self, pair_index: int):
        if self._stop_event.is_set():
            raise UserInterrupt("Stop event is set")
        logger.info(f"Thread {self.index} loading pair {pair_index}")
        pair_data = self.uniswap_factory.get_pair(pair_index)
        logger.info(f"Thread {self.index} loaded pair {pair_index}")
        await self.handle_pair_data([pair_data])

    async def load_pairs_from_db(self):
        my_interval = interval([0, self.uniswap_factory.get_pair_length()], self.cores)[self.index]  # noqa: E501
        logger.info(f"Thread {self.index} will process pairs {my_interval}")
        pairs = self.pair_repository.get_pairs(my_interval[1] - my_interval[0], my_interval[0])  # noqa: E501
        await self.handle_pair_data(pairs)

    def run(self, *args, **kwargs):
        logger.info("Starting Uniswap syncer")
        logger.info("Loading pairs from DB")
        asyncio.run(self.load_pairs_from_db())
        logger.info("Loading pairs from DB finished")
        try:
            asyncio.run(self.run_async())
        except UserInterrupt:
            logger.critical("User interrupt. Stopping syncer")

    def stop(self):
        self._stop_event.set()


def start_syncer(app: FastAPI, index: int):
    database_settings: settings.DatabaseSettings = settings.get_database_settings()
    engine = create_engine(database_settings.uri_sync)
    Session = sessionmaker(bind=engine)
    with Session.begin() as session:
        token_repository = TokenRepository(session=session)
        pair_repository = PairRepository(session=session)
        syncer = UniswapSyncer(
            app=app,
            index=index,
            token_repository=token_repository,
            pair_repository=pair_repository,
        )
        syncer.start()
    return syncer


def start_threads(app: FastAPI):
    cpu_cores = multiprocessing.cpu_count()

    for index in range(cpu_cores):
        syncer = start_syncer(app, index)
        app.state.syncers.append(syncer)
