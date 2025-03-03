from dataclasses import dataclass

from pydantic import BaseModel


class RequestResetPasswordRequestDTO(BaseModel):
    email: str
    token: str


class ResetPasswordDTO(BaseModel):
    password: str
