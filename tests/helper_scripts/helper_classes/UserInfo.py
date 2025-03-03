from pydantic import BaseModel


class UserInfo(BaseModel):
    email: str
    password: str
    user_id: int = None
