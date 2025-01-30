from datetime import timedelta
from typing import List

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis

from src.config import Settings, ConnectDatabaseModel
from src.config.env_config import get_config_data

# Инициализация некоторых объектов для доступа из кода

config = Settings("settings.yaml")
env_config_data = get_config_data()

# combination_database_model нужен для того, что бы поддерживать работу с docker
connect_database_model = ConnectDatabaseModel(
    host=env_config_data.POSTGRES_HOST,
    port=env_config_data.POSTGRES_PORT,
    user=env_config_data.POSTGRES_USER,
    password=env_config_data.POSTGRES_PASSWORD,
    database=env_config_data.POSTGRES_DB,
)

_redis = Redis(host=env_config_data.REDIS_HOST, port=env_config_data.REDIS_PORT)

REDIS_STORAGE_STATE_TTL = timedelta(minutes=config.config_data.aiogram_fms_redis.redis_storage_ttl_minutes)
REDIS_STORAGE_DATA_TTL = REDIS_STORAGE_STATE_TTL

storage = RedisStorage(_redis, state_ttl=REDIS_STORAGE_STATE_TTL, data_ttl=REDIS_STORAGE_DATA_TTL)

FORBIDDEN_TEXTS: List[str] = config.config_data.forbidden_message.forbidden_text_list
FORBIDDEN_RE: List[str] = config.config_data.forbidden_message.forbidden_regex_list
