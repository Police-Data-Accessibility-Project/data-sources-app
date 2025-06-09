from pydantic import BaseModel, Field


class RequestResetPasswordRequestDTO(BaseModel):
    email: str = Field(description="The email address associated with the account.")
