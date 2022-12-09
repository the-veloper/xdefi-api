from sqlalchemy import ForeignKey
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy.orm import relationship

from app.models.token_model import TokenModel
from app.models.base_model import Base
from app.models.time_model import TimeModel


# test
class PairModel(Base, TimeModel):
    __tablename__ = "pairs"

    id = Column(String, primary_key=True)
    token0_id = Column(ForeignKey(TokenModel.id))
    token0 = relationship(
        "TokenModel",
        uselist=False,
        cascade="all,delete",
        foreign_keys=[token0_id],
    )
    token1_id = Column(ForeignKey(TokenModel.id))
    token1 = relationship(
        "TokenModel",
        uselist=False,
        cascade="all,delete",
        foreign_keys=[token1_id],
    )
    token0Price = Column(Numeric(300, 100))
    token1Price = Column(Numeric(300, 100))
