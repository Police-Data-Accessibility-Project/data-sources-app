from pydantic import BaseModel

from db.enums import UserCapacityEnum


class UserInfo(BaseModel):
    email: str
    password: str
    capacities: list[UserCapacityEnum] = None
    user_id: int = None
