from dataclasses import dataclass

from pydantic import BaseModel, Field


class RequestResetPasswordRequestDTO(BaseModel):
    email: str = Field(description="The email of the user.")
    token: str = Field(description="The token of the user.")


class ResetPasswordDTO(BaseModel):
    password: str = Field(description="The new password of the user.")
