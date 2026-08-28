from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str


class DbHealthStatus(BaseModel):
    status: str
    database: str
