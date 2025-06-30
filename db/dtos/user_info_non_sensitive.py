from datetime import datetime

from pydantic import BaseModel


class UserInfoNonSensitive(BaseModel):
    user_id: int
    email: str
    created_at: datetime
    updated_at: datetime
