from sqlalchemy import delete, select

from app.models import PairModel
from app.repositories.base_repository import PostgresRepository
from app.schemas.uniswap_api import PairResponse


class PairRepository(PostgresRepository):
    def get_pair(self, pair_id: str) -> PairResponse | None:
        pair = self.session.execute(
            select(PairModel).where(PairModel.id == pair_id)
        )
        pair = pair.scalar_one_or_none()

        if pair:
            return PairResponse.from_orm(pair)

        return None

    def get_pairs(self, limit: int = 100, offset: int = 0) -> list[PairResponse]:
        pairs = self.session.execute(
            select(PairModel).limit(limit).offset(offset)
        )
        pairs = pairs.scalars().all()

        return [PairResponse.from_orm(pair) for pair in pairs]

    def create_pair(self, pair: PairResponse) -> None:
        pair = PairModel(**pair.dict())
        self.session.add(pair)
        self.session.commit()

    def create_or_update_pair(self, pair: PairResponse) -> None:
        pair = PairModel(**pair.dict(exclude={'token0', 'token1'}), token0_id=pair.token0.id, token1_id=pair.token1.id)  # noqa: E501
        self.session.merge(pair)
        self.session.commit()

    async def delete_pair(self, pair: str) -> None:
        self.session.execute(
            delete(PairModel).where(PairModel.pair == pair)
        )
        self.session.flush()
