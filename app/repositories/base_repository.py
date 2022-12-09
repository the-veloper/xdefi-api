from dataclasses import dataclass

from sqlalchemy.orm import Session


@dataclass
class PostgresRepository:
    session: Session
