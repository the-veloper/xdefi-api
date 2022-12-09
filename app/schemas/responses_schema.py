from pydantic import BaseModel, StrictBool


class Healthcheck(BaseModel):
    status: StrictBool


class Degraded(Healthcheck):
    status: StrictBool = False
