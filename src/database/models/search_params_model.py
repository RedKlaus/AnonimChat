from typing import List

from pydantic import BaseModel


class SearchParamsModel(BaseModel):
    user_id: int
    interlocutor_age: List[int]
