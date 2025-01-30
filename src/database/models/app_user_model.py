from typing import Optional

from pydantic import BaseModel


class AppUserModel(BaseModel):
    id: int
    telegram_id: Optional[int] = None
    age: Optional[int] = None
