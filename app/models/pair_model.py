from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy.orm import relationship

from app.models.base_model import Base
from app.models.time_model import TimeModel


# test
class PairModel(Base, TimeModel):
    __tablename__ = "pairs"

    id = Column(String, primary_key=True)
    token0 = relationship(
        "TokenModel",
        uselist=False,
        cascade="all,delete",
        back_populates="pairs",
    )
    token1 = relationship(
        "TokenModel",
        uselist=False,
        cascade="all,delete",
        back_populates="pairs",
    )
    token0Price = Column(Numeric(20, 10))
    token1Price = Column(Numeric(20, 10))
