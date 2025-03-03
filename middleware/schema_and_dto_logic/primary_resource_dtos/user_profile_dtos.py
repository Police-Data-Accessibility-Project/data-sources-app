from dataclasses import dataclass

from pydantic import BaseModel


class UserPutDTO(BaseModel):
    old_password: str
    new_password: str
