from datetime import datetime

from sqlalchemy import DateTime, Column
from sqlalchemy.sql import func


class TimeModel:
    created_at = Column(
        DateTime,
        nullable=False,
        index=True,
        default=datetime.utcnow,
        server_default=func.now(),
    )
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
