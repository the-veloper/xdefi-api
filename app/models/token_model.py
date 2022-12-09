from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from app.models.base_model import Base
from app.models.time_model import TimeModel


class TokenModel(Base, TimeModel):
    __tablename__ = "tokens"

    id = Column(String, primary_key=True)
    name = Column(String)
    symbol = Column(String)
    decimals = Column(Integer)
