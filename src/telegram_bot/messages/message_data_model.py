from typing import Optional

from aiogram.types import InlineKeyboardMarkup
from pydantic import BaseModel


class MessageDataModel(BaseModel):
    text: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
