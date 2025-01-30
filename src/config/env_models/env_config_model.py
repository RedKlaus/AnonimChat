from pydantic import BaseModel


class EnvConfigModel(BaseModel):
    TELEGRAM_TOKEN: str
    SUBSCRIBE_TELEGRAM_CHANNEL: int
    SUBSCRIBE_TELEGRAM_CHANNEL_LINK: str
    ADMIN_TELEGRAM_ID: int

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int
