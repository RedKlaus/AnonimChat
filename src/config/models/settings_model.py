from typing import List

from pydantic import BaseModel


class SettingsDatabaseModel(BaseModel):
    log_debug: bool


class SettingsDialogLoopModel(BaseModel):
    sleep_time: int
    max_users: int


class AiogramFSMRedisModel(BaseModel):
    redis_storage_ttl_minutes: int


class ForbiddenMessageModel(BaseModel):
    forbidden_text_list: List[str]
    forbidden_regex_list: List[str]


class SettingsModel(BaseModel):
    database: SettingsDatabaseModel
    dialog_loop: SettingsDialogLoopModel
    aiogram_fms_redis: AiogramFSMRedisModel
    forbidden_message: ForbiddenMessageModel
