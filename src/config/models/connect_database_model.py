from pydantic import BaseModel


class ConnectDatabaseModel(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str
