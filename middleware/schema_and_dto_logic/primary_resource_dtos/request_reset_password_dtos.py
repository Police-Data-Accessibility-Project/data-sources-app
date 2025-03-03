from dataclasses import dataclass

from pydantic import BaseModel


class RequestResetPasswordRequestDTO(BaseModel):
    email: str
