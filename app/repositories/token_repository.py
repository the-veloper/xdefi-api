from sqlalchemy import delete, select

from app.models import TokenModel
from app.repositories.base_repository import PostgresRepository
from app.schemas.uniswap_api import TokenResponse


class TokenRepository(PostgresRepository):
    async def get_token(self, token_id: str) -> TokenResponse | None:
        token = self.session.execute(
            select(TokenModel).where(TokenModel.id == token_id)
        )
        token = token.scalar_one_or_none()

        if token:
            return TokenResponse.from_orm(token)

        return None

    def create_token(self, token: TokenResponse) -> None:
        token = TokenModel(**token.dict())
        self.session.add(token)
        self.session.commit()

    def create_or_update_token(self, token: TokenResponse) -> None:
        token = TokenModel(**token.dict())
        self.session.merge(token)
        self.session.commit()

    async def delete_token(self, token: str) -> None:
        self.session.execute(
            delete(TokenModel).where(TokenModel.token == token)
        )
        self.session.flush()
