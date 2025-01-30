from os import getenv

from src.config.env_models import EnvConfigModel


def get_config_data() -> EnvConfigModel:
    return EnvConfigModel(
        TELEGRAM_TOKEN=getenv("TELEGRAM_TOKEN"),
        SUBSCRIBE_TELEGRAM_CHANNEL=int(getenv("SUBSCRIBE_TELEGRAM_CHANNEL")),
        SUBSCRIBE_TELEGRAM_CHANNEL_LINK=getenv("SUBSCRIBE_TELEGRAM_CHANNEL_LINK"),
        ADMIN_TELEGRAM_ID=int(getenv("ADMIN_TELEGRAM_ID")),
        POSTGRES_HOST=getenv("POSTGRES_HOST"),
        POSTGRES_PORT=int(getenv("POSTGRES_PORT")),
        POSTGRES_USER=getenv("POSTGRES_USER"),
        POSTGRES_PASSWORD=getenv("POSTGRES_PASSWORD"),
        POSTGRES_DB=getenv("POSTGRES_DB"),
        REDIS_HOST=getenv("REDIS_HOST"),
        REDIS_PORT=int(getenv("REDIS_PORT")),
    )
